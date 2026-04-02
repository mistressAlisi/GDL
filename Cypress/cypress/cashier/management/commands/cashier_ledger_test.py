from django.core.management.base import BaseCommand
from tabulate import tabulate
from collections import defaultdict

from account.models import Account
from cashier.models import AccountBalanceLedgerTX, AccountBalance
from parameters.models import VHost
from django.db.models import Sum, Value, CharField, Case, When, Subquery, OuterRef
from django.db.models.functions import TruncDate, ExtractWeekDay

from wager.models import Wager


class Command(BaseCommand):
    help = 'Ledger Tests'

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument("-a", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        account_filter = {}
        if options.get("a"):
            accountObj = Account.objects.get(acctnum=options["a"][0])
            account_filter["parent__account"] = accountObj
        # 🧮 Aggregate transactions by day and account
        qs = (
            AccountBalanceLedgerTX.objects
            .filter(vhost=vHost, **account_filter)
            .annotate(day=TruncDate('created'))
            .annotate(weekday=ExtractWeekDay('created'))
            .annotate(
                day_name=Case(
                    When(weekday=1, then=Value('Sunday')),
                    When(weekday=2, then=Value('Monday')),
                    When(weekday=3, then=Value('Tuesday')),
                    When(weekday=4, then=Value('Wednesday')),
                    When(weekday=5, then=Value('Thursday')),
                    When(weekday=6, then=Value('Friday')),
                    When(weekday=7, then=Value('Saturday')),
                    output_field=CharField()
                )
            )
            .values('parent__account__acctnum', 'day', 'day_name')
            .annotate(
                total_fees_change=Sum('fees_change'),
                total_processor_fees=Sum('processor_fees'),
                total_avail_change=Sum('avail_change'),
                total_win_change=Sum('win_change'),
                total_deposit_change=Sum('deposit_change'),
                total_rollover_change=Sum('rollover_change'),
                total_withdrawable_change=Sum('withdrawable_change'),
                total_pending_deposit_change=Sum('pending_deposit_change'),
                total_pending_rollover_change=Sum('pending_rollover_change'),
                total_pending_withdraw_change=Sum('pending_withdraw_change'),
                total_at_risk_change=Sum('at_risk_change'),
                pending_wagers=Subquery(
                    Wager.objects
                    .filter(
                        account=OuterRef('parent__account'),
                        created__date=OuterRef('day'),
                        status__in=['P', 'M'],
                        grade_outcome__isnull=True
                    )
                    .values('account')  # group by account
                    .annotate(pending_sum=Sum('risk'))
                    .values('pending_sum')[:1]
                )
            )
            .order_by('parent__account__acctnum', 'day')
        )

        # 🏦 Get starting balances per account (optional, defaults to 0)
        running_balances = defaultdict(lambda: 0)
        # for acct in AccountBalance.objects.filter(vhost=vHost):
        #     running_balances[acct.account.acctnum] = float(acct.available_balance)

        self.stdout.write(f">>> Ledger Summary:")

        ledger_table = []
        for q in qs:
            acct = q["parent__account__acctnum"]
            start_balance = running_balances[acct]

            deposits = float(q["total_deposit_change"] or 0)
            wagers = float(q["total_at_risk_change"] or 0)
            wins = float(q["total_win_change"] or 0)
            fees = float(q["total_fees_change"] or 0)
            pending_wagers = float(q["pending_wagers"] or 0)
            withdrawable_change = float(q["total_withdrawable_change"] or 0)
            bonus = 0

            # Calculate end balance
            day_net = (deposits + wins+  bonus) - (wagers + fees + pending_wagers)
            end_balance = start_balance + day_net

            ledger_table.append([
                acct,
                q["day"],
                q["day_name"],
                round(start_balance, 2),
                round(deposits, 2),
                round(withdrawable_change, 2),
                round(bonus,2),
                round(fees, 2),
                round(wins-wagers, 2),
                round(end_balance, 2),
                round(pending_wagers, 2),
                round(end_balance, 2),
            ])

            # Update running balance
            running_balances[acct] = end_balance

        self.stdout.write(
            tabulate(
                ledger_table,
                headers=[
                    "Account",
                    "Date",
                    "Day",
                    "Starting Bal",
                    "Deposits",
                    "Withdrawals",
                    "Bonuses",
                    "Fees",
                    "W/L",
                    "Ending Balance",
                    "Pending Wagers",
                    "Available Bal",
                ],
                tablefmt="grid",
            )
        )

        self.stdout.write(
            "<><>**<><>**<><>**<><>**<><>**<><>**<><>**<><>**<><>**<><>"
        )
