# cypress/views/bootstrap.py
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET

from cashier.engine import Cashier
from notifications.models import AccountNotifications


@ensure_csrf_cookie
@require_GET
def gibootstrap_handler(request):
    vhost = request.vhost
    vdomain = request.vdomain
    account = request.account
    manager = request.manager
    # print(f"Bootstrap request: {request.vhost}")
    if vdomain.website_icon:
        icon_url = vdomain.website_icon.url
    else:
        icon_url = None
    # --- Base response (always present) ---
    data = {
        "vhost": {
            "uuid": str(vhost.uuid),
            "name": vhost.name,
        },
        "domain": {
            "fqdn": vdomain.domain_fqdn,
            "name": vdomain.website_name,
            "icon": icon_url,
            "uuid": str(vdomain.uuid),
        },
        "features": {
            # # example flags – adjust to your schema
            # "cashier": vhost.enable_cashier,
            # "kyc": vhost.enable_kyc,
            # "withdrawals": vhost.enable_withdrawals,
        },
        "appearance": {
            "theme": vdomain.theme.uuid if vdomain.theme else None,
        },
        "session": {
            "authenticated": bool(account),
            "is_manager": bool(manager),
        },
    }

    # --- Account context (optional) ---
    if account:
        cashier = Cashier(vhost=request.vhost, account=account)
        # print(cashier)
        balances = {
            "latest_balance": cashier.get_balance(),
            "latest_bonus": cashier.get_available_bonus(),
            "pending": cashier.get_at_risk_balance(),
            "available": cashier.get_available_balance() + cashier.get_available_bonus()
        }
        notifications = AccountNotifications.objects.filter(account=account,seen_at__isnull=True).count()
        data["account"] = {
            "uuid": str(account.uuid),
            "acctname": account.acctname,
            "acctnum":account.acctnum,
            "pronouns": account.pronouns,
            "balances": balances,
            "locale": str(account.locale.lang) if account.locale else None,
            "timezone": account.timezone.timezone if account.timezone else None,
            "message_count":notifications,
        }
        if account.avatar:
            data["account"]["avatar"] = account.avatar.url
        # --- Available payment providers ---

        deposit_providers = cashier.get_available_deposit_providers(vdomain)
        withdrawal_providers = cashier.get_available_withdrawal_providers(vdomain)

        data["providers"] = {
            "deposit": [
                {
                    "module": p.payment_provider.module_name,
                    "name": p.payment_provider.name,
                    "min": float(p.payment_provider.dep_min),
                    "max": float(p.payment_provider.dep_max),
                    "fees": float(p.payment_provider.dep_fees),
                }
                for p in deposit_providers
            ],
            "withdrawal": [
                {
                    "module": p.payment_provider.module_name,
                    "name": p.payment_provider.name,
                    "min": float(p.payment_provider.wdl_min),
                    "max": float(p.payment_provider.wdl_max),
                    "fees": float(p.payment_provider.wdl_fees),
                }
                for p in withdrawal_providers
            ],
        }

    # --- Manager context (optional) ---
    if manager:
        data["manager"] = {
            "uuid": str(manager.uuid),
            "role": manager.role,
        }

    return JsonResponse(data)
