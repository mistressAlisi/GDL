import base64
import logging
import asyncio

from django.core.management import BaseCommand

from dataengine.consensus.daemon.match import AsyncMatchLinkDaemon

from parameters.models import VHost, VHostParameterRegistry


class Command(BaseCommand):
    help = 'DataEngine Tool to set Winner Publisher API parameters.'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument("api_endpoint", type=str, nargs="+")
        parser.add_argument("api_key", type=str, nargs="+")
        parser.add_argument("api_secret", type=str, nargs="+")


    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"DataEngine Winner Publishers Configuration for {vHost}"
            )
        )
        vHost = VHost.objects.get(pk=options["vhost"][0])
        parameters, c = VHostParameterRegistry.objects.get_or_create(vhost=vHost, name="api_keys",
                                                                     application="dataengine.publisher.winners")
        api_key = base64.b64decode(options["api_secret"][0])
        parameters.value_text = options["api_key"][0]
        parameters.value_bin = api_key
        parameters.save()
        parameters, c = VHostParameterRegistry.objects.get_or_create(vhost=vHost, name="url",
                                                                     application="dataengine.publisher.winners")
        parameters.value_text = options["api_endpoint"][0]
        parameters.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"DataEngine Winner Publishers Configuration for {vHost} Saved!"
            )
        )

