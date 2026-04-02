import importlib
from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction, models, IntegrityError
from django.db.models import Sum
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils.timezone import now, localdate
# Needed later:
from cashier import models as dynamic_models

from cashier.models import AccountBalance, AccountBalanceLedgerTX, \
    AccountDepositBonus, AccountBonusStateTracker, AccountBonusStateHistory, \
    VDomainPaymentProviders, AccountLevelActivationBonus, CashierVDomainParameters, \
    CryptoCurrency, AccountPromoCodeBonus, GenericInternalBonus

from licensemanager.models import VHostLicencedApplications

from minerve.toolkit.errors import generic_json_error

from logging import getLogger

from notifications.models import AccountNotifications, ManagerNotifications



class Cashier(object):
    account = False

    logger = None
    debug = False
    vhost = False
    def __init__(self,vhost,account,**kwargs):
        self.vhost = vhost
        self.account = account
        self.logger = getLogger(f"cashier.engine.acct[{self.account.uuid}]")
        # self.logger.info(f"Starting up for VHost: {self.vhost} and Account {self.account.uuid}")


    def _get_domain_parameters(self):
        if self.account.domain:
            with_vdomain = CashierVDomainParameters.objects.filter(vhost=self.account.vhost,vdomain__in=[self.account.vdomain])
            if (len(with_vdomain) > 0):
                return with_vdomain[0]
            else:
                params = CashierVDomainParameters.objects.filter(vhost=self.account.vhost)[0]
                return params
        else:
            params = CashierVDomainParameters.objects.filter(vhost=self.account.vhost)[0]
            return params


    def get_exchange_rate_usd(self,crypto_curr_symbol):
        ccObj = CryptoCurrency.objects.get(vhost=self.vhost,symbol=crypto_curr_symbol)
        return ccObj.current_usd_exr

    def get_exchange_rate_btc(self,crypto_curr_symbol):
        ccObj = CryptoCurrency.objects.get(vhost=self.vhost,symbol=crypto_curr_symbol)
        return ccObj.current_btc_exr

    def get_exchange_rate(self):
        """
        Get exchange rate for crypto withdrawals.
        For ionBlock/crypto providers, return 1 since we're dealing in USD/tokens directly
        """
        return 1

    def get_balance_obj(self):
        try:
            abo,c = AccountBalance.objects.get_or_create(account=self.account,vhost=self.vhost)
            if c: abo.save()
        except IntegrityError:
            abo = AccountBalance.objects.filter(account=self.account, vhost=self.vhost).first()

        return abo



    @transaction.atomic
    def _bonus_rollover_complete(self,btickt,playerBal):
        if btickt.rollover_completed >= btickt.rollover_amount:
            btickt.rollover_complete = True
            playerBal.pending_rollovers -= btickt.rollover_amount
            if playerBal.pending_rollovers < 0: playerBal.pending_rollovers = 0
            bhist = AccountBonusStateHistory.objects.get(parent=btickt)
            bhist.active = False
            bhist.finished_at = now()
            bhist.parent = None
            bhist.save()
            btickt.delete()
            from cashier.signals import signal_bonus_rollover_met
            signal_bonus_rollover_met.send(sender=self,account=btickt.account,bhist=bhist)


    def _get_bonus_obj(self,class_name,uuid):
        obj = getattr(dynamic_models,class_name)
        try:
            return obj.objects.get(uuid=uuid)
        except obj.DoesNotExist:
            return False

    @transaction.atomic
    def _bonus_payout(self,bonusObj,bonusTrackObj,**kwargs):
        bonus_dep = 0
        rollover_amnt = 0
        if bonusObj.__class__.__name__ == "AccountInitialDepositBonus":
            # Deposit bonus amount calc: For AccountInitialDepositBonus, we treat reward_deposit as a "maximum" threshold value.
            bonus_dep = bonusTrackObj.current_deposit * bonusObj.deposit_multiplier
            if (bonus_dep >= bonusObj.max_reward_amount) >= bonusObj.reward_deposit:
                bonus_dep = bonusObj.max_reward_amount

            rollover_amnt = (bonusTrackObj.current_deposit+bonus_dep) * bonusObj.rollover
        if bonusObj.__class__.__name__ == "AccountDepositBonus":
            # Deposit bonus amount calc:
            if "curr_deposit_amount" in kwargs:
                bonus_dep_amn = kwargs["curr_deposit_amount"]
            else:
                bonus_dep_amn = bonusTrackObj.current_deposit
            if bonusTrackObj.current_deposit == 0:
                bonus_dep = bonus_dep_amn * bonusObj.deposit_multiplier + bonusObj.reward_deposit

            elif bonusTrackObj.current_deposit == 1:
                bonus_dep = bonusTrackObj.current_deposit * bonusObj.second_deposit_multiplier
            elif bonusTrackObj.current_deposit == 2:
                bonus_dep = bonusTrackObj.current_deposit * bonusObj.third_deposit_multiplier
            rollover_amnt = (bonusObj.reward_deposit+bonus_dep) * bonusObj.rollover
        elif bonusObj.__class__.__name__ == "AccountPromoCodeBonus":
            # Deposit bonus amount calc:
            bonus_dep = bonusObj.reward_deposit
            rollover_amnt = bonus_dep * bonusObj.rollover
        elif bonusObj.__class__.__name__ == "AccountLevelActivationBonus":
            # Level Activation Bonus amount calc:
            bonus_dep = bonusObj.reward_deposit
            rollover_amnt = bonus_dep * bonusObj.rollover
        elif bonusObj.__class__.__name__ == "GenericInternalBonus":
            bonus_dep = bonusObj.reward_deposit
            rollover_amnt = bonus_dep * bonusObj.rollover
        bonus_dep = min(bonus_dep,bonusObj.max_reward_amount)
        balance  = self.get_balance_obj()
        ledgerTX = AccountBalanceLedgerTX(parent=balance, type="BONUS_DEPOSIT", fees_change=0,
                                          avail_change=0, bonus_change=bonus_dep, vhost=self.vhost, deposit_change=bonus_dep)
        ledgerTX.save()

        notData = {
            "tuuid": str(ledgerTX.uuid)
        }
        accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type="BONUS", data=notData,
                                             title="Bonus", text=f"Your bonus of ${bonus_dep} has been credited.")
        accountNotObj.save()

        balance.bonus += bonus_dep
        # NOTE: Bonus is NOT added to available balance - users must explicitly choose to use bonus
        balance.pending_rollovers += rollover_amnt
        # self.logger.info(f'Bonus payout {bonusObj.__class__.__name__} UUID {bonusObj.uuid}')
        bonusTrackerObj,cc = AccountBonusStateTracker.objects.get_or_create(account=self.account, bonus_obj_type=bonusObj.__class__.__name__,
                                                            bonus_obj_uuid=bonusObj.uuid,active=True,vhost=self.vhost)
        if cc:
            bonusTrackerObj.save()
        # Set the bonus object's active state itself to False, in addition to the TrackerObj active state, as this is used by Cashier Landing front-end
        if bonusTrackerObj.bonus_obj_type == "AccountInitialDepositBonus":
            bonusTrackerObj.active = False
            #bonusTrackerObj.save()
            bonusObj.active = False
            bonusObj.save(update_fields=["active"])
        elif bonusTrackObj.bonus_obj_type == "AccountDepositBonus":
            if bonusTrackObj.deposit_count >= bonusObj.max_deposit_count:
                bonusTrackerObj.active = False
                # bonusTrackerObj.save()
                bonusObj.active = False
                bonusObj.save()
            else:
                bonusTrackerObj.deposit_count += 1

        # self.logger.info(f"Bonus Deposit! {bonus_dep} / {btickt.current_deposit}  / {rollover_amnt}")
        # houseBal = HouseBalance.objects.get_or_create(vhost=self.account.vhost,application_id__isnull=True)[0]


        balance.save()
        bonusTrackerObj.reward_deposit = bonus_dep
        histObj,cc = AccountBonusStateHistory.objects.get_or_create(parent=bonusTrackerObj)
        if cc:
            histObj.save()
        histObj.current_deposit += bonusTrackerObj.current_deposit
        bonusTrackerObj.rollover += bonus_dep
        # hist.parent = None
        # hist.active = False
        # hist.finished_at = now()
        bonusTrackerObj.rollover_amount = rollover_amnt
        # btickt.reward_deposit = bonus_dep
        # btickt.save()
        bonusTrackerObj.save()

    @transaction.atomic
    def get_withdrawable_balance(self):
        bal = self.get_balance_obj()
        if bal.pending_rollovers > 0:
            return 0
        return bal.available

    @transaction.atomic
    def get_bonus_points_balance(self):
        return self.get_balance_obj().bonus_points


    def get_pending_withdrawals(self):
        return self.get_balance_obj().pending_withdraw

    @transaction.atomic
    def get_pending_rollovers(self):
        return self.get_balance_obj().pending_rollovers

    def get_at_risk_balance(self):
        bo = self.get_balance_obj()
        return bo.at_risk

    def get_balance(self):
        bo = self.get_balance_obj()
        balt = bo.available
        return balt

    def get_available_balance(self,use_bonus=False):
        bo = self.get_balance_obj()
        if not use_bonus:
            balt = bo.available
            balt -= bo.at_risk
            balt -= bo.pending_withdraw
        else:
            balt = bo.bonus
        return balt

    def confirm_withdrawable_balance(self,pending_balance):
        bo = self.get_balance_obj()
        balt = bo.available
        balt -= bo.at_risk
        balt -= bo.pending_withdraw
        balt += pending_balance
        if balt >0:
            return True
        else:
            return False


    @transaction.atomic
    def get_available_bonus(self):
        return self.get_balance_obj().bonus

    def get_bonus_balance(self):
        """Get available bonus balance (alias for get_available_bonus)"""
        return self.get_balance_obj().bonus

    @transaction.atomic
    def use_bonus_for_wager(self, wagerObj, amount, **kwargs):
        """
        Deduct from bonus balance when user explicitly chooses to use bonus for a wager.

        Args:
            wagerObj: The wager object
            amount: Amount to deduct from bonus

        Returns:
            tuple: (success, ledgerTX)
        """
        bal = self.get_balance_obj()

        if bal.bonus < amount:
            raise ValidationError(f"Insufficient bonus balance! Available: ${bal.bonus:.2f}.")

        # By default, Relationship data should include relations to the TX, ie, wagers:
        if "relations" in kwargs:
            rdata = kwargs["relations"]
        else:
            rdata = {}

        ledgerTX = AccountBalanceLedgerTX(
            parent=bal,
            type="BONUS_USED",
            fees_change=0,
            avail_change=0,
            bonus_change=-amount,
            at_risk_change=amount,
            domain=wagerObj.account.domain,
            reference_data=rdata,
            subtype="Wager",
            vhost=self.vhost,
            application=wagerObj.application_type
        )
        ledgerTX.save()

        bal.bonus -= Decimal(amount)
        bal.at_risk += Decimal(amount)
        bal.save()

        return True, ledgerTX

    @transaction.atomic
    def credit_bonus(self, amount, bonus_type="BONUS", rollover=1, expiry_days=14, **kwargs):
        """
        Credit bonus to account (for RAF rewards, promotions, etc.)

        Args:
            amount: Bonus amount to credit
            bonus_type: Type of bonus (e.g., "RAF_REWARD", "PROMO")
            rollover: Rollover multiplier for withdrawability
            expiry_days: Days until bonus expires

        Returns:
            tuple: (success, ledgerTX)
        """
        balance = self.get_balance_obj()
        rollover_amnt = Decimal(amount) * Decimal(rollover)

        ledgerTX = AccountBalanceLedgerTX(
            parent=balance,
            type=bonus_type,
            fees_change=0,
            avail_change=0,
            bonus_change=amount,
            vhost=self.vhost
        )
        ledgerTX.save()

        balance.bonus += Decimal(amount)
        balance.pending_rollovers += rollover_amnt
        balance.save()

        # Create notification
        notData = {"tuuid": str(ledgerTX.uuid)}
        accountNotObj = AccountNotifications(
            vhost=self.vhost,
            account=self.account,
            type="BONUS",
            data=notData,
            title="Bonus Credited",
            text=f"Your bonus of ${amount} has been credited."
        )
        accountNotObj.save()

        self.logger.info(f"Credited bonus {amount} to account {self.account.uuid}, rollover: {rollover_amnt}")

        return True, ledgerTX

    def get_max_deposit(self):
        return min(self.account.account_level.daily_deposit_lim_cryp,self.account.account_level.weekly_deposit_lim_cryp,self.account.account_level.monthly_deposit_lim_cryp,self.account.account_level.yearly_deposit_lim_cryp)



    @transaction.atomic
    def create_withdrawal_ticket(self,vdomain,provider,crypto,_amount,**kwargs):
        # Does account have Withdrawal allowed?
        balance =self.get_balance_obj()
        if "xchng" not in kwargs:
            cco = CryptoCurrency.objects.get(symbol=crypto)
            xchg = cco.current_usd_exr
        else:
            xchg = kwargs.get("xchng")

        # self.logger.info(f"{_amount:.2f}|{xchg}")
        # For ionBlock/hotwallet, keep Decimal precision for crypto amounts
        # Otherwise round to integer for traditional providers
        # if provider in ["cashier.providers.ionBlock", "cashier.providers.hotwallet"]:
        #     amount = Decimal(str(_amount)) / Decimal(str(xchg))
        #     # For ionBlock/hotwallet, limits are in USD, so check against original amount
        #     limit_check_amount = Decimal(str(_amount))
        # elif provider in ["cashier.providers.sepa"]:
        #     amount = Decimal(str(_amount))
        # else:
        amount = (_amount / xchg)
        print("_amount:", amount,"xchng:", xchg,"total_amount",amount)
        self.logger.info(f"{amount:.2f} from {_amount:.2f} / {xchg:.2f}")

        if self.account.account_level.max_withdrawal_cryp <= 0:
            raise ValidationError(
                {"level": "Account's current level does not permit Crypto Withdrawals of this amount."})

        # Disabled while we do something better than counters.
        # if limit_check_amount + counters.daily_total_cryp > self.account.account_level.daily_withdrawal_lim_cryp:
        #     raise ValidationError(
        #         {"daily_limit": "Account's daily withdrawal limit would be exceeded by this transaction."})
        #
        # if limit_check_amount + counters.weekly_total_cryp > self.account.account_level.weekly_withdrawal_lim_cryp:
        #     raise ValidationError(
        #         {"weekly_limit": "Account's weekly withdrawal limit would be exceeded by this transaction."})
        #
        # if limit_check_amount + counters.monthly_total_cryp > self.account.account_level.monthly_withdrawal_lim_cryp:
        #     raise ValidationError(
        #         {"monthly_limit": "Account's monthly withdrawal limit would be exceeded by this transaction."})
        #
        # if limit_check_amount + counters.yearly_total_cryp > self.account.account_level.yearly_withdrawal_lim_cryp:
        #     raise ValidationError(
        #         {"yearly_limit": "Account's yearly withdrawal limit would be exceeded by this transaction."})

        # if limit_check_amount > self.account.account_level.max_withdrawal_cryp:
        #     raise ValidationError({"max_withdrawal": "Withdrawal amount exceeds maximum crypto withdrawal limit."})

        fees = Decimal(self.account.account_level.withl_fee_pct_cryp / 100) * amount
        effective_withdrawal = Decimal(amount - fees)
        # Now compute processor fees:
        # self.logger.info(effective_deposit)
        try:
            chosen_provider = self.get_available_withdrawal_providers(vdomain).get(
                payment_provider__module_name=provider).payment_provider

        except VDomainPaymentProviders.DoesNotExist:
            raise ValidationError({f"Provider {provider} does not exist."})
        proc_fees = Decimal(chosen_provider.wdl_fees / 100) * amount
        effective_withdrawal -= proc_fees
        modname = f"{provider}.withdrawals"
        deposit_module = importlib.import_module(modname)
        dmObj = deposit_module.WithdrawalProvider()
        try:
            # self.logger.info(amount)
            # Pass additional kwargs (address, network, etc.) to provider
            results = dmObj.create_withdrawal(vdomain, self.account, amount, fees, xchg=xchg, **kwargs)
            success = results[0]
            further_val = results[1]
            # self.logger.info(success,further_val)
        except Exception as e:
            # self.logger.info(e)
            return generic_json_error("Withdrawal ticket failed", str(e))
        if success is True:
            if not further_val:
                # No further validation is required:

                return self._withdraw_from_account(Decimal(amount), chosen_provider, f"WITHDRAWAL",modname)
            else:
                # TODO: FURTHER VALIDATION IS REQUIRED
                return generic_json_error("Just a stub", "Stubby mc stub stub")
        elif success == 0:
            # Transaction is not yet successful, pending!!!
            balance.pending_withdraw += amount
            ledgerTX = AccountBalanceLedgerTX(parent=balance, type=f"PENDING_WDL",subtype=chosen_provider.module_name,
                                              fees_change=fees,vhost=self.vhost,xchg_rate=xchg,
                                              avail_change=effective_withdrawal, pending_withdraw_change=amount,
                                              processor_txid=further_val,processor_provider=chosen_provider)
            ledgerTX.save()
            balance.save()
            # houseBal = HouseBalance.objects.get_or_create(vhost=self.account.vhost,application_id__isnull=True)[0]

            # Create notification to denote pending Withdraw request to the account.
            notData = {
                "tuuid": str(ledgerTX.uuid)
            }
            if provider == "cashier.providers.ionBlock":
                msg_str = f"Your withdraw request for {amount} ETH has been initiated."
            else:
                msg_str = f"Your withdraw request for €{amount} EUR has been initiated."

            accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type="WITHDRAW_PENDING", data=notData,
                                                 title="Withdraw Pending", text=msg_str)
            accountNotObj.save()

            return 0, further_val
        elif success == -1:
            balance.pending_withdraw += amount
            ledgerTX = AccountBalanceLedgerTX(parent=balance,
                                              type=f"EXTERNAL_PENDING_WDL",subtype=chosen_provider.module_name,
                                              fees_change=fees,vhost=self.vhost,xchg_rate=xchg,
                                              avail_change=effective_withdrawal, pending_withdraw_change=amount,
                                              processor_txid=further_val,processor_provider=chosen_provider)
            ledgerTX.save()
            balance.save()

            # Create notification to denote pending Withdraw request to the account.
            notData = {
                "tuuid": str(ledgerTX.uuid)
            }

            if provider == "cashier.providers.ionBlock":
                msg_str = f"Your withdraw request for {amount} ETH has been initiated."
            else:
                msg_str = f"Your withdraw request for €{amount} EUR has been initiated."

            accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type="WITHDRAW_PENDING",
                                                 data=notData,
                                                 title="Withdraw Pending",
                                                 text=msg_str)
            accountNotObj.save()

            return -1, further_val, results[2]

    @transaction.atomic
    def create_deposit_ticket(self,vdomain,provider,amount,**kwargs):
        # Does account have deposit allowed?
        balance = self.get_balance_obj()

        if self.account.account_level.max_deposit_cryp <= 0:
            raise ValidationError(
                {"level": "Account's current level does not permit Crypto Deposits of this amount."})

        # Disabled for now while we figure out how to do something smarter than counter tables.
        # if amount + counters.dep_daily_total_cryp > self.account.account_level.daily_deposit_lim_cryp:
        #     raise ValidationError(
        #         {"daily_limit": "Account's daily deposit limit would be exceeded by this transaction."})
        #
        # # if amount + counters.dep_weekly_total_cryp > self.account.account_level.weekly_deposit_lim_cryp:
        # #     raise ValidationError(
        # #         {"weekly_limit": "Account's weekly deposit limit would be exceeded by this transaction."})
        #
        # if amount + counters.dep_monthly_total_cryp > self.account.account_level.monthly_deposit_lim_cryp:
        #     raise ValidationError(
        #         {"monthly_limit": "Account's monthly deposit limit would be exceeded by this transaction."})
        #
        # if amount + counters.dep_yearly_total_cryp > self.account.account_level.yearly_deposit_lim_cryp:
        #     raise ValidationError(
        #         {"yearly_limit": "Account's yearly deposit limit would be exceeded by this transaction."})

        if amount > self.account.account_level.max_deposit_cryp:
            raise ValidationError({"max_deposit": "Deposit amount exceeds maximum crypto deposit limit."})
        fees = Decimal(self.account.account_level.deposit_fee_pct_cryp / 100) * amount
        effective_deposit = Decimal(amount - fees)
        # Now compute processor fees:
        # self.logger.info(effective_deposit)
        try:
            chosen_provider = self.get_available_deposit_providers(vdomain).get(payment_provider__module_name=provider).payment_provider
        except VDomainPaymentProviders.DoesNotExist:
            raise ValidationError({f"Provider {provider} does not exist."})
        proc_fees = Decimal(chosen_provider.dep_fees/100) * amount

        effective_deposit -= proc_fees
        # Good, now create the deposit ticket with the chosen provider:
        modname = f"{provider}.deposit"
        deposit_module = importlib.import_module(modname)
        dmObj = deposit_module.DepositProvider()
        try:
            results = dmObj.create_deposit(vdomain,self.account,amount,fees,**kwargs)
            success = results[0]
            further_val = results[1]
            # self.logger.info(success,further_val)
        except Exception as e:
            self.logger.info(f"Deposit Ticket Failed: {e}")
            return generic_json_error("Deposit ticket failed", str(e))
        if success is True:
            if not further_val:
                # No further validation is required:

                return self._deposit_to_account(Decimal(amount),chosen_provider,f"DEPOSIT", modname=modname)
            else:
                # TODO: FURTHER VALIDATION IS REQUIRED
                return generic_json_error("Just a stub","Stubby mc stub stub")
        elif success == 0:
            # Transaction is not yet successful, pending!!!
            balance.pending_deposits += amount
            ledgerTX = AccountBalanceLedgerTX(parent=balance, type=f"PENDING_DEP: {chosen_provider.module_name}", fees_change=fees,
                                              avail_change=effective_deposit, pending_deposit_change=amount,vhost=self.vhost,
                                              processor_txid=further_val)
            ledgerTX.save()
            # houseBal = HouseBalance.objects.get_or_create(vhost=self.account.vhost,application_id__isnull=True)[0]

            # Create notification to represent pending deposit request to account.
            notData = {
                "tuuid": str(ledgerTX.uuid)
            }
            accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type="DEPOSIT_PENDING", data=notData,
                                                 title="Deposit Pending", text=f"Your deposit request of ${amount} is Pending.")
            accountNotObj.save()

            return 0,further_val
        elif success == -1:
            balance.pending_deposits += amount
            ledgerTX = AccountBalanceLedgerTX(parent=balance, type=f"EXTERNAL_PENDING_DEP: {chosen_provider.module_name}",
                                              fees_change=fees,vhost=self.vhost,
                                              avail_change=effective_deposit, pending_deposit_change=amount,
                                              processor_txid=further_val)
            ledgerTX.save()
            # houseBal = HouseBalance.objects.get_or_create(vhost=self.account.vhost,application_id__isnull=True)[0]

            # Create notification to represent pending deposit request to account.
            notData = {
                "tuuid": str(ledgerTX.uuid)
            }
            accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type="DEPOSIT_PENDING",
                                                 data=notData,
                                                 title="Deposit Pending", text=f"Your deposit request of ${amount} is Pending.")
            accountNotObj.save()

            return -1, further_val, results[2]

        elif success == -2:
            balance.pending_deposits += amount
            ledgerTX = AccountBalanceLedgerTX(parent=balance, type=f"INTERNAL_PENDING_DEP: {chosen_provider.module_name}",
                                              fees_change=fees,
                                              avail_change=effective_deposit, pending_deposit_change=amount,
                                              processor_txid=further_val["uuid"])
            ledgerTX.save()

            # Create notification to represent pending deposit request to account.
            notData = {
                "tuuid": str(ledgerTX.uuid)
            }
            accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type="DEPOSIT_PENDING",
                                                 data=notData,
                                                 title="Deposit Pending", text=f"Your deposit request of ${amount} is Pending.")
            accountNotObj.save()

            return -2, further_val, results[2]

    @transaction.atomic
    def confirm_pending_deposit(self,processor_tx,final_amount=False):
        balance = self.get_balance_obj()
        if not final_amount:
            final_amount = processor_tx.amount
        # houseBal = HouseBalance.objects.get_or_create(vhost=self.account.vhost,application_id__isnull=True)[0]
        ledgerTX = AccountBalanceLedgerTX.objects.get(processor_txid=processor_tx.uuid)

        # self.logger.info(ledgerTX.pending_deposit_change,houseTX.pending_deposit_change)
        # if final_amount > ledgerTX.pending_deposit_change:
        #     return JsonResponse({"invalid_op":"You cannot deposit more than the outstanding balance."})
        if processor_tx.deposited_at:
            return JsonResponse({"invalid_op":"You cannot execute the same deposit twice."})
        balance.pending_deposits -= ledgerTX.pending_deposit_change
        balance.save()
        self._deposit_to_account(final_amount,processor_tx.provider,"DEPOSIT",skip_fees=True)
        processor_tx.deposited_at = now()
        processor_tx.completed = True
        processor_tx.save()

        # Emit signal for RAF and other deposit-triggered events
        from cashier.signals import signal_deposit_confirmed
        signal_deposit_confirmed.send(
            sender=self,
            account=self.account,
            deposit_amount=final_amount,
            processor_tx=processor_tx
        )

        return JsonResponse({"success": True,"res":"ok","deposited":final_amount,"account":str(processor_tx.account.uuid)})


    @transaction.atomic
    def confirm_pending_withdrawal(self,processor_tx,final_amount=False):
        balance = self.get_balance_obj()
        tolerance = 0.00001
        if not final_amount:
            final_amount = processor_tx.amount
        print("Confirm wd UUID: ", processor_tx.uuid)
        ledgerTX = AccountBalanceLedgerTX.objects.get(processor_txid=processor_tx.uuid)
        print("final: ", final_amount, "pending_wd_change: ", ledgerTX.pending_withdraw_change)
        if abs(final_amount - ledgerTX.pending_withdraw_change) > tolerance:
            print("Test Error 1")
            #final_amount = ledgerTX.pending_withdraw_change # There is a small rounding error when accounting for Crypto TX via Network
            return JsonResponse({"invalid_op":"You cannot withdraw more than the outstanding balance."})
        if processor_tx.deposited_at:
            print("Test Error 2")
            return JsonResponse({"invalid_op":"You cannot execute the same withdrawal twice."})

        balance.pending_withdraw -= ledgerTX.pending_withdraw_change
        print(balance.pending_withdraw)
        balance.save()
        crypto = CryptoCurrency.objects.get(symbol="ETH")
        self._withdraw_from_account(final_amount, ledgerTX.processor_provider, f"WITHDRAWAL",ledgerTX.processor_provider.module_name,xchg=crypto.current_usd_exr,skip_pending_adjust=True)
        processor_tx.deposited_at = now()
        processor_tx.completed = True
        processor_tx.save()
        return JsonResponse({"success": True,"res":"ok","withdrawn":final_amount,"account":str(processor_tx.account.uuid)})


    @transaction.atomic
    def _deposit_to_account(self, amount, provider, type="DEPOSIT", **kwargs):
        ''' Don't call directly!!! Should be called AFTER a transaction is pending and transacted. Call create_deposit_ticket to actually do this.'''
        # Does account have deposit allowed?
        balance = self.get_balance_obj()
        if self.account.account_level.max_deposit_cryp <= 0:
            raise ValidationError({"level":"Account's current level does not permit Crypto Deposits of this amount."})

        # Disabled while we move away from counters:
        # if amount + counters.daily_total_cryp > self.account.account_level.daily_deposit_lim_cryp:
        #     raise ValidationError({"daily_limit":"Account's daily deposit limit would be exceeded by this transaction."})
        #
        # if amount + counters.weekly_total_cryp > self.account.account_level.weekly_deposit_lim_cryp:
        #     raise ValidationError({"weekly_limit":"Account's weekly deposit limit would be exceeded by this transaction."})
        #
        # if amount + counters.monthly_total_cryp > self.account.account_level.monthly_deposit_lim_cryp:
        #     raise ValidationError({"monthly_limit":"Account's monthly deposit limit would be exceeded by this transaction."})
        #
        # if amount + counters.yearly_total_cryp > self.account.account_level.yearly_deposit_lim_cryp:
        #     raise ValidationError({"yearly_limit":"Account's yearly deposit limit would be exceeded by this transaction."})

        if amount > self.account.account_level.max_deposit_cryp:
            raise ValidationError({"max_deposit":"Deposit amount exceeds maximum crypto deposit limit."})

        # self.logger.info(fees)
        if "skip_fees" not in kwargs:
            withdrawable_fees = Decimal(self.account.account_level.deposit_fee_pct_cryp/100) * amount
            provider_fees = Decimal(provider.dep_fees/100) * amount
            fees = (Decimal(self.account.account_level.deposit_fee_pct_cryp / 100) + Decimal(
                provider.dep_fees / 100))
            fees = fees * amount

        else:
            withdrawable_fees = 0
            fees = 0
            provider_fees = 0
        final_deposit = (amount - fees)
        parameters = self._get_domain_parameters()
        effective_deposit = final_deposit*parameters.xchng_rate
        effective_fees = fees * parameters.xchng_rate
        total_amount = amount*parameters.xchng_rate
        self.logger.info(f"Fees: {fees}, Eff Dep: {effective_deposit} Eff fee: {effective_fees}, TA: {total_amount}, FD: {final_deposit}, fees: {fees}")
        ledgerTX = AccountBalanceLedgerTX(parent=balance,type=type,fees_change=effective_fees,avail_change=effective_deposit,deposit_change=amount*fees,withdrawable_change=effective_deposit,xchg_rate=parameters.xchng_rate,vhost=self.vhost)
        if "modname" in kwargs:
            ledgerTX.subtype = kwargs["modname"]
        ledgerTX.save()

        # Create notification to represent confirmed deposit to account.
        notData = {
            "tuuid": str(ledgerTX.uuid)
        }
        accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type=type, data=notData,
                                             title="Deposit", text=f"Your deposit of ${amount} has been confirmed.")
        accountNotObj.save()

        balance.deposits += total_amount
        balance.available += Decimal(effective_deposit)
        balance.fees += Decimal(fees*parameters.xchng_rate)
        balance.save()

        # First, we create bonus trackers for new bonuses:
        # DEPOSIT BONUSES:
        bonusObjs = AccountDepositBonus.objects.filter(level=self.account.account_level,active=True,vhost=self.vhost)
        if len(bonusObjs) > 0:
            self._create_bonus_objects(AccountDepositBonus)

        # # Initial Deposit bonus is created once per premium account and can only be used for one maximum deposit. Should be active=False once credited.
        # initBonusObj = AccountInitialDepositBonus.objects.filter(level=self.account.account_level,active=True,is_user_claimed=True,vhost=self.vhost)
        # if len(initBonusObj) > 0:
        #     self._create_bonus_objects(AccountInitialDepositBonus)

            # self.logger.info(f"Created Deposit Bonus State  and history Tracker for {self.account} and bonus {bonus.uuid}")
        # Once the tickets are created; process them:
        bonus_type_filters = ['AccountDepositBonus']
        i = 0
        bonusObjs = AccountBonusStateTracker.objects.filter(account=self.account,bonus_obj_type__in=bonus_type_filters,active=True,expires_at__gte=now(),vhost=self.vhost)
        for bsttkt in bonusObjs:
            i += 1
            # self.logger.info(f"Checking Bonus {btickt}/{i}...")
            bsttkt.current_deposit += Decimal(effective_deposit)
            hist = AccountBonusStateHistory.objects.get(parent=bsttkt)
            hist.current_deposit += Decimal(effective_deposit)
            # If our deposit is larger than the triggering deposit, trigger the deposit rollover bonus and then delete root ticket, keep history:
            # self.logger.info(f"Current BTicket status, {btickt.uuid}/{btickt.current_deposit}//")
            hist.save()
            bsttkt.save()
            # PAYOUT Deposit Bonuses that have crossed their threshold!
            if hist.current_deposit >= hist.min_deposit:

                bonusObj = self._get_bonus_obj(bsttkt.bonus_obj_type,bsttkt.bonus_obj_uuid)
                if bonusObj:
                    self._bonus_payout(bonusObj,bsttkt,curr_deposit_amount=effective_deposit)
        from cashier.signals import signal_balance_deposit
        signal_balance_deposit.send(sender=self,account=self.account,amount=amount,type="CRYPTO")
        return True, ledgerTX

    @transaction.atomic
    def risk_balance(self,wagerObj,**kwargs):
        # Allow optional amount override (for split bonus/available usage)
        risk_amount = kwargs.get('amount', wagerObj.risk)

        # Is wager even possible?
        bal = self.get_available_balance()
        if bal < risk_amount:
            raise ValidationError(f"You don't have enough balance! Available: ${bal:.2f}.")
        # Only validate min/max against full wager risk, not partial amount
        if wagerObj.risk < self.account.account_level.min_play_amount_cryp:
            raise ValidationError(f"Minimum Amount for Wagers is {self.account.account_level.min_play_amount_cryp}.")
        if wagerObj.risk > self.account.account_level.max_play_amount_cryp:
            raise ValidationError(f"Maximum Amount for Wagers is {self.account.account_level.max_play_amount_cryp}.")
        # Let's calculate if we're using bonus amounts at all or not:
        bal = self.get_balance_obj()

        if bal.available < risk_amount:
            raise ValidationError(f"You don't have enough balance! Available: ${bal.available:.2f}.")

        # By default, Relationship data should include relations to the TX, ie, wagers:
        if "relations" in kwargs:
            rdata = kwargs["relations"]
        else:
            rdata = {}
        # if "type" is in kwargs, assign it, else, "Wager".
        if "type" in kwargs:
            subtype = kwargs["type"]
        else:
            subtype = "Wager"
        ledgerTX = AccountBalanceLedgerTX(parent=bal,type="RISK",fees_change=0,avail_change=0,
                                          at_risk_change=risk_amount,domain=wagerObj.account.domain,
                                          reference_data=rdata,subtype=subtype,vhost=self.vhost,application=wagerObj.application_type)
        ledgerTX.save()
        bal.at_risk += Decimal(risk_amount)
        bal.save()
        bonusObjs = AccountBonusStateTracker.objects.filter(account=self.account,active=True, expires_at__gte=now())
        # TIME TO PROCESS Relations and link to bonuses if applicable:
        if "relations" in kwargs:
            from wager.models import Wager
            for bo in bonusObjs:
                for rel in kwargs["relations"]:
                    try:
                        wo = Wager.objects.get(uuid=rel)
                        abst = AccountBonusStateTracker(bonus_obj_type=bo.__class__.__name__,bonus_obj_uuid=bo.uuid,wager=wo,account=self.account)
                        abst.save()
                    except Wager.DoesNotExist:
                        self.logger.info(f"Could not add Relationship to Bonus State Tracker for Wager with uuid {rel}")
        from cashier.signals import signal_balance_wager_created,signal_balance_at_risk
        signal_balance_at_risk.send(sender=self,account=self.account,amount=risk_amount,wager=wagerObj)
        return True, ledgerTX, bonusObjs

    @transaction.atomic
    def rollback_wager(self,wagerObj,**kwargs):
        self.logger.info(f"Wager {wagerObj.uuid} attempting rollback...")
        if not wagerObj.grade_outcome:
            self.logger.warning(f"Wager {wagerObj.uuid} doesn't have a grade outcome.")
            return False
        bal = self.get_balance_obj()

        if wagerObj.grade_outcome == "L":
            self.logger.info(f"Wager {wagerObj.uuid} was lost, rolling back....")
            ledgerTX = AccountBalanceLedgerTX(parent=bal, type="ROLLBACK", fees_change=0, avail_change=wagerObj.risk,
                                              application=wagerObj.application_type,
                                              at_risk_change=wagerObj.risk, withdrawable_change=0, vhost=self.vhost,
                                              reference_data="", subtype="REGRADE", domain=self.account.domain)
            ledgerTX.save()
            bal.at_risk += wagerObj.risk
            bal.available += wagerObj.risk

            if bal.pending_rollovers > 0:
                bal.pending_rollovers += wagerObj.risk
            bal.save()
        elif wagerObj.grade_outcome == "W":
            self.logger.info(f"Wager {wagerObj.uuid} was won, rolling back....")
            ledgerTX = AccountBalanceLedgerTX(parent=bal, type="ROLLBACK", fees_change=0, avail_change=-wagerObj.win,
                                              application=wagerObj.application_type,
                                              at_risk_change=wagerObj.risk, withdrawable_change=0, vhost=self.vhost,
                                              reference_data="", subtype="REGRADE", domain=self.account.domain)
            ledgerTX.save()

            bal.at_risk += wagerObj.risk
            bal.available -= wagerObj.win

            # Simple rollover logic for now:
            if bal.pending_rollovers > 0:
                bal.pending_rollovers += min(wagerObj.risk, wagerObj.win)


        bal.save()
        wagerObj.grade_outcome = None
        wagerObj.status = "P"
        wagerObj.grader_history["regrade"] = {"regrade":True,"at":now().isoformat(),"tx_rollback":True}
        wagerObj.graded_at = None
        wagerObj.executed = False
        wagerObj.graded = False
        wagerObj.closed = False
        wagerObj.save()
        self.logger.info(f"Wager {wagerObj.uuid} was rolled back.")
        return True

    def get_available_deposit_bonuses(self):
        avail = []
        _adb = AccountDepositBonus.objects.filter(level=self.account.account_level, active=True,vhost=self.vhost)
        for adb in _adb:
            #self.logger.info(adb)
            try:
                check = AccountBonusStateTracker.objects.get(account=self.account,bonus_obj_uuid=adb.uuid,bonus_obj_type=adb.__class__.__name__,vhost=self.vhost)
            except AccountBonusStateTracker.DoesNotExist:
                avail.append(adb)
        return avail


    def _create_bonus_objects(self,_bonusObj,**kwargs):
        if "level" in kwargs:
            bonusObjs = _bonusObj.objects.filter(active=True,vhost=self.vhost,level=kwargs["level"])
        elif "name" in kwargs:
            bonusObjs = _bonusObj.objects.filter(active=True, vhost=self.vhost, name=kwargs["name"])
        else:
            bonusObjs = _bonusObj.objects.filter(active=True, vhost=self.vhost)
        # self.logger.info(bonusObjs)
        trackers = []
        for bonus in bonusObjs:
            histObjs = AccountBonusStateHistory.objects.filter(account=self.account,bonus_obj_type=bonus.__class__.__name__,bonus_obj_uuid=bonus.uuid,vhost=self.vhost)
            if (len(histObjs) > 0):
                self.logger.info(f"Skipping Bonus: {bonus}, already used up for account: {self.account} in Hist: {histObjs[0]}")
                continue

            stateTracker = AccountBonusStateTracker(account=self.account, bonus_obj_type=bonus.__class__.__name__,bonus_obj_uuid=bonus.uuid,
                                                    min_deposit=bonus.reward_deposit,
                                                    expires_at=now() + timedelta(seconds=bonus.time_limit),
                                                    vhost=self.account.vhost,
                                                    deposit_multiplier=bonus.deposit_multiplier,
                                                    rollover=bonus.rollover, rollover_type=bonus.rollover_type,
                                                    min_bet=bonus.min_bet, reward_deposit=bonus.reward_deposit,
                                                    )
            stateTracker.sports.set(bonus.sports.all())
            stateTracker.groups.set(bonus.groups.all())
            stateTracker.save()
            stateHistory = AccountBonusStateHistory(account=self.account, bonus_obj_type=bonus.__class__.__name__,bonus_obj_uuid=bonus.uuid,
                                                    min_deposit=bonus.reward_deposit,
                                                    expires_at=now() + timedelta(seconds=bonus.time_limit),
                                                    vhost=self.account.vhost,
                                                    deposit_multiplier=bonus.deposit_multiplier,
                                                    rollover=bonus.rollover, rollover_type=bonus.rollover_type,
                                                    min_bet=bonus.min_bet, parent=stateTracker,
                                                    reward_deposit=bonus.reward_deposit,
                                                    )
            stateHistory.sports.set(bonus.sports.all())
            stateHistory.groups.set(bonus.groups.all())
            stateHistory.save()
            trackers.append([stateTracker,stateHistory])
        return trackers


    def get_historic_bonuses(self):
        return AccountBonusStateHistory.objects.filter(account=self.account,parent__isnull=True)

    def get_active_bonuses(self):
        return AccountBonusStateTracker.objects.filter(account=self.account, active=True)

    def get_available_deposit_providers(self,vdomain):
        return VDomainPaymentProviders.objects.filter(active=True, vdomain=vdomain,payment_provider__deposits=True)

    def get_available_withdrawal_providers(self,vdomain,name=False,module=False):
        if module:
            return VDomainPaymentProviders.objects.filter(active=True, vdomain=vdomain,
                                                          payment_provider__withdrawals=True,
                                                          payment_provider__module_name=name)

        elif name:
            return VDomainPaymentProviders.objects.filter(active=True, vdomain=vdomain,payment_provider__withdrawals=True,payment_provider__name=name)
        else:
            return VDomainPaymentProviders.objects.filter(active=True, vdomain=vdomain,
                                                          payment_provider__withdrawals=True,)
    def find_withdrawal_providers(self,vdomain, provider_name):
            return VDomainPaymentProviders.objects.get(active=True, vdomain=vdomain,payment_provider__withdrawals=True,payment_provider__name__icontains=provider_name)


    def get_max_possible_wager(self,use_bonus=False):
        retr= min(self.account.account_level.max_play_amount_cryp, self.get_available_balance(use_bonus))
        # self.logger.info(retr)
        return retr

    def account_promocode_eligible(self,promo_code):
        try:
            promoObj = AccountPromoCodeBonus.objects.get(promo_code=promo_code)
        except AccountPromoCodeBonus.DoesNotExist:
            self.logger.info("Invalid Promocode!")
            return False
        checkUsageObj = AccountBonusStateTracker.objects.filter(account=self.account,bonus_obj_uuid=promoObj.uuid,bonus_obj_type=promoObj.__class__.__name__)
        if len(checkUsageObj) > 0:
            self.logger.warning(f"Promocode  {promo_code} already activated for account!")
            return False
        return promoObj


    @transaction.atomic
    def account_activate_promocode(self,promo_code):
        promoObj = self.account_promocode_eligible(promo_code)
        if not promoObj:
            self.logger.warning(f"Invalid Promocode! {promo_code}")
            return False
        self.logger.info(f"Activating promocode for account! {promo_code} / {promoObj}")
        stateHistory,stateTracker = self._create_bonus_objects(AccountPromoCodeBonus)[0]
        self._bonus_payout(promoObj,stateTracker)
        from cashier.signals import signal_bonus_created
        # for stateHistory,stateTracker in trackers:
        signal_bonus_created.send(sender=self, hist=stateHistory, btickt=stateTracker,account=self.account)
        return True

    def account_generic_bonus_eligible(self,bonus_slug):
        try:
            promoObj = GenericInternalBonus.objects.get(vhost=self.vhost,slug=bonus_slug)
        except GenericInternalBonus.DoesNotExist:
            self.logger.warning("Invalid Promocode!")
            return False
        checkUsageObj = AccountBonusStateTracker.objects.filter(account=self.account,bonus_obj_uuid=promoObj.uuid,bonus_obj_type=promoObj.__class__.__name__)
        if len(checkUsageObj) > 0:
            self.logger.info(f"Generic Bonus  {bonus_slug} already activated for account!")
            return False
        return promoObj


    @transaction.atomic
    def account_activate_generic_bonus(self,bonus_slug):
        promoObj = self.account_generic_bonus_eligible(bonus_slug)
        if not promoObj:
            self.logger.warning(f"Invalid Generic Bonus! {bonus_slug}")
            return False
        self.logger.info(f"Activating Generic Bonus for account! {bonus_slug} / {promoObj}")
        stateHistory,stateTracker = self._create_bonus_objects(GenericInternalBonus,name=bonus_slug)[0]
        self._bonus_payout(promoObj,stateTracker)
        from cashier.signals import signal_bonus_created
        # for stateHistory,stateTracker in trackers:
        signal_bonus_created.send(sender=self, hist=stateHistory, btickt=stateTracker,account=self.account)
        return True

    @transaction.atomic
    def set_account_level(self,level,validation_mobile_type="tel"):
        if self.account.account_level == level:
            raise ValidationError("Account Level Already Assigned to Account.")
        self.account.account_level = level

        stateHistory,stateTracker  = self._create_bonus_objects(AccountLevelActivationBonus,level=level)[0]
        from cashier.signals import signal_bonus_created
        signal_bonus_created.send(sender=self, hist=stateHistory, btickt=stateTracker,account=self.account)
        # self.logger.info(f"Created Deposit Bonus State  and history Tracker for {self.account} and bonus {bonus.uuid}")
        # Once the tickets are created; process them:
        i = 0
        bonusObjs = AccountBonusStateTracker.objects.filter(account=self.account, bonus_obj_type="AccountLevelActivationBonus",
                                                            active=True, expires_at__gte=now(),vhost=self.vhost)
        for btickt in bonusObjs:
            i += 1
            # self.logger.info(f"Checking Bonus {btickt}/{i}...")
            btickt.current_deposit += Decimal(btickt.reward_deposit)
            hist = AccountBonusStateHistory.objects.get(parent=btickt)
            hist.current_deposit += Decimal(btickt.reward_deposit)
            # If our deposit is larger than the triggering deposit, trigger the deposit rollover bonus and then delete root ticket, keep history:
            # self.logger.info(f"Current BTicket status, {btickt.uuid}/{btickt.current_deposit}//")
            hist.save()
            btickt.save()
            # PAYOUT Deposit Bonuses that have crossed their threshold!
            if hist.current_deposit >= hist.min_deposit:
                # self.logger.info("Payin' out!")

                bonusObj = self._get_bonus_obj(btickt.bonus_obj_type, btickt.bonus_obj_uuid)
                if bonusObj:
                    self._bonus_payout(bonusObj,btickt)
                    from cashier.signals import signal_bonus_paid
                    signal_bonus_paid.send(sender=self, hist=hist, btickt=btickt,account=self.account,vhost=self.vhost)
        self.account.save()

        return True


    @transaction.atomic
    def _withdraw_from_account(self, amount, provider, type="WITHDRAWAL", subtype="", **kwargs):
        ''' Don't call directly!!! Should be called AFTER a transaction is pending and transacted. Call create_withdrawal_ticket to actually do this.'''
        ''' DO NOT pass the amount already processed with exchange rate for withdrawal; pass an actual FIAT/Crypto amount here! '''
        # Does account have deposit allowed?
        balance = self.get_balance_obj()

        if self.account.account_level.max_withdrawal_cryp <= 0:
            raise ValidationError({"level":"Account's current level does not permit Crypto Withdrawals of this amount."})
        # Disabled for now while we make better counter arrangements:
        # if amount + counters.daily_total_cryp > self.account.account_level.daily_withdrawal_lim_cryp:
        #     raise ValidationError({"daily_limit":"Account's daily withdrawal limit would be exceeded by this transaction."})
        #
        # if amount + counters.weekly_total_cryp > self.account.account_level.weekly_withdrawal_lim_cryp:
        #     raise ValidationError({"weekly_limit":"Account's weekly withdrawal limit would be exceeded by this transaction."})
        #
        # if amount + counters.monthly_total_cryp > self.account.account_level.monthly_withdrawal_lim_cryp:
        #     raise ValidationError({"monthly_limit":"Account's monthly withdrawal limit would be exceeded by this transaction."})
        #
        # if amount + counters.yearly_total_cryp > self.account.account_level.yearly_withdrawal_lim_cryp:
        #     raise ValidationError({"yearly_limit":"Account's yearly withdrawal limit would be exceeded by this transaction."})

        if amount > self.account.account_level.max_withdrawal_cryp:
            raise ValidationError({"max_deposit":f"Deposit amount exceeds maximum crypto withdrawal limit: {amount}"})
        if not self.confirm_withdrawable_balance(amount):
            raise ValidationError({"max_deposit":f"Withdrawal amount exceeds maximum balance available to withdraw!: {amount}"})
        level_fees = Decimal(self.account.account_level.withl_fee_pct_cryp/100)*amount
        provider_fees = Decimal(provider.wdl_fees/100)*amount
        fees = level_fees + provider_fees
        effective_withdrawal = amount - fees
        if "xchg" in kwargs:
            xchg = kwargs["xchg"]
        else:
            xchg = 1
        ledgerTX = AccountBalanceLedgerTX(parent=balance,type=type,subtype=subtype,fees_change=fees,avail_change=-effective_withdrawal,
                                          withdrawable_change=effective_withdrawal,xchg_rate=xchg,
                                          vhost=self.vhost,processor_provider=provider)
        ledgerTX.save()
        if provider.name == "ionBlock":
            xamn = Decimal(round(xchg*amount))
        else:
            xamn = Decimal(round(amount))
        print("amt=", amount)
        print("xchg=", xchg)
        print("xam=", xamn)
        balance.withdrawals += xamn
        print(balance.withdrawals)
        balance.available -= xamn
        print(balance.available)
        balance.fees += Decimal(fees*xchg)
        print(balance.fees)
        if not kwargs.get('skip_pending_adjust') and balance.pending_withdraw >= xamn:
            balance.pending_withdraw -= xamn
            print(balance.pending_withdraw)
        balance.save()

        # Create notification to represent completed withdraw transaction to account.
        notData = {
            "tuuid": str(ledgerTX.uuid)
        }
        if provider.name == "ionBlock":
            msgStr = f"Your withdraw for {amount} ETH has been processed."
        else:
            msgStr = f"Your withdraw for €{amount} EUR has been processed."
        accountNotObj = AccountNotifications(vhost=self.vhost, account=self.account, type=type, data=notData,
                                             title="Withdraw", text=msgStr)
        accountNotObj.save()

        from cashier.signals import signal_balance_withdrawal
        signal_balance_withdrawal.send(sender=self,account=self.account,amount=effective_withdrawal)
        return True, ledgerTX

    @transaction.atomic
    def credit_wager_win(self, wagerObj, **kwargs):
        # Really barebones for now!!
        # TODO: Need to fix this and make it a proper bonus calculator. For demo purposes it goes straight to available; no withdrawals.
        if wagerObj.account != self.account:
            return False,-1
        bal = self.get_balance_obj()
        subtype = "win_payout"
        rdata = [str(wagerObj.uuid)]
        if wagerObj.win > 0:
            bal.available += wagerObj.win
        # if wagerObj.risk > 0:
        #     bal.at_risk -= wagerObj.risk

        ledgerTX = AccountBalanceLedgerTX(parent=bal, type="PAYOUT", fees_change=0, win_change=wagerObj.win,
                                          at_risk_change=wagerObj.risk, withdrawable_change=0,
                                          reference_data=rdata, subtype=subtype,vhost=self.vhost,domain=self.account.domain,application=wagerObj.application_type)
        ledgerTX.save()
        notData = {
                "wuuid":str(wagerObj.uuid)
        }
        accountNotObj = AccountNotifications(vhost=self.vhost,account=wagerObj.account,type="WAGER_WON",data=notData,title="You won!")
        accountNotObj.save()
        if wagerObj.account.manager:
            if wagerObj.win >= wagerObj.account.manager.win_notification_threshold:
                managerNotObj = ManagerNotifications(vhost=self.vhost,manager=wagerObj.account.manager,type="WAGER_WON",data=notData,title="Account Won!")
                managerNotObj.save()
        # Simple rollover logic for now:
        if bal.pending_rollovers > 0:
            bal.pending_rollovers -= min(wagerObj.risk,wagerObj.win)
            if bal.pending_rollovers < 0: bal.pending_rollovers = 0
        bal.save()
        return True, ledgerTX


    @transaction.atomic
    def debit_wager_loss(self,wagerObj,**kwargs):
        # Really barebones for now!!
        # TODO: Need to fix this and make it a proper bonus calculator. For demo purposes it goes straight to losses.
        bal = self.get_balance_obj()
        subtype = "debit_loss"

        bal.at_risk -= wagerObj.risk
        if not wagerObj.use_bonus:
            bal.available -= wagerObj.risk
            ledgerTX = AccountBalanceLedgerTX(parent=bal, type="LOSS", fees_change=0, avail_change=wagerObj.risk,
                                              application=wagerObj.application_type,
                                              at_risk_change=wagerObj.risk, withdrawable_change=0, vhost=self.vhost,
                                              subtype=subtype, domain=self.account.domain,
                                              reference_data=[str(wagerObj.uuid)])
        else:
            ledgerTX = AccountBalanceLedgerTX(parent=bal, type="BONUS_LOSS", fees_change=0, bonus_change=wagerObj.risk,
                                              application=wagerObj.application_type,
                                              at_risk_change=wagerObj.risk, withdrawable_change=0, vhost=self.vhost,
                                              subtype=subtype, domain=self.account.domain,
                                              reference_data=[str(wagerObj.uuid)])


        ledgerTX.save()

        if bal.pending_rollovers > 0:
            bal.pending_rollovers -= wagerObj.risk
            if bal.pending_rollovers < 0: bal.pending_rollovers = 0
        bal.save()
        return True, ledgerTX



    def _get_at_risk_bal(self):

        from wager.models import Wager
        total_risk = (
             Wager.objects
             .filter(
                 account_id=self.account.uuid,
                 vhost=self.vhost,
                 executed=False,
                 status__in=["P", "M"],
                 hide_in_reports=False,
                 grade_outcome__isnull=True,

             )
             .aggregate(total=Sum("risk"))
         )["total"] or 0
        return total_risk


    def set_risk_bal(self):
        at_risk = self._get_at_risk_bal()
        bal = self.get_balance_obj()
        if bal:
            bal.at_risk = at_risk
            bal.save()
        else:
            self.logger.warning(f"Account {self.account.uuid} has no balance object.. not setting risk.")