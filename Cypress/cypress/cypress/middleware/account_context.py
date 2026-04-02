# middleware/account_context.py
from django.http import Http404
from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin

from account.models import Account
from management.models import Manager
from parameters.models import VHostDomain


class AccountContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.vdomain = None
        request.vhost = None
        request.account = None
        request.manager = None

        host = request.get_host().split(":")[0]

        # --- 1. Resolve domain (ALWAYS) ---
        try:
            vdomain = VHostDomain.objects.select_related("vhost").get(
                domain_fqdn=host
            )
        except VHostDomain.DoesNotExist:
            raise Http404(f"No VHost configured for host: {host}")

        request.vdomain = vdomain
        request.vhost = vdomain.vhost

        # --- 2. Account context (OPTIONAL) ---
        account_id = request.session.get("account_id")
        if not account_id:
            return

        try:
            account = Account.objects.select_related(
                "locale", "timezone", "system_theme"
            ).get(
                uuid=account_id,
                vhost=request.vhost,
            )
        except Account.DoesNotExist:
            return

        request.account = account

        # Locale
        if account.locale:
            translation.activate(str(account.locale.lang))

        # Timezone
        if account.timezone:
            timezone.activate(account.timezone.timezone)

        # --- 3. Manager context (OPTIONAL) ---
        manager_id = request.session.get("management")
        if manager_id:
            try:
                request.manager = Manager.objects.get(
                    uuid=manager_id,
                    vhost=request.vhost,
                )
            except Manager.DoesNotExist:
                pass
