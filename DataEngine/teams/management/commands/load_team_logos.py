import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from teams.models import Team


class Command(BaseCommand):
    help = 'Load Team logos from the MEDIA_ROOT and sync it with the database'
    card_path = ""

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(f"Synchronising Teams with no logos - assigning best fit from media storage!"))
        teams = Team.objects.all()

        self.card_path = settings.MEDIA_ROOT + "teams/cards"
        if os.path.exists(self.card_path):
            card_logos = os.listdir(self.card_path)
            for team in teams:
                 file_name = team.key.lower().replace("-","_")
                 for logo in card_logos:
                     if logo.lower().startswith(file_name):
                         self.stdout.write(self.style.MIGRATE_HEADING(f"Found {logo} for Team {team.name}..."))
                         with connection.cursor() as cursor:
                             cursor.execute("UPDATE teams_team SET card_logo = %s WHERE uuid = %s",[f"teams/cards/{logo}",team.uuid])
                             cursor.close()
                         break

            self.card_path = settings.MEDIA_ROOT + "teams/large"
            if os.path.exists(self.card_path):
                card_logos = os.listdir(self.card_path)
                for team in teams:
                    file_name = team.key.lower().replace("-", "_")
                    for logo in card_logos:
                        if logo.lower().startswith(file_name):
                            self.stdout.write(self.style.MIGRATE_HEADING(f"Found {logo} for Team {team.name}..."))
                            with connection.cursor() as cursor:
                                cursor.execute("UPDATE teams_team SET large_logo = %s WHERE uuid = %s", [f"teams/large/{logo}", team.uuid])
                                cursor.close()
                            break









