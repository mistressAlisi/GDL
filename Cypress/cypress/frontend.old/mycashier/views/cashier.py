import datetime
import time
from datetime import timedelta
from decimal import Decimal
from math import floor

from click import DateTime
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password, check_password

from account.forms import TimeZoneForm
from account.models import Account
from cashier.engine import Cashier
from cashier.models import VDomainPaymentProviders, CryptoCurrency, CashierVDomainParameters, \
     AccountLossesLimits, AccountReferralCodeTracker, AccountBalanceLedgerTX, \
    AccountBonusStateTracker, AccountDepositBonus, IonBlockChannel
from cashier.models.sepawithdrawrequest import SepaWithdrawRequest
# from frontend.mycashier.forms import  AccountLossesLimitsForm, SepaWithdrawForm

from minerve.toolkit.errors import generic_json_error
from minerve.toolkit.responses import generic_json_success
from notifications.models import AccountNotifications
from parameters.models import VHostUserMenuEntry, VHostUserSideBarEntry, \
    VHostCryptoExchangeCurrencies, VHostParameterRegistry

from toolkit.decorators import account_login
from toolkit.string import random_string
from django.utils.translation import gettext_lazy as _

CASHIER_PROVIDERS_STR = _("Cashier Providers")
PROVIDER_ERROR_STR = _("Provider Error")
UNABLE_TO_GENERATE_DEP_URL_STR = _("Unable to generate deposit URL")
CASHIER_ERROR = _("Cashier Error")
TYPE_STR = _("Type")
TXN_STR = _("TXN")
UPDATED_STR = _("Updated")
CURRENCY1_STR = _("Currency 1")
AMOUNT1_STR = _("Amount 1")
CURRENCY2_STR = _("Currency 2")
AMOUNT2_STR = _("Amount 2")
RECEIVED_STR = _("Received")
PENDING_STR = _("Pending")
WAIT_FOR_EMAIL_CONF_STR = _("Waiting for Email Confirmation")

@account_login
def my_balance(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    balance = cashier.get_balance()
    avail = cashier.get_available_balance()
    cwp,cc= VHostParameterRegistry.objects.get_or_create(vhost=vhost,application="cashier",name="withdrawal_page")
    wd_avail = floor(avail/100)
    if cc:
        cwp.value_text ="gift_cards.html"
        cwp.save()
    context.update({
        "cryptoParams":cryptoParams,
        "balance":balance,
        "cashier":cashier,
        "available":avail,
        "wd_avail":wd_avail,
        "cashier_withdrawal_page":f"dashboard/cashier/withdrawal/providers/{cwp.value_text}",
    })


    return render(request, "dashboard/cashier/balance.html", context)

@account_login
def my_promos(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    context.update({
        "cryptoParams":cryptoParams,
        "promos":cashier.get_active_bonuses()
    })


    return render(request, "dashboard/cashier/promos/active.html", context)

@account_login
def my_past_promos(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    context.update({
        "cryptoParams":cryptoParams,
        "promos":cashier.get_historic_bonuses()
    })
    account_ping(context["account"], request)

    return render(request, "dashboard/cashier/promos/historic.html", context)

# @account_login
def deposit_landing(request):
    # if 'account_id' not in request.session:
    #     return redirect("/login")
    # vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cdp,cc= VHostParameterRegistry.objects.get_or_create(vhost=vhost,application="cashier",name="deposit_landing_page")
    if cc:
        cdp.value_text ="default_providers.html"
        cdp.save()
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    providers = cashier.get_available_deposit_providers(vdomain)
    bonuses = cashier.get_available_deposit_bonuses()
    if not cashier.account_generic_bonus_eligible("REFERRED"):
        referred = True
    else:
        referred = False
    referrals = AccountReferralCodeTracker.objects.filter(vhost=vhost,referrer=account)
    context.update({
        "cryptoParams": cryptoParams,
        "max_deposit":cashier.get_max_deposit(),
        "providers":providers,
        "bonuses":bonuses,
        "referrals":referrals,
        "referred":referred,
        "cashier_deposit_page":f"dashboard/cashier/deposit/{cdp.value_text}",


    })

    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/deposit/landing.html", context)

@account_login
def deposit_start(request,provider):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    #TODO: This can be fixed up...
    iframe_url = ""

    # Handle hotwallet provider
    if provider == "cashier.providers.hotwallet":
        # Get amount from request or use minimum
        amount = request.GET.get('amount', None)
        if amount is None:
            providers = cashier.get_available_deposit_providers(vdomain)
            try:
                chosen_provider = providers.get(payment_provider__module_name=provider)
                amount = chosen_provider.payment_provider.dep_min
            except VDomainPaymentProviders.DoesNotExist:
                no_such_provider_str = _("No such provider: {provider}").format(provider=provider)
                return generic_json_error(CASHIER_PROVIDERS_STR, no_such_provider_str)

        try:
            from decimal import Decimal
            result = cashier.create_deposit_ticket(vdomain, provider, Decimal(str(amount)))
            if result[0] == -2 and "majestic_url" in result[1]:
                iframe_url = result[1]["majestic_url"]
            else:
                return generic_json_error(PROVIDER_ERROR_STR, UNABLE_TO_GENERATE_DEP_URL_STR)
        except Exception as e:
            return generic_json_error("Cashier Error", str(e))

    # Handle ionBlock provider
    elif provider == "cashier.providers.ionBlock":
        # Check if amount was submitted
        amount = request.POST.get('amount') or request.GET.get('amount')
        currency_selected = request.POST.get('currency') or request.GET.get('currency')

        if amount:
            # User submitted amount - create deposit channel
            try:
                from decimal import Decimal
                import logging
                logger = logging.getLogger(__name__)

                amount_decimal = Decimal(str(amount))
                logger.info(f"ionBlock: Creating deposit ticket for ${amount_decimal}")

                # Create deposit ticket with ETH as currency
                result = cashier.create_deposit_ticket(
                    vdomain,
                    provider,
                    amount_decimal,
                    currency=currency_selected
                )

                # Check if result is an error JsonResponse
                if isinstance(result, JsonResponse):
                    logger.error(f"ionBlock: Deposit failed, returning error response")
                    return result

                logger.info(f"ionBlock: Result status code: {result[0]}")

                if result[0] == -2:
                    # Success - channel created, show payment details
                    channel_data = result[1]
                    logger.info(f"ionBlock: Channel created successfully: {channel_data.get('channel_id', 'N/A')}")
                    context.update({
                        "cryptoParams": cryptoParams,
                        "max_deposit": cashier.get_max_deposit(),
                        "cashier": cashier,
                        "ionblock_channel": channel_data,
                        "show_channel": True
                    })
                    account_ping(context["account"], request)
                    return render(request, "dashboard/cashier/deposit/ionblock_channel.html", context)
                else:
                    logger.error(f"ionBlock: Unexpected result code: {result[0]}")
                    return generic_json_error("Provider Error", "Unable to create payment channel")
            except Exception as e:
                logger.error(f"ionBlock: Exception occurred: {str(e)}", exc_info=True)
                return generic_json_error("Cashier Error", str(e))
        else:
            # Show amount input form
            providers = cashier.get_available_deposit_providers(vdomain)
            try:
                chosen_provider = providers.get(payment_provider__module_name=provider)
                min_deposit = chosen_provider.payment_provider.dep_min
                max_deposit = cashier.get_max_deposit()
            except VDomainPaymentProviders.DoesNotExist:
                min_deposit = 10
                max_deposit = cashier.get_max_deposit()

            context.update({
                "cryptoParams": cryptoParams,
                "max_deposit": max_deposit,
                "min_deposit": min_deposit,
                "cashier": cashier,
                "provider": provider,
                "show_amount_form": True
            })
            account_ping(context["account"], request)
            return render(request, "dashboard/cashier/deposit/ionblock_amount.html", context)

    # Handle Apple Pay, PayPal, and Credit Card via Majestic with hotwallet
    elif provider in ["apl", "pyl", "crd"]:
        # Get amount from request or use minimum
        amount = request.GET.get('amount', None)
        if amount is None:
            # Use default minimum amount for hotwallet
            amount = 0.01  # Default minimum ETH
        try:
            from decimal import Decimal
            # Create hotwallet deposit with payment method specified
            # This will generate the wallet and the appropriate Majestic URL
            result = cashier.create_deposit_ticket(
                vdomain,
                "cashier.providers.hotwallet",
                Decimal(str(amount)),
                payment_method=provider  # Pass the payment method (apl, pyl, crd)
            )

            if result[0] == -2 and "majestic_url" in result[1]:
                # Use the Majestic URL generated by the provider
                iframe_url = result[1]["majestic_url"]
                print(f"DEBUG: Generated Majestic URL for {provider}: {iframe_url}")
            else:
                return generic_json_error("Provider Error", "Unable to generate deposit URL")
        except Exception as e:
            return generic_json_error("Cashier Error", str(e))

    context.update({
        "cryptoParams": cryptoParams,
        "max_deposit":cashier.get_max_deposit(),
        "iframe_url":iframe_url,
        "cashier":cashier,


    })
    #print(context)
    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/deposit/start.html", context)

@account_login
def deposit_start_v1(request,provider):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    providers = cashier.get_available_deposit_providers(vdomain)
    try:
        chosen_provider = providers.get(payment_provider__module_name=provider)
    except VDomainPaymentProviders.DoesNotExist:
        no_such_provider_str = _("No such provider: {provider}").format(provider=provider)
        return generic_json_error(CASHIER_PROVIDERS_STR, no_such_provider_str)
    bonuses = cashier.get_available_deposit_bonuses()

    context.update({
        "cryptoParams": cryptoParams,
        "max_deposit":cashier.get_max_deposit(),
        "provider":chosen_provider.payment_provider,
        "bonuses":bonuses,
        "cashier":cashier,


    })
    #print(context)
    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/deposit/start.html", context)


@account_login
def deposit_modal(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request, "player")
    cdp, cc = VHostParameterRegistry.objects.get_or_create(vhost=vhost, application="cashier",
                                                           name="deposit_landing_page")
    if cc:
        cdp.value_text = "default_providers.html"
        cdp.save()
    cashier = Cashier(vhost=vhost,account=account)
    providers = cashier.get_available_deposit_providers(vdomain)
    bonuses = cashier.get_available_deposit_bonuses()
    context.update({
        "max_deposit":cashier.get_max_deposit(),
        "providers":providers,
        "bonuses":bonuses,
        "cashier_deposit_page": f"dashboard/cashier/deposit/{cdp.value_text}",


    })

    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/deposit/modal.html", context)


@account_login
def buy_tokens(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    top_menu = VHostUserMenuEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    side_menu = VHostUserSideBarEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')

    context.update({
        "cryptoParams":cryptoParams,
        "DYNAMIC_DASHBOARD_TOP_MENU": top_menu,
        "DYNAMIC_DASHBOARD_SIDE_MENU": side_menu,
        "MINERVE_BODY_THEME": "dark",
        
    })
    account_ping(context["account"], request)

    return render(request, "dashboard/cashier/buy_tokens/step1.html", context)


@account_login
def completed_transactions(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    transactions = VHostCryptoTransactionLedger.objects.filter(vhost=vhost,account=context["account"],deposited=True)
    top_menu = VHostUserMenuEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    side_menu = VHostUserSideBarEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    context.update({
        "cryptoParams":cryptoParams,
        "DYNAMIC_DASHBOARD_TOP_MENU": top_menu,
        "DYNAMIC_DASHBOARD_SIDE_MENU": side_menu,
        "MINERVE_BODY_THEME": "dark",
        
        "table_header_rows":[TYPE_STR,TXN_STR,UPDATED_STR,CURRENCY1_STR,AMOUNT1_STR,CURRENCY2_STR, AMOUNT2_STR],
        "table_rows":transactions
    })
    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/completed.html", context)


@account_login
def pending_transactions(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    transactions = VHostCryptoTransactionLedger.objects.filter(vhost=vhost,account=context["account"],status__lt=100)
    top_menu = VHostUserMenuEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    side_menu = VHostUserSideBarEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    context.update({
        "cryptoParams":cryptoParams,
        "DYNAMIC_DASHBOARD_TOP_MENU": top_menu,
        "DYNAMIC_DASHBOARD_SIDE_MENU": side_menu,
        "MINERVE_BODY_THEME": "dark",
        
        "table_header_rows":[TYPE_STR,TXN_STR,UPDATED_STR,CURRENCY1_STR,AMOUNT1_STR,CURRENCY2_STR, AMOUNT2_STR,RECEIVED_STR,PENDING_STR],
        "table_rows":transactions
    })
    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/pending.html", context)


@account_login
def exchange_tokens_step1(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    tokens = VHostCryptoExchangeCurrencies.objects.filter(vhost=vhost,active=True)
    top_menu = VHostUserMenuEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    side_menu = VHostUserSideBarEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    context.update({
        "cryptoParams": cryptoParams,
        "DYNAMIC_DASHBOARD_TOP_MENU": top_menu,
        "DYNAMIC_DASHBOARD_SIDE_MENU": side_menu,
        "MINERVE_BODY_THEME": "dark",
        

        "tokens":tokens,

    })
    account_ping(context["account"], request)

    return render(request, "dashboard/cashier/exchange_tokens/step1.html", context)

@account_login
def exchange_tokens_step2(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    withdrawal_amount =  Decimal(request.POST["xchange_amount"])
    dest_crypto = request.POST["dest_crypto"]
    wallet_address_1 = request.POST["wallet_address_1"]
    wallet_address_1_prev = wallet_address_1[-6:]
    token = VHostCryptoExchangeCurrencies.objects.filter(vhost=vhost,active=True,symbol=dest_crypto)
    top_menu = VHostUserMenuEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    side_menu = VHostUserSideBarEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    withdrawal_amount_bcrypto = withdrawal_amount / cryptoParams.token_base_currency_xrate
    context.update({
        "cryptoParams":cryptoParams,
        "token":token,
        "withdrawal_amount":withdrawal_amount,
        "dest_crypto":dest_crypto,
        "wallet_address_1":wallet_address_1,
        "withdrawal_amount_bcrypto":withdrawal_amount_bcrypto,
        "wallet_address_1_prev":wallet_address_1_prev,
        "DYNAMIC_DASHBOARD_TOP_MENU": top_menu,
        "DYNAMIC_DASHBOARD_SIDE_MENU": side_menu,
        "MINERVE_BODY_THEME": "dark",
        


    })
    account_ping(context["account"], request)

    return render(request, "dashboard/cashier/exchange_tokens/step2.html", context)


@account_login
def exchange_tokens_step3(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    withdrawal_amount =  Decimal(request.POST["amount"])
    dest_crypto = request.POST["dest_crypto"]
    wallet_address_1 = request.POST["wallet_address_1"]
    wallet_address_2 = request.POST["wallet_address_2"]
    top_menu = VHostUserMenuEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    side_menu = VHostUserSideBarEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    context.update({
        "DYNAMIC_DASHBOARD_TOP_MENU": top_menu,
        "DYNAMIC_DASHBOARD_SIDE_MENU": side_menu,
        "MINERVE_BODY_THEME": "dark",
        
    })
    if withdrawal_amount > context["account"].withdrawable:
        account_ping(context["account"], request)
        return render(request, "dashboard/cashier/exchange_tokens/funds_error.html", context)

    if wallet_address_1 != wallet_address_2:
        account_ping(context["account"], request)
        return render(request, "dashboard/cashier/exchange_tokens/wallet_error.html", context)
    token = VHostCryptoExchangeCurrencies.objects.filter(vhost=vhost,active=True,symbol=dest_crypto)
    withdrawal_amount_bcrypto = withdrawal_amount / cryptoParams.token_base_currency_xrate
    context["account"].withdrawable -= withdrawal_amount
    context["account"].available -= withdrawal_amount
    context["account"].pending_withdraw += withdrawal_amount
    context["account"].save()
    edate = now() + timedelta(days=2)
    ckey = random_string(64)
    txn = random_string(32)
    transObj = VHostCryptoTransactionLedger(vhost=vhost,account=context["account"],type='w',
                                            address=wallet_address_1,amount1=withdrawal_amount_bcrypto,currency1=cryptoParams.token_base_currency,
                                            currency2=dest_crypto,pending=True,expiry_date=edate,confirmation_key=ckey,txn_id=txn)
    transObj.status_text = WAIT_FOR_EMAIL_CONF_STR
    transObj.status = 1
    transObj.save()
    context.update({
        "cryptoParams":cryptoParams,
        "token":token,
        "withdrawal_amount":withdrawal_amount,
        "dest_crypto":dest_crypto,
        "wallet_address_1":wallet_address_1,
        "withdrawal_amount_bcrypto":withdrawal_amount_bcrypto,
        "transaction":transObj
    })
    account_ping(context["account"], request)
    conf_exchange_tx_str = _("{apperance}: Confirm Exchange Transaction").format(apperance = apperance.site_name)
    email_str = render_to_string("dashboard/cashier/exchange_tokens/emails/confirm_exchange.eml", context)
    email = EmailMessage(
        conf_exchange_tx_str,
        email_str,
        settings.EMAIL_FROM_ADDR,
        [ context["account"].email1],
        [],
        reply_to=[settings.EMAIL_REPLY_TO],
    )
    email.send()
    return render(request, "dashboard/cashier/exchange_tokens/step3.html", context)

@account_login
def exchange_tokens_confirm(request,confirm_key):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    try:
        transObj = VHostCryptoTransactionLedger.objects.get(account=context["account"],confirmation_key=confirm_key,type="w",confirmed=False)
    except VHostCryptoTransactionLedger.DoesNotExist:
        return render(request, "dashboard/cashier/exchange_tokens/token_error.html", context)
    transObj.confirmed = True
    transObj.save()
    top_menu = VHostUserMenuEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    side_menu = VHostUserSideBarEntry.objects.filter(vhost=vhost, domains__in=[vdomain], active=True).order_by('ordering_key')
    context.update({
        "transaction":transObj,
        "DYNAMIC_DASHBOARD_TOP_MENU": top_menu,
        "DYNAMIC_DASHBOARD_SIDE_MENU": side_menu,
        "MINERVE_BODY_THEME": "dark",
        
    })
    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/exchange_tokens/transaction_confirmed.html", context)

@account_login
def exchange_tokens_resend(request,tuuid):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    try:
        transObj = VHostCryptoTransactionLedger.objects.get(account=context["account"],uuid=tuuid,type="w",confirmed=False)
    except VHostCryptoTransactionLedger.DoesNotExist:
        return render(request, "dashboard/cashier/exchange_tokens/token_error.html", context)
    context.update({
        "token_amount": transObj.amount1 * cryptoParams.token_base_currency_xrate,
        "crypto_amount": transObj.amount1,
        "crypto_name": cryptoParams.token_base_currency,
        "dest_crypto": transObj.currency2,
        "transaction":transObj

    })
    conf_exchange_tx_str = _("{apperance}: Confirm Exchange Transaction").format(apperance=apperance.site_name)
    email_str = render_to_string("dashboard/cashier/exchange_tokens/emails/confirm_exchange.eml", context)
    email = EmailMessage(
        conf_exchange_tx_str,
        email_str,
        settings.EMAIL_FROM_ADDR,
        [context["account"].email1],
        [],
        reply_to=[settings.EMAIL_REPLY_TO],
    )
    email.send()
    account_ping(context["account"], request)
    return redirect("/cashier/pending")


@account_login
def withdrawal_landing(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    providers = cashier.get_available_withdrawal_providers(vdomain)
    context.update({
        "cryptoParams": cryptoParams,
        "max_deposit":cashier.get_max_deposit(),
        "providers":providers,
        "pending_wdl":cashier.get_pending_withdrawals(),
        "available":cashier.get_available_balance(),

    })
    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/withdrawal/landing.html", context)

@account_login
def withdrawal_start(request,provider):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    providers = cashier.get_available_withdrawal_providers(vdomain)
    amount = request.GET.get('amount', None)
    try:
        chosen_provider = providers.get(payment_provider__module_name=provider)
    except VDomainPaymentProviders.DoesNotExist:
        return generic_json_error("Cashier Providers", f"No such provider: {provider}")
    bonuses = []  # No bonuses for withdrawals

    # For ionBlock, get actual ETH exchange rate
    exchange_rate = 1  # Default for fiat
    if provider == "cashier.providers.ionBlock":
        # Get ETH exchange rate (USD per ETH)
        try:
            from cashier.models import CryptoCurrency
            eth = CryptoCurrency.objects.get(vhost=vhost, symbol='ETH')
            exchange_rate = float(eth.current_usd_exr)  # e.g., 2747.51 USD per ETH
        except CryptoCurrency.DoesNotExist:
            exchange_rate = 1

    context.update({
        "cryptoParams": cryptoParams,
        "max_deposit":cashier.get_max_deposit(),
        "provider":chosen_provider.payment_provider,
        "bonuses":bonuses,
        "cashier":cashier,
        "is_fiat": False,  # ionBlock is crypto, not fiat
        "withdrawal_exchange_rate": exchange_rate,  # USD per ETH for withdrawals
        "amount": amount,
    })
    #print(context)
    account_ping(context["account"], request)
    return render(request, "dashboard/cashier/withdrawal/start.html", context)

@account_login
def application_limits(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    applications = VHostLicencedApplications.objects.filter(vhost=vhost)
    appl = []
    for app in applications:
        aas,asc = AccountApplicationLimits.objects.get_or_create(vhost=vhost,application=app.application,account=account)
        if asc: aas.save()
        appl.append([app.application,aas])
    cashier = Cashier(vhost=vhost,account=account)
    context.update({
        "balance":cashier.get_balance_obj(),
        "cashier":cashier,
        "limits":appl,
    })
    account_ping(context["account"], request)

    return render(request, "dashboard/cashier/application_limits.html", context)


@account_login
def application_limit_form(request,auuid):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    application = VHostLicencedApplications.objects.get(vhost=vhost,application__uuid=auuid)
    aas = AccountApplicationLimits.objects.get(vhost=vhost, application=application.application, account=account)

    modal_form = ApplicationLimitForm(initial={
        "application":application.application,
        "vhost":vhost,
        "account":account},instance=aas)

    context.update({
        "modal_form":modal_form,
        "application":application.application
    })
    return render(request, "dashboard/cashier/limit_modal.html", context)

@account_login
def losses_limits(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    limits,lc = AccountLossesLimits.objects.get_or_create(vhost=vhost,account=account)
    if lc: limits.save()
    cashier = Cashier(vhost=vhost,account=account)
    context.update({
        "balance":cashier.get_balance_obj(),
        "cashier":cashier,
        "cashier_limits":limits,
    })
    account_ping(context["account"], request)

    return render(request, "dashboard/cashier/loss_limits.html", context)


@account_login
def losses_limit_form(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    limits,lc = AccountLossesLimits.objects.get_or_create(vhost=vhost,account=account)
    if lc: limits.save()
    modal_form = AccountLossesLimitsForm(initial={

        "vhost":vhost,
        "account":account},instance=limits)

    context.update({
        "modal_form":modal_form
    })
    return render(request, "dashboard/cashier/loss_limit_modal.html", context)

@account_login
def account_lockout(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    applications = VHostLicencedApplications.objects.filter(vhost=vhost)
    appl = []
    for app in applications:
        aas,asc = AccountApplicationLimits.objects.get_or_create(vhost=vhost,application=app.application,account=account)
        if asc: aas.save()
        appl.append([app.application,aas])
    cashier = Cashier(vhost=vhost,account=account)
    context.update({
        "balance":cashier.get_balance_obj(),
        "cashier":cashier,
        "limits":appl,
    })
    account_ping(context["account"], request)

    return render(request, "dashboard/cashier/account_lockout.html", context)


@account_login
def withdrawal_validate(request):
    """
    Handle withdrawal form submission and create withdrawal transaction
    """
    from django.contrib.auth.hashers import check_password

    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request, "player")

    if request.method != 'POST':
        return generic_json_error("Invalid Request", "Only POST requests are allowed")

    try:
        # Validate password first
        pwd = request.POST.get("acct_passwd")
        if not pwd or not check_password(pwd, account.secret):
            return generic_json_error("Incorrect credentials!", "Please check your password!")

        # Get form data
        provider = request.POST.get('provider')
        amount = Decimal(request.POST.get('amount', '0'))
        address = request.POST.get('address', '').strip()
        network = request.POST.get('network', 'ETH')

        # Validate inputs
        if not provider:
            return generic_json_error("Invalid Request", "Provider is required")

        if amount <= 0:
            return generic_json_error("Invalid Amount", "Amount must be greater than 0")

        # For ionBlock and hotwallet, validate address
        if provider in ["cashier.providers.ionBlock", "cashier.providers.hotwallet"]:
            if not address:
                return generic_json_error("Invalid Address", "Withdrawal address is required")

            # Basic Ethereum address validation
            if not address.startswith('0x') or len(address) != 42:
                return generic_json_error(
                    "Invalid Address",
                    "Please enter a valid Ethereum address (0x...)"
                )

        # Initialize cashier
        cashier = Cashier(vhost=vhost, account=account)

        # Create withdrawal ticket
        # Amount is in tokens (1 token = $1 USD)
        # Pass ETH as the crypto symbol, ionBlock will handle USD->ETH conversion
        result = cashier.create_withdrawal_ticket(
            vdomain,
            provider,
            'ETH',
            amount,
            address=address,
            network=network
        )

        # Check if result is an error
        if isinstance(result, dict) and result.get('res') == 'err':
            return result

        # Success
        return generic_json_success(
            "Withdrawal Created!",
            f"Your withdrawal of ${amount} has been initiated. "
            f"You will receive ETH at {address}. "
            f"The transaction will be processed shortly."
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return generic_json_error("Withdrawal Failed", str(e))

@account_login
def landing_dep(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    balance = cashier.get_balance()
    avail = cashier.get_available_balance()
    # bonusEngine, bonus_created = AccountInitialDepositBonus.objects.get_or_create(account=account, level=account.account_level, is_fiat=True, vhost=vhost, deposit_multiplier=5, reward_deposit=500)
    message_type_filter = ['WITHDRAWAL', 'WITHDRAW_PENDING', 'DEPOSIT', 'DEPOSIT_PENDING', 'BONUS']
    messageEngine = AccountNotifications.objects.filter(account=account, vhost=vhost, type__in=message_type_filter).order_by("-created_at")
    unread_alert_count = messageEngine.filter(seen_at=None).count()
    cwp,cc= VHostParameterRegistry.objects.get_or_create(vhost=vhost,application="cashier",name="landing_deposit")
    wd_avail = floor(avail/100)
    pending = cashier.get_at_risk_balance()
    ledger_tx = AccountBalanceLedgerTX.objects.filter(Q(type="DEPOSIT") | Q(type="WITHDRAWAL"), vhost=vhost,parent__account=account).order_by('-created')
    if cc:
        cwp.value_text ="gift_cards.html"
        cwp.save()
    context.update({
        "cryptoParams":cryptoParams,
        "balance":balance,
        "cashier":cashier,
        "available":avail,
        "wd_avail":wd_avail,
        "pending":pending,
        "ledger":ledger_tx,
        "messageEngine":messageEngine,
        "unread_alert_count":unread_alert_count,
    })
    account_ping(context["account"], request)
    # if "vip" in vdomain.domain_fqdn:
    #     return render(request,  "dashboard/cashier/deposit/new_landing.html", context)
    # else:
    #     context["cashier_deposit_page"] = "dashboard/cashier/deposit/referral_dep_only.html"
    #     return render(request, "dashboard/cashier/deposit/landing.html", context)
    return render(request,  "dashboard/cashier/deposit/new_landing.html", context)

@account_login
@require_POST
def claim_bonus(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request, "player")
    # bonusEngine = AccountInitialDepositBonus.objects.get(account=account, level=account.account_level, is_fiat=True, vhost=vhost)
    # if bonusEngine.is_user_claimed or bonusEngine.active == False:
    #     return JsonResponse({"success": False, "message": "Bonus already claimed"})

    # bonusEngine.is_user_claimed = True
    # bonusEngine.save(update_fields=["is_user_claimed"])
    return JsonResponse({"success": True})

@account_login
def landing_withd(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=vhost)[0]
    cashier = Cashier(vhost=vhost,account=account)
    balance = cashier.get_balance()
    avail = cashier.get_available_balance()
    # bonusEngine, bonus_created = AccountInitialDepositBonus.objects.get_or_create(account=account, level=account.account_level, is_fiat=True, vhost=vhost)
    message_type_filter = ['WITHDRAWAL', 'WITHDRAW_PENDING', 'DEPOSIT', 'DEPOSIT_PENDING', 'BONUS']
    messageEngine = AccountNotifications.objects.filter(account=account, vhost=vhost, type__in=message_type_filter).order_by("-created_at")
    unread_alert_count = messageEngine.filter(seen_at=None).count()
    cwp,cc= VHostParameterRegistry.objects.get_or_create(vhost=vhost,application="cashier",name="landing_withdraw")
    wd_avail = floor(avail/100)
    pending = cashier.get_at_risk_balance()
    ledger_tx = AccountBalanceLedgerTX.objects.filter(Q(type="DEPOSIT") | Q(type="WITHDRAWAL"), vhost=vhost,parent__account=account).order_by('-created')
    if cc:
        cwp.value_text ="gift_cards.html"
        cwp.save()
    context.update({
        "cryptoParams":cryptoParams,
        "balance":balance,
        "cashier":cashier,
        "available":avail,
        "wd_avail":wd_avail,
        "cashier_withdrawal_page":f"dashboard/cashier/withdrawal/providers/{cwp.value_text}",
        "pending":pending,
        "ledger":ledger_tx,
        # "bonusEngine":bonusEngine,
        "messageEngine":messageEngine,
        "unread_alert_count":unread_alert_count,
    })
    account_ping(context["account"], request)
    if "vip" or "127.0.0.1" in vdomain.domain_fqdn:
        return render(request, "dashboard/cashier/withdrawal/new_landing.html", context)
    else:
        return render(request, "dashboard/cashier/withdrawal/landing.html", context)

@account_login
@require_POST
def mark_message_read(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request, "player")
    alert_id = request.POST.get("alert_id")
    if not alert_id:
        return JsonResponse({"success": False, "error": "Missing alert_id"}, status=400)

    updated = AccountNotifications.objects.filter(
        uuid=alert_id,
        account=account,
        vhost=vhost,
        seen_at=None
    ).update(seen_at=datetime.datetime.now())

    if updated == 0:
        return JsonResponse({"success": False, "error": "Message not found or already read"}, status=404)

    return JsonResponse({"success": True})

def ionblock_status(request, channel_id):
    channel = get_object_or_404(IonBlockChannel, channel_id=channel_id)
    if channel.valid_until - int(round(time.time() * 1000)) <= 0 and channel.status != "Expired/Failed":
        channel.status = "Expired/Failed"
        channel.save(update_fields=["status"])

    return JsonResponse({
        "status": channel.status,
        "expired": channel.is_expired,
        "valid_until": channel.valid_until if channel.valid_until else None
    })

@account_login
def sepa_request_page(request):
    if 'account_id' not in request.session:
        return redirect("/login")
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    amount = request.GET.get('amount', None)
    cashier = Cashier(vhost=vhost, account=account)
    context.update({
        "amount": amount,
    })
    account_ping(context["account"], request)

    if request.method == "POST":
        form = SepaWithdrawForm(request.POST)

        if form.is_valid():

            # 🔐 PASSWORD VALIDATION
            password = form.cleaned_data["acct_passwd"]
            user = request.user

            if not check_password(password, account.secret):
                form.add_error(
                    "acct_passwd",
                    _("Incorrect account password.")
                )
            else:
                # ✅ Password verified — proceed
                data = form.cleaned_data

                # SEND MESSAGE TO ADMINS
                with transaction.atomic():
                    print("CODE RUN #1")
                    cashier.create_withdrawal_ticket(vdomain, "cashier.providers.sepa", 'EUR', _amount=data["amount"], wd_data=data)
                messages.success(
                    request,
                    _("Your SEPA withdrawal request has been submitted.")
                )
                return redirect("withdrawal_landing")  # or success page

    else:
        form = SepaWithdrawForm()

    context.update({
        "form": form,
    })


    return render(request, "dashboard/cashier/withdrawal/bank_transfer_form.html", context)


def health_check(request):
    return JsonResponse({"res": "ok"})