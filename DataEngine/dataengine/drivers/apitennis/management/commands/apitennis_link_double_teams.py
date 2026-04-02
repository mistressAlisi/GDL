import asyncio
import logging
import re
import unicodedata

from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.db.models import Func, F, CharField

from dataengine.drivers.apitennis.models.players import Players
from dataengine.models import TeamSyncStatus
from parameters.models import VHost

from dataengine.drivers.apisports.driver.daemons.apisporthttpd import APISportsHTTPd
from teams.models import Team


def shorten_first_name(full_name: str) -> str:
    if not full_name:
        return full_name

    # Normalize once
    name = unicodedata.normalize("NFC", full_name.strip())
    name = re.sub(r'\s+', ' ', name)

    # ---- NEW: handle doubles teams "X Y / A B" ----
    if "/" in name:
        left, right = [part.strip() for part in name.split("/", 1)]

        # Each side: surname = last word
        left_surname = left.split(" ")[-1].title()
        right_surname = right.split(" ")[-1].title()

        # Format: Surname1/ Surname2   (NOTE: ONE space after slash)
        retr = f"{left_surname}/ {right_surname}"
        # print(f"Double trouble {retr}")
        return retr

    # ---- ORIGINAL logic (with accents, apostrophes, hyphens) ----
    name = name.title()
    word = r"[A-Za-zÀ-ÖØ-öø-ÿ'-]+"

    # First Second Last → F. S. Last
    if re.match(fr"^{word} {word} {word}$", name):
        return re.sub(
            fr"^({word}) ({word}) ({word})$",
            lambda m: f"{m.group(1)[0]}. {m.group(2)[0]}. {m.group(3)}",
            name
        )

    # First Last → F. Last
    elif re.match(fr"^{word} {word}$", name):
        return re.sub(
            fr"^({word}) ({word})$",
            lambda m: f"{m.group(1)[0]}. {m.group(2)}",
            name
        )

    return name

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
        sys_teams = Team.objects.filter(vhost=vHost,name__contains="/")
        subquery = TeamSyncStatus.objects.filter(
            driver_object_type="apitennis.players.Player",
        ).values("pk")

        for team in sys_teams:
            playerObj = False
            shortened_name = shorten_first_name(team.name)
            try:
                playerObj = Players.objects.get(vhost=vHost,player_name=shortened_name)
            except Players.DoesNotExist:
                playerObj = False
            except MultipleObjectsReturned:
                playerObj = False
            if playerObj:
                print(f"Api Player: {playerObj}... Refers to {team.name}...linking!")
                ntso = TeamSyncStatus(driver_object_type="apitennis.players.Player", driver_object_uuid=playerObj.uuid,
                                      system_object_type="team", system_object_uuid=team.uuid, team=team)
                ntso.save()




