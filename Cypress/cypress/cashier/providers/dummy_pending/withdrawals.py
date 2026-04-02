from decimal import Decimal

from cashier.models import DummyProviderTXStub


class WithdrawalProvider(object):
    def create_withdrawal(self,domain,account,amount,fees):
        if amount <= 0:
            raise ValueError("amount must be > 0")
        if amount > 100:
            raise ValueError("amount must be <= 100")
        dtxObj = DummyProviderTXStub(account=account,amount=amount,fees=fees,vdomain=domain,provider_fees=amount*Decimal(.05),type="WDL")
        dtxObj.save()
        # NOTE: Returns 0 (for PENDING Withdrawal ) and TXID
        # in the API design of the cashier, receiving a 0 means the deposit is not yet failed, and we're
        # waiting for a reply for an external service, thus, the status is "PENDING".
        # in this state, the second value should contain the pending TXID and we provide it here.
        return 0, dtxObj.provider_tx
