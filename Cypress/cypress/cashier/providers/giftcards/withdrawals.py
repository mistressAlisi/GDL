from decimal import Decimal

from cashier.models import AccountBalanceLedgerTX
from cashier.providers.giftcards.models import GiftCardWithdrawal


class WithdrawalProvider(object):
    def create_withdrawal(self,domain,account,_amount,fees,**kwargs):
        amount = _amount/100

        if amount <= 0:
            raise ValueError("amount must be > 0")
        if amount > 1000000:
            raise ValueError("amount must be <= 1000")
        gcwObj = GiftCardWithdrawal.objects.create(vhost=account.vhost,domain=account.domain,account=account,amount=amount)
        gcwObj.save()
        # NOTE: Returns 0 (for PENDING Withdrawal ) and TXID
        return 0, gcwObj.uuid
