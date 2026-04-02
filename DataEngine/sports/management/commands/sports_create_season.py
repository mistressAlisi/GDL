from django.core.management.base import BaseCommand

from sports.models import Season


class Command(BaseCommand):
    help = 'Creates a Season in the Sports Database and mark it active'
    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(f"Creating Season {options['year']}"))
        Season.objects.all().update(active=False)
        season = Season.objects.get_or_create(season_key=options['year'],active=True)[0]
        season.save()
