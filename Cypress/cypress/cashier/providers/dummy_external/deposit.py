from decimal import Decimal
from cashier.models import DummyProviderTXStub


class DepositProvider(object):
    def create_deposit(self,domain,account,amount,fees):
        if amount <= 0:
            raise ValueError("amount must be > 0")
        if amount > 100:
            raise ValueError("amount must be <= 100")
        dtxObj = DummyProviderTXStub(account=account,amount=amount,fees=fees,vdomain=domain,provider_fees=amount*Decimal(.05))
        dtxObj.save()
        payment_url = f"https://test.url/payment_gateways?txid={dtxObj.uuid}"
        # NOTE: Returns -1 (for PENDING EXTERNAL Deposit) and TXID
        # in the API design of the cashier, receiving a 0 means the deposit is not yet failed, and we're
        # waiting for a reply for an external service, thus, the status is "PENDING".
        # in this state, the second value should contain the pending TXID and we provide it here.
        # We also pass a THIRD object in this mode, the payment TX url for further validation:
        return -1, dtxObj.provider_tx,payment_url
