import json
from uuid import UUID

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.text import slugify

from parameters.models import VHost, VHostParameterRegistry
from providers.apisports.models import League,CoreSportMap
from dataengine.drivers.kiblio.api.http import KiblHttpAPI
from sports.models import Sport
from providers.apisports.tasks import amf, bab, base, fball


class Command(BaseCommand):
    help = 'KBL.io set user/password'


    def add_arguments(self, parser):
        parser.add_argument("vhost",nargs='+', type=UUID,help="VHost to work on.")
        parser.add_argument("user", nargs='+', type=str, help="Set KIBL username to")
        parser.add_argument("password", nargs='+', type=str, help="SET KIBL password to.")
        parser.add_argument("clientid", nargs='+', type=str, help="SET KIBL client id to.")


    def handle(self, *args, **options):
        vhost = VHost.objects.get(uuid=options['vhost'][0])
        self.stdout.write(self.style.MIGRATE_HEADING(f"Working on VHost {vhost}"))
        vpr = VHostParameterRegistry.objects.get_or_create(vhost=vhost, application="dataengine.drivers.kiblio", name="username")[0]
        vpr.value_text = options['user'][0]
        vpr.save()
        vpr = \
        VHostParameterRegistry.objects.get_or_create(vhost=vhost, application="dataengine.drivers.kiblio", name="password")[0]
        vpr.value_text = options['password'][0]
        vpr.save()
        vpr = \
        VHostParameterRegistry.objects.get_or_create(vhost=vhost, application="dataengine.drivers.kiblio", name="clientid")[0]
        vpr.value_text = options['clientid'][0]
        vpr.save()
        self.stdout.write(self.style.SUCCESS(f"Set KIBL user, password and clientid."))

