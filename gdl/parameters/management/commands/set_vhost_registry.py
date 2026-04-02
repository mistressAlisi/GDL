import tablib
from django.core.management.base import BaseCommand

from parameters.models import VHost, VHostMenuEntry, VHostParameterRegistry


class Command(BaseCommand):
    help = 'Set the given key in the registry for the VHost  and application to the given value'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("application", type=str, nargs="+")
        parser.add_argument("name", type=str, nargs="+")
        parser.add_argument("value", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        parameter = VHostParameterRegistry.objects.get_or_create(vhost=vHost,application=options["application"][0],name=options["name"][0])[0]
        parameter.value_bin = None
        parameter.value_json = None
        parameter.value_int = None
        parameter.application = options["application"][0]
        parameter.value_text = options['value'][0]
        parameter.save()
        self.stdout.write(self.style.SUCCESS(f'Parameter {options["application"][0]} - {options["name"][0]} for Virtual Host: {vHost.name} - set.'))



