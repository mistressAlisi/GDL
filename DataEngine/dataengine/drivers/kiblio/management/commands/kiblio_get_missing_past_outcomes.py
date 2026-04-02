import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.drivers.kiblio.api.http import KiblHttpAPI
from dataengine.drivers.kiblio.models import Fixture
from dataengine.engine import DataEngine
from dataengine.models import DataEngineVHostConfig, MatchSyncStatus
from matches.models import Match
from parameters.models import VHost


class Command(BaseCommand):
    help = "Find Matches without finished status that need outcomes fixed."

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument("-l", type=str, nargs="+")

    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"KIBL.io: Fetching Outcomes for Past Fixtures with no data for {vHost}"
            )
        )

        matchObjs = Match.objects.filter(
            vhost=vHost,
            commence_time__lte=now(),
            finished=False,
            wagers_paid=False,
        )
        total_matches = matchObjs.count()

        api = KiblHttpAPI(vHost)
        dataEngine = DataEngine(vHost)
        dataEngine._load_driver(
            DataEngineVHostConfig.objects.get(
                vhost=vHost,
                active=True,
                driver__class_name="dataengine.drivers.kiblio",
            ).driver
        )

        self.stdout.write(
            self.style.MIGRATE_LABEL(f"KIBL.io: Found {total_matches} Matches to process...")
        )

        # Processing function for a single match
        def process_match(match):
            try:
                try:
                    mssObj = MatchSyncStatus.objects.get(match=match)
                except MatchSyncStatus.MultipleObjectsReturned:
                    _mssObj = MatchSyncStatus.objects.filter(match=match)
                    mssObj = _mssObj[0]
                    for _ms in _mssObj[1:]:
                        _ms.delete()

                fixtureObj = None
                try:
                    fixtureObj = Fixture.objects.get(uuid=mssObj.driver_object_uuid)
                    outcomes = api.fetch_fixture_outcomes(fixture=fixtureObj)
                    logging.info(f"Match {match.uuid}: Outcomes = {outcomes}")
                except Fixture.DoesNotExist:
                    logging.warning(f"Fixture {mssObj.driver_object_uuid} does not exist")

                # Mark as finished
                match.finished = True
                match.finished_at = now()
                match.status_short = "SYNC"
                match.status_long = "Outcomes Synced."
                match.save()

                # Sync outcomes if fixture exists
                if fixtureObj:
                    dataEngine.sync_outcomes(True, provider_match_objs=[fixtureObj])

                return f"✅ Processed match {match.uuid}"

            except Exception as e:
                logging.exception(f"❌ Error processing match {match.uuid}: {e}")
                return f"❌ Error processing match {match.uuid}: {e}"

        # Run with ThreadPoolExecutor, limited by CPU cores
        max_workers = cpu_count()
        self.stdout.write(self.style.MIGRATE_LABEL(f"Running with {max_workers} workers..."))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_match = {executor.submit(process_match, match): match for match in matchObjs}

            for future in as_completed(future_to_match):
                msg = future.result()
                self.stdout.write(msg)

        self.stdout.write(self.style.SUCCESS("All matches processed."))
