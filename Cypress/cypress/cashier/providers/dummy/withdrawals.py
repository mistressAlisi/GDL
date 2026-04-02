from decimal import Decimal

from cashier.models import DummyProviderTXStub


class WithdrawalProvider(object):
    def create_withdrawal(self,domain,account,amount,fees,**kwargs):
        if amount <= 0:
            raise ValueError("amount must be > 0")
        if amount > 100:
            raise ValueError("amount must be <= 100")
        dtxObj = DummyProviderTXStub(account=account,amount=amount,fees=fees,vdomain=domain,provider_fees=amount*Decimal(.05),type="WDL")
        dtxObj.save()
        # NOTE: Returns TRUE (for successful deposit) and FALSE for (no further action needed)
        # in the API design of the cashier, if the second value is FALSE, the amount is already completely deposited,
        # and the account should be credited immediately.
        # If this is passed as TRUE, TRUE, then the Cashier
        # will call continue_deposit() on the provider object
        # to show the needed forms/validation steps.
        return True, False
