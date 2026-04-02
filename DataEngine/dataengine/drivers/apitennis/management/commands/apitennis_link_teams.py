import asyncio
import logging

from django.core.management.base import BaseCommand
from django.db.models import Func, F, CharField

from dataengine.drivers.apitennis.models.players import Players
from dataengine.models import TeamSyncStatus
from parameters.models import VHost

from dataengine.drivers.apisports.driver.daemons.apisporthttpd import APISportsHTTPd
from teams.models import Team


class ApiTennisStyleName(Func):
    function = 'regexp_replace'
    template = (
        # if two given names, produce "F. S. Last"
        "CASE "
        "WHEN %(expressions)s ~ '^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$' "
        "THEN regexp_replace(%(expressions)s, "
        "E'^([A-Z])[a-z]+ ([A-Z])[a-z]+ ([A-Z][a-z]+)$', "
        "'\\1. \\2. \\3') "
        # else (one given name + surname): "F. Last"
        "WHEN %(expressions)s ~ '^[A-Z][a-z]+ [A-Z][a-z]+$' "
        "THEN regexp_replace(%(expressions)s, "
        "E'^([A-Z])[a-z]+ ([A-Z][a-z]+)$', "
        "'\\1. \\2') "
        "ELSE %(expressions)s END"
    )
    output_field = CharField()


class Command(BaseCommand):
    help = 'APITennis: Start the Async Updater Daemon'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Getting Fixtures!'))
        vHost = VHost.objects.get(pk=options["vhost"][0])
        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO,force=True)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG,force=True)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING,force=True)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR,force=True)
        sys_teams = Team.objects.filter(vhost=vHost).annotate(
            short_name=ApiTennisStyleName(F('name'))
        )
        subquery = TeamSyncStatus.objects.filter(
            driver_object_type="apitennis.players.Player",
        ).values("pk")
        api_players = Players.objects.filter(vhost=vHost)
        for api_player in api_players:
            tss = False
            try:
                tss = TeamSyncStatus.objects.get(driver_object_type="apitennis.players.Player",driver_object_uuid=api_player.uuid)
            except TeamSyncStatus.DoesNotExist:
                tss = False
            except TeamSyncStatus.MultipleObjectsReturned:
                _tss = TeamSyncStatus.objects.filter(driver_object_type="apitennis.players.Player",
                                                 driver_object_uuid=api_player.uuid)
                tss = _tss.first()
                for t in _tss[1:]:
                    t.delete()
                print(f"Api Player {api_player}: Multiple TSS objects.")

            if tss:
                print(f"Api Player: {api_player}... Linked by {tss.uuid}")
            if not tss:
                print(f"Api Player: {api_player}... Not Linked... Searching...")
                sto = sys_teams.filter(short_name__icontains=api_player.player_name)
                if (len(sto)==1):
                    print(f"Api Player: {api_player}... Refers to {sto[0].name}...linking!")
                    ntso = TeamSyncStatus(driver_object_type="apitennis.players.Player",driver_object_uuid=api_player.uuid,system_object_type="team",system_object_uuid=sto[0].uuid,team=sto[0])
                    ntso.save()
                elif (len(sto)>1):
                    print(f"Api Player: {api_player}... Multiple teams found!")
                    print(sto)



