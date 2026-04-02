
from django.conf import settings
from account.models import Account
from cashier.engine import Cashier
from notifications.models import AccountNotifications
from parameters.models import VHostDomainCSS, VHostUserSideBarEntry, VHostUserMenuEntry, VHostMenuEntry, \
    VHostSideBarEntry, ThemeStyleSheet
from toolkit.vhosts import get_vhost_and_apperance
from logging import getLogger
logger = getLogger(__name__)


# context_processors/dashboard.py

def dashboard_context(request):
    if not getattr(request, "account", None):
        return {}

    account = request.account
    vhost = request.vhost
    vdomain = request.vdomain

    notifications = AccountNotifications.objects.filter(
        account=account,
        active=True,
        seen_at__isnull=True
    ).count()

    cashier = Cashier(vhost, account)

    return {
        "account": account,
        "vhost": vhost,
        "vdomain": vdomain,
        "apperance": request.appearance,

        "current_balance": cashier.get_balance(),
        "pending_balance": cashier.get_at_risk_balance(),
        "available_balance": cashier.get_available_balance(),

        "current_notifications": notifications,
        "FONT_AWESOME_KIT": settings.FONT_AWESOME_KIT,
        "SKIP_ACCT_BALANCE": True,
        "MINERVE_BODY_THEME": "dark",
        "is_fiat": False,

        "no_timeout": (
            request.GET.get("__notimeout")
            or request.user.is_superuser
        ),
    }

def get_dashboard_menus(request, app_mode=None):
    if not request.account:
        return {}, []

    qwa = {
        "vhost": request.vhost,
        "domains__in": [request.vdomain],
        "active": True,
    }

    if app_mode:
        qwa["app_mode"] = app_mode
    else:
        qwa["app_mode__isnull"] = True

    top_menu = list(
        VHostUserMenuEntry.objects.filter(**qwa).order_by("ordering_key")
    )

    side_menu = []
    lang = request.account.locale.lang if request.account.locale else None

    for side in VHostUserSideBarEntry.objects.filter(**qwa).order_by("ordering_key"):
        side_menu.append({
            "icon": side.icon,
            "on_click": side.on_click,
            "url": side.url,
            "ordering_key": side.ordering_key,
            "help_text": side.help_text,
            "name": side.name,
            "submenu_entries": side.get_submenus(app_mode, False, lang),
        })

    return top_menu, side_menu

