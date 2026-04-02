from django.core.management.base import BaseCommand

from teams.models import Team


class Command(BaseCommand):
    help = 'Load Team logos from the MEDIA_ROOT and sync it with the database'
    card_path = ""

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(f"Fixing teams with no names."))
        teams = Team.objects.filter(name="")
        for team in teams:
            name = team.key.replace("-"," ").capitalize()
            team.name = name
            team.save()
            self.stdout.write(self.style.SUCCESS(f"Team {team.key}->{name} has been fixed"))










