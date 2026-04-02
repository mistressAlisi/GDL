from django.core.management.base import BaseCommand

from matches.tasks import close_and_score_match


class Command(BaseCommand):
    help = 'Close all stale and finished matches.'

    def handle(self, *args, **options):
        muuid = "b9e1252c-fe2a-44a6-a9bd-fef3851aaefa"
        self.stdout.write(self.style.MIGRATE_HEADING(f"Close Match:{muuid}"))
        close_and_score_match(muuid)