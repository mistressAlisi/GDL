"""
RAF (Refer-A-Friend) Signal Handler

Handles the automatic RAF reward when a referred player makes their first deposit.
"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.dispatch import receiver
from django.db.models import Sum
from django.utils.timezone import now

from cashier.signals.balances import signal_deposit_confirmed

log = logging.getLogger(__name__)


@receiver(signal_deposit_confirmed)
def handle_raf_reward(sender, account, deposit_amount, processor_tx=None, **kwargs):
    """
    When a referred player makes their FIRST deposit,
    credit a percentage (default 50%) to referrer's bonus balance.

    Args:
        sender: The Cashier instance
        account: The account that made the deposit
        deposit_amount: The deposit amount
        processor_tx: The processor transaction object
    """
    from cashier.models import AccountReferralCodeTracker, RAFConfiguration, RAFRewardTracker
    from cashier.engine import Cashier

    log.info(f"RAF handler: Checking deposit for account {account.uuid}, amount: {deposit_amount}")

    # 1. Check if this account was referred and hasn't had RAF processed yet
    try:
        referral = AccountReferralCodeTracker.objects.filter(
            new_player=account,
            first_deposit_processed=False
        ).first()
    except Exception as e:
        log.error(f"RAF: Error checking referral: {e}")
        return

    if not referral:
        log.debug(f"RAF: No unprocessed referral found for account {account.uuid}")
        return

    log.info(f"RAF: Found referral - referrer: {referral.referrer.uuid}, referred: {account.uuid}")

    # 2. Get RAF configuration for this vhost/vdomain
    try:
        # Try domain-specific config first, then vhost-level
        config = RAFConfiguration.objects.filter(
            vhost=account.vhost,
            vdomain=account.domain,
            is_active=True
        ).first()

        if not config:
            config = RAFConfiguration.objects.filter(
                vhost=account.vhost,
                vdomain__isnull=True,
                is_active=True
            ).first()

        if not config:
            log.warning(f"RAF: No active configuration found for vhost {account.vhost}")
            return
    except RAFConfiguration.DoesNotExist:
        log.warning(f"RAF: No configuration found for vhost {account.vhost}")
        return

    # 3. Calculate reward (percentage of deposit, capped at max per referral)
    reward = Decimal(str(deposit_amount)) * (config.reward_percentage / Decimal('100'))
    reward = min(reward, config.max_reward_per_referral)

    log.info(f"RAF: Calculated reward: ${reward} ({config.reward_percentage}% of ${deposit_amount})")

    # 4. Check monthly cap for referrer
    month_start = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_total = RAFRewardTracker.objects.filter(
        referrer=referral.referrer,
        created_at__gte=month_start,
        is_paid=True
    ).aggregate(Sum('reward_amount'))['reward_amount__sum'] or Decimal('0')

    remaining_monthly = config.max_reward_per_month - monthly_total
    if remaining_monthly <= 0:
        log.info(f"RAF: Referrer {referral.referrer.uuid} has hit monthly cap of ${config.max_reward_per_month}")
        # Still mark as processed so we don't try again
        referral.first_deposit_processed = True
        referral.first_deposit_amount = deposit_amount
        referral.save()
        return

    reward = min(reward, remaining_monthly)

    if reward <= 0:
        log.info(f"RAF: Calculated reward is 0, skipping")
        referral.first_deposit_processed = True
        referral.first_deposit_amount = deposit_amount
        referral.save()
        return

    # 5. Credit referrer's bonus balance
    try:
        referrer_cashier = Cashier(vhost=account.vhost, account=referral.referrer)
        success, ledger_tx = referrer_cashier.credit_bonus(
            amount=reward,
            bonus_type="RAF_REWARD",
            rollover=config.rollover_multiplier,
            expiry_days=config.reward_expiry_days
        )

        if not success:
            log.error(f"RAF: Failed to credit bonus to referrer {referral.referrer.uuid}")
            return

        log.info(f"RAF: Successfully credited ${reward} to referrer {referral.referrer.uuid}")

    except Exception as e:
        log.exception(f"RAF: Error crediting bonus: {e}")
        return

    # 6. Update referral tracker
    referral.first_deposit_processed = True
    referral.first_deposit_amount = deposit_amount
    referral.reward_amount = reward
    referral.reward_paid_at = now()
    referral.save()

    # 7. Create RAF reward record
    RAFRewardTracker.objects.create(
        vhost=account.vhost,
        vdomain=account.domain,
        referrer=referral.referrer,
        referred=account,
        referral_tracker=referral,
        deposit_amount=deposit_amount,
        reward_amount=reward,
        expires_at=now() + timedelta(days=config.reward_expiry_days),
        is_paid=True,
        paid_at=now()
    )

    log.info(
        f"RAF: Complete - Referrer {referral.referrer.acctname} received ${reward} "
        f"for referred player {account.acctname}'s deposit of ${deposit_amount}"
    )
