import asyncio
import datetime
import logging
from decimal import Decimal

from time import localtime
from types import SimpleNamespace

from asgiref.sync import sync_to_async
from celery.fixups.django import fixup

from pydantic import ValidationError

from asynctools.abc import AsyncWorkerABC



class GoalServeD(AsyncWorkerABC):
    url_root = "https://www.goalserve.com/getfeed/8015a863314c4c5ff1b808de315f0ca1"
    regappid = "dataengine.drivers.goalserve"
    last_timestamp = False
    verbose = False
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.goalserve.models import SportCategory, SoccerFixture, Team, SoccerFixtureScore, \
            SoccerEvent, \
            BasketBallFixture, BasketBallScore, TennisFixture, TennisScore, HockeyFixture, HockeyEvent, \
            HockeyFixtureScore, \
            AmericanFBallFixture, AmericanFBallScore
        from dataengine.drivers.goalserve.models.baseball import BaseBallScore, BaseBallFixture

        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            SportCategory=SportCategory,
            SoccerFixture=SoccerFixture,
            Team=Team,
            SoccerFixtureScore=SoccerFixtureScore,
            SoccerEvent=SoccerEvent,
            BasketBallFixture=BasketBallFixture,
            BasketBallScore=BasketBallScore,
            TennisFixture=TennisFixture,
            TennisScore=TennisScore,
            HockeyFixture=HockeyFixture,
            HockeyEvent=HockeyEvent,
            HockeyFixtureScore=HockeyFixtureScore,
            AmericanFBallFixture=AmericanFBallFixture,
            AmericanFBallScore=AmericanFBallScore,
            BaseBallScore=BaseBallScore,
            BaseBallFixture=BaseBallFixture

        )

        self.logger.debug("APITennisAsyncDaemon: Django models bound in child")
    def __init__(self, vhost = object ,logger = object, name: str = "worker", interval: float = 60,run_in_process: bool = True,loki_url=None,):
        if logger is None or not isinstance(logger, logging.Logger):
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
        AsyncWorkerABC.__init__(self,vhost, logger, name, interval,run_in_process,loki_url)

    async def _get_team(self,id,name):
        try:
            team, cc = await sync_to_async(lambda: self.models.Team.objects.using("default").get_or_create(vhost=self.vhost,name=name,id=int(id)),thread_sensitive=False)()
            if cc:
                await sync_to_async(team.save, thread_sensitive=False)()
        except self.models.Team.MultipleObjectsReturned:
            team = await sync_to_async(lambda: self.models.Team.objects.using("default").filter(vhost=self.vhost, name=name, id=int(id)).first(),
                                           thread_sensitive=False)()
        return team


    async def process_soccer_fixture(self,fixture_data,catObj):
        if self.verbose:
            self.logger.info(f"Processing Soccer Fixture {fixture_data['@fix_id']}...")
        if fixture_data['localteam']['@id'] != "" and fixture_data['visitorteam']['@id'] !="":
            home_team = await self._get_team(fixture_data['localteam']["@id"],fixture_data['localteam']["@name"])
            away_team = await self._get_team(fixture_data['visitorteam']["@id"], fixture_data['visitorteam']["@name"])
            if fixture_data["@static_id"] != "" and fixture_data["@fix_id"] != "":
                try:
                    fixtureObj,cc = await sync_to_async(lambda:self.models.SoccerFixture.objects.using("default").get_or_create(vhost=self.vhost,category=catObj,
                                                                                                   static_id=fixture_data["@static_id"],
                                                                                                   fixture_id=fixture_data["@fix_id"],
                                                                                                   home_team=home_team,away_team=away_team,
                                                                                                   date=datetime.datetime.strptime(fixture_data["@formatted_date"],"%d.%m.%Y")),thread_sensitive=False)()
                    if cc:
                        # fixtureObj.date = fixture_data["@date"]
                        fixtureObj.venu = fixture_data["@venue"]
                except self.models.SoccerFixture.MultipleObjectsReturned:
                    fixtureObj = await sync_to_async(
                        lambda: self.models.SoccerFixture.objects.using("default").filter(vhost=self.vhost, category=catObj,
                                                                    static_id=fixture_data["@static_id"],
                                                                    fixture_id=fixture_data["@fix_id"],
                                                                    home_team=home_team, away_team=away_team,
                                                                    date=datetime.datetime.strptime(
                                                                        fixture_data["@formatted_date"], "%d.%m.%Y")).first(),
                        thread_sensitive=False)()
                if "@intj_time" in fixture_data:
                    fixtureObj.intj_time = fixture_data["@intj_time"]
                if "@intj_minute" in fixture_data:
                    fixtureObj.intj_minute = fixture_data["@intj_minute"]
                fixtureObj.status = fixture_data["@status"]
                fixtureObj.time = fixture_data["@time"]
                if "PM" in fixtureObj.time or "AM" in fixtureObj.time:
                    cto = datetime.datetime.strptime(f"{fixture_data["@formatted_date"]} {fixture_data["@time"]}",
                                                     "%d.%m.%Y %I:%M %p").replace(tzinfo=datetime.timezone.utc)
                else:
                    cto = datetime.datetime.strptime(f"{fixture_data["@formatted_date"]} {fixture_data["@time"]}",
                                                     "%d.%m.%Y %H:%M").replace(tzinfo=datetime.timezone.utc)
                fixtureObj.commence_time = cto
                await sync_to_async(fixtureObj.save,thread_sensitive=False)()
                try:
                    home_score,_ = await sync_to_async(lambda:self.models.SoccerFixtureScore.objects.using("default").get_or_create(fixture=fixtureObj,team=home_team,vhost=self.vhost),thread_sensitive=False)()
                except self.models.SoccerFixtureScore.MultipleObjectsReturned:
                    home_score = await sync_to_async(lambda: self.models.SoccerFixtureScore.objects.using("default").filter(fixture=fixtureObj, team=home_team, vhost=self.vhost).first(), thread_sensitive=False)()
                try:
                    away_score,_ = await sync_to_async(lambda:self.models.SoccerFixtureScore.objects.using("default").get_or_create(fixture=fixtureObj,team=away_team,vhost=self.vhost),thread_sensitive=False)()
                except self.models.SoccerFixtureScore.MultipleObjectsReturned:
                    away_score = await sync_to_async(lambda: self.models.SoccerFixtureScore.objects.using("default").filter(fixture=fixtureObj, team=away_team, vhost=self.vhost).first(), thread_sensitive=False)()
                try:
                    home_score.score = int(fixture_data["localteam"]["@goals"])
                except ValueError:
                    home_score.score = 0
                try:
                    away_score.score = int(fixture_data["visitorteam"]["@goals"])
                except ValueError:
                    away_score.score = 0
                await sync_to_async(lambda:home_team.save(),thread_sensitive=False)()
                await sync_to_async(lambda:away_team.save(),thread_sensitive=False)()
                await sync_to_async(lambda:home_score.save(), thread_sensitive=False)()
                await sync_to_async(lambda:away_score.save(), thread_sensitive=False)()
                if "events" in fixture_data and fixture_data["events"] != None:
                    if "event" in fixture_data["events"]:
                        for ev in list(fixture_data["events"]["event"]):
                            if type(ev) == dict:
                                if ev["@team"] == "visitorteam":
                                    eteam = away_team
                                else:
                                    eteam = home_team
                                try:
                                    evObj, _ = await sync_to_async(
                                        lambda: self.models.SoccerEvent.objects.using("default").get_or_create(vhost=self.vhost, fixture=fixtureObj, type=ev["@type"],
                                                                                  team=eteam,
                                                                                  event_id=int(ev["@eventid"])), thread_sensitive=False)()
                                except self.models.SoccerEvent.MultipleObjectsReturned:
                                    evObj = await sync_to_async(
                                        lambda: self.models.SoccerEvent.objects.using("default").filter(vhost=self.vhost, fixture=fixtureObj,
                                                                                  type=ev["@type"],
                                                                                  team=eteam,
                                                                                  event_id=int(ev["@eventid"])).first(),
                                        thread_sensitive=False)()

                                if ev["@playerId"] != "":
                                    evObj.player = ev["@player"]
                                    evObj.player_id = int(ev["@playerId"])

                                if ev["@assistid"] != "":
                                    evObj.assist_id = int(ev["@assistid"])
                                    evObj.assist = ev["@assist"]
                                evObj.minute = ev["@minute"]
                                evObj.extra_min = ev["@extra_min"]
                                evObj.result = ev["@result"]
                                await sync_to_async(evObj.save,thread_sensitive=False)()









    async def get_soccer_fixtures(self,fetch_type="home"):
        turl = self.url_root + f"/soccernew/{fetch_type}?json=1"
        data = await self._fetch_with_retry(turl)
        if data:
            json_data = data.json()
            if json_data["scores"]["@sport"] != "soccer":
                raise ValidationError(f"Feed {turl} did not provide a soccer type score result!!")
            for cat in json_data["scores"]["category"]:
                catObj,created = await sync_to_async(lambda:self.models.SportCategory.objects.using("default").get_or_create(vhost=self.vhost,gid=int(cat["@gid"] or 0),
                                                                                        name=cat["@name"],id=int(cat["@id"] or 0),
                                                                                        file_group=cat["@file_group"]),thread_sensitive=False)()
                if created:
                    if cat["@iscup"] == "True":
                        catObj.iscup = True
                if created:
                    await sync_to_async(lambda:catObj.save(),thread_sensitive=False)()
                    self.logger.info(f"Category {cat['@name']} created.")
                if "match" in cat['matches']:
                    if type(cat["matches"]["match"]) == list:
                        # tasks = [self.process_soccer_fixture(row, catObj) for row in cat["matches"]["match"]]
                        # await asyncio.gather(*tasks, return_exceptions=True)
                        await self.run_in_batches(
                            items=cat["matches"]["match"],
                            handler=lambda row: self.process_soccer_fixture(row, catObj),
                            batch_size=25,
                            label="soccer:fixtures",
                        )
                    else:
                        await self.process_soccer_fixture(cat["matches"]["match"], catObj)
            self.logger.info(f"Synced Soccer fixtures from {fetch_type}.")

    async def process_basketball_fixture(self, fixture_data, catObj):
        if self.verbose:
            self.logger.info(f"Processing Basketball Fixture {fixture_data['id']}...")
        home_team = await self._get_team(fixture_data['localteam']["id"], fixture_data['localteam']["name"])
        away_team = await self._get_team(fixture_data['awayteam']["id"], fixture_data['awayteam']["name"])

        if fixture_data["id"] != "":
            try:
                fixtureObj, cc = await sync_to_async(
                    lambda: self.models.BasketBallFixture.objects.using("default").get_or_create(vhost=self.vhost, category=catObj,
                                                                    fixture_id=fixture_data["id"],
                                                                    home_team=home_team, away_team=away_team,
                                                                    date=datetime.datetime.strptime(fixture_data["date"],
                                                                                                    "%d.%m.%Y")),
                    thread_sensitive=False)()
            except self.models.BasketBallFixture.MultipleObjectsReturned:
                fixtureObj = await sync_to_async(
                    lambda: self.models.BasketBallFixture.objects.using("default").filter(vhost=self.vhost, category=catObj,
                                                                    fixture_id=fixture_data["id"],
                                                                    home_team=home_team, away_team=away_team,
                                                                    date=datetime.datetime.strptime(fixture_data["date"],
                                                                                                    "%d.%m.%Y")).first(),
                    thread_sensitive=False)()
            # print("Ayieee")
            fixtureObj.status = fixture_data["status"]
            fixtureObj.time = fixture_data["time"]
            if "PM" in fixtureObj.time or "AM" in fixtureObj.time:
                cto = datetime.datetime.strptime(f"{fixture_data["date"]} {fixture_data["time"]}", "%d.%m.%Y %I:%M %p").replace(tzinfo=datetime.timezone.utc)
            else:
                cto = datetime.datetime.strptime(f"{fixture_data["date"]} {fixture_data["time"]}","%d.%m.%Y %H:%M").replace(tzinfo=datetime.timezone.utc)
            fixtureObj.commence_time = cto

            await sync_to_async(fixtureObj.save, thread_sensitive=False)()
            # print("reeee")
            try:
                home_score, _ = await sync_to_async(
                    lambda: self.models.BasketBallScore.objects.using("default").get_or_create(fixture=fixtureObj, team=home_team, vhost=self.vhost),
                    thread_sensitive=False)()
            except self.models.BasketBallScore.MultipleObjectsReturned:
                home_score  = await sync_to_async(
                    lambda: self.models.BasketBallScore.objects.using("default").filter(fixture=fixtureObj, team=home_team, vhost=self.vhost).first(),
                    thread_sensitive=False)()
            try:
                away_score, _ = await sync_to_async(
                    lambda: self.models.BasketBallScore.objects.using("default").get_or_create(fixture=fixtureObj, team=away_team, vhost=self.vhost),
                    thread_sensitive=False)()
            except self.models.BasketBallScore.MultipleObjectsReturned:
                away_score  = await sync_to_async(
                    lambda: self.models.BasketBallScore.objects.using("default").filter(fixture=fixtureObj, team=away_team, vhost=self.vhost).first(),
                    thread_sensitive=False)()
            for k in ["q1", "q2", "q3", "q4", "ot"]:
                # print(fixture_data["localteam"][k])
                if fixture_data["localteam"][f"{k}"] != "" and fixture_data["localteam"][f"{k}"] != "False":
                    val = int(fixture_data["localteam"][f"{k}"])
                else:
                    val = 0
                setattr(home_score, k, val)

                if fixture_data["awayteam"][f"{k}"] != "" and fixture_data["awayteam"][f"{k}"] != "False":
                    val = int(fixture_data["awayteam"][f"{k}"])
                else:
                    val = 0
                setattr(away_score, k, val)

            try:
                home_score.score = int(fixture_data["localteam"]["totalscore"])
            except ValueError:
                home_score.score = 0
            try:
                away_score.score = int(fixture_data["awayteam"]["totalscore"])
            except ValueError:
                away_score.score = 0
            await sync_to_async(lambda:home_team.save(), thread_sensitive=False)()
            await sync_to_async(lambda:away_team.save(), thread_sensitive=False)()
            await sync_to_async(lambda:home_score.save(), thread_sensitive=False)()
            await sync_to_async(lambda:away_score.save(), thread_sensitive=False)()
            if self.verbose:
                self.logger.info(f"Basketball Fixture {fixture_data['id']} - Data Synced.")

    async def get_basketball_fixtures(self,fetch_type="home"):
        turl = self.url_root + f"/bsktbl/{fetch_type}?json=1"
        data = await self._fetch_with_retry(turl)
        if data:
            json_data = data.json()
            if json_data["scores"]["sport"] != "basketball":
                raise ValidationError(f"Feed {turl} did not provide a basketball type score result!!")

            for cat in json_data["scores"]["category"]:
                if  "id" in cat and cat["id"] != "":
                    catObj,created = await sync_to_async(lambda:self.models.SportCategory.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                            name=cat["name"],id=int(cat["id"] or 0),
                                                                                            file_group=cat["file_group"]),thread_sensitive=False)()
                    if created:
                        await sync_to_async(lambda:catObj.save(),thread_sensitive=False)()
                        self.logger.info(f"Category {cat['name']} created.")
                    # print(cat)

                    if "match" in cat:
                        if type(cat["match"]) == list:
                            # tasks = [self.process_basketball_fixture(row, catObj) for row in cat["match"]]
                            # await asyncio.gather(*tasks, return_exceptions=True)
                            await self.run_in_batches(
                                items=cat["match"],
                                handler=lambda row: self.process_basketball_fixture(row, catObj),
                                batch_size=25,
                                label="basketball:fixtures",
                            )
                        else:
                            await self.process_basketball_fixture(cat["match"], catObj)
            self.logger.info(f"Synced Basketball fixtures from {fetch_type}.")


    async def process_baseball_fixture(self,fixture_data,catObj):
        if self.verbose:
            self.logger.info(f"Processing Baseball Fixture {fixture_data['@id']}...")
        home_team = await self._get_team(fixture_data['localteam']["@id"], fixture_data['localteam']["@name"])
        away_team = await self._get_team(fixture_data['awayteam']["@id"], fixture_data['awayteam']["@name"])

        if fixture_data["@id"] != "":
            try:
                fixtureObj,cc = await sync_to_async(lambda:self.models.BaseBallFixture.objects.using("default").get_or_create(vhost=self.vhost,category=catObj,
                                                                                               fixture_id=fixture_data["@id"],
                                                                                               home_team=home_team,away_team=away_team,
                                                                                               date=datetime.datetime.strptime(fixture_data["@date"],"%d.%m.%Y")),thread_sensitive=False)()
            except self.models.BaseBallFixture.MultipleObjectsReturned:
                fixtureObj = await sync_to_async(
                    lambda: self.models.BaseBallFixture.objects.using("default").filter(vhost=self.vhost, category=catObj,
                                                                  fixture_id=fixture_data["@id"],
                                                                  home_team=home_team, away_team=away_team,
                                                                  date=datetime.datetime.strptime(fixture_data["@date"],
                                                                                                  "%d.%m.%Y")).first(),thread_sensitive=False)()
            fixtureObj.status = fixture_data["@status"]
            fixtureObj.time = fixture_data["@time"]
            fixtureObj.extra_inn = fixture_data["@extra_inn"]
            if "PM" in fixtureObj.time or "AM" in fixtureObj.time:
                cto = datetime.datetime.strptime(f"{fixture_data["@date"]} {fixture_data["@time"]}", "%d.%m.%Y %I:%M %p").replace(tzinfo=datetime.timezone.utc)
            else:
                cto = datetime.datetime.strptime(f"{fixture_data["@date"]} {fixture_data["@time"]}","%d.%m.%Y %H:%M").replace(tzinfo=datetime.timezone.utc)
            fixtureObj.commence_time = cto
            await sync_to_async(fixtureObj.save,thread_sensitive=False)()
            home_score,_ = await sync_to_async(lambda:self.models.BaseBallScore.objects.using("default").get_or_create(fixture=fixtureObj,team=home_team,vhost=self.vhost),thread_sensitive=False)()
            away_score,_ = await sync_to_async(lambda:self.models.BaseBallScore.objects.using("default").get_or_create(fixture=fixtureObj,team=away_team,vhost=self.vhost),thread_sensitive=False)()
            for k in ["in1","in2","in3","in4","in5","in6","in7","in8","in9","extra","hits","errors"]:
                # print(fixture_data["player"][0][f"@{k}"])
                if fixture_data["localteam"][f"@{k}"] != "" and fixture_data["localteam"][f"@{k}"] != "False":
                    val = int(fixture_data["localteam"][f"@{k}"])
                else:
                    val = 0
                setattr(home_score, k, val)
                if fixture_data["awayteam"][f"@{k}"] != "" and fixture_data["awayteam"][f"@{k}"] != "False":
                    val = int(fixture_data["awayteam"][f"@{k}"])
                else:
                    val = 0
                setattr(away_score, k, val)

            try:
                home_score.score = int(fixture_data["localteam"]["@totalscore"])
            except ValueError:
                home_score.score = 0
            try:
                away_score.score = int(fixture_data["awayteam"]["@totalscore"])
            except ValueError:
                away_score.score = 0
            await sync_to_async(lambda:home_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:away_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:home_score.save(),thread_sensitive=False)()
            await sync_to_async(lambda:away_score.save(),thread_sensitive=False)()


    async def get_baseball_fixtures(self,fetch_type="home"):
        turl = self.url_root + f"/baseball/{fetch_type}?json=1"
        data = await self._fetch_with_retry(turl)
        if data:
            json_data = data.json()
            if json_data["scores"]["@sport"] != "baseball":
                raise ValidationError(f"Feed {turl} did not provide a baseball type score result!!")
            for cat in json_data["scores"]["category"]:
                if type(cat) == dict:
                    if "@id" in cat and cat["@id"] != "":
                        catObj,created = await sync_to_async(lambda:self.models.SportCategory.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                                name=cat["@name"],id=int(cat["@id"])),thread_sensitive=False)()
                        if created:
                            await sync_to_async(lambda:catObj.save(),thread_sensitive=False)()
                            self.logger.info(f"Category {cat['@name']} created.")
                        if "match" in cat:
                            if type(cat["match"]) == list:
                                # tasks = [self.process_baseball_fixture(row, catObj) for row in cat["match"]]
                                await self.run_in_batches(
                                    items=cat["match"],
                                    handler=lambda row: self.process_baseball_fixture(row, catObj),
                                    batch_size=25,
                                    label="baseball:fixtures",
                                )
                                # await asyncio.gather(*tasks, return_exceptions=True)
                            else:
                                await self.process_baseball_fixture(cat["match"], catObj)
            self.logger.info(f"Synced Baseball fixtures from {fetch_type}.")


    async def process_tennis_fixture(self,fixture_data,catObj):
        if self.verbose:
            self.logger.info(f"Processing Tennis Fixture {fixture_data['@id']}...")
        home_team = await self._get_team(fixture_data['player'][0]["@id"], fixture_data['player'][0]["@name"])
        away_team = await self._get_team(fixture_data['player'][1]["@id"], fixture_data['player'][1]["@name"])

        if fixture_data["@id"] != "":
            try:
                fixtureObj,cc = await sync_to_async(lambda:self.models.TennisFixture.objects.using("default").get_or_create(vhost=self.vhost,category=catObj,
                                                                                               fixture_id=fixture_data["@id"],
                                                                                               home_team=home_team,away_team=away_team,
                                                                                               date=datetime.datetime.strptime(fixture_data["@date"],"%d.%m.%Y")),thread_sensitive=False)()
            except self.models.TennisFixture.MultipleObjectsReturned:
                fixtureObj = await sync_to_async(
                    lambda: self.models.TennisFixture.objects.using("default").filter(vhost=self.vhost, category=catObj,
                                                                            fixture_id=fixture_data["@id"],
                                                                            home_team=home_team, away_team=away_team,
                                                                            date=datetime.datetime.strptime(
                                                                                fixture_data["@date"], "%d.%m.%Y")).first(),
                    thread_sensitive=False)()

            # print("Aa")
            fixtureObj.status = fixture_data["@status"]
            fixtureObj.time = fixture_data["@time"]
            if "PM" in fixtureObj.time or "AM" in fixtureObj.time:
                cto = datetime.datetime.strptime(f"{fixture_data["@date"]} {fixture_data["@time"]}", "%d.%m.%Y %I:%M %p").replace(tzinfo=datetime.timezone.utc)
            else:
                cto = datetime.datetime.strptime(f"{fixture_data["@date"]} {fixture_data["@time"]}","%d.%m.%Y %H:%M").replace(tzinfo=datetime.timezone.utc)
            fixtureObj.commence_time = cto

            if "@tb" in fixture_data:
                fixtureObj.tb = fixture_data["@tb"]


            await sync_to_async(fixtureObj.save,thread_sensitive=False)()
            try:
                home_score,_ = await sync_to_async(lambda:self.models.TennisScore.objects.using("default").get_or_create(fixture=fixtureObj,team=home_team,vhost=self.vhost),thread_sensitive=False)()
            except self.models.TennisScore.MultipleObjectsReturned:
                home_score = await sync_to_async(
                    lambda: self.models.TennisScore.objects.using("default").filter(fixture=fixtureObj,
                                                                                           team=home_team,
                                                                                           vhost=self.vhost).first(),
                    thread_sensitive=False)()
            try:
                away_score,_ = await sync_to_async(lambda:self.models.TennisScore.objects.using("default").get_or_create(fixture=fixtureObj,team=away_team,vhost=self.vhost),thread_sensitive=False)()
            except self.models.TennisScore.MultipleObjectsReturned:
                away_score = await sync_to_async(
                    lambda: self.models.TennisScore.objects.using("default").filter(fixture=fixtureObj,
                                                                                           team=away_team,
                                                                                           vhost=self.vhost).first(),
                    thread_sensitive=False)()
            for k in ["s1","s2","s3","s4","s5","game_score","serve"]:
                # print(fixture_data["player"][0][f"@{k}"])
                if f"@{k}" in fixture_data["player"][0] and fixture_data["player"][0][f"@{k}"] != "False":
                    try:
                        val = Decimal(fixture_data["player"][0][f"@{k}"])
                    except:
                        val = 0
                else:
                    val = 0
                setattr(home_score,k,val)

                if f"@{k}" in fixture_data["player"][1] and fixture_data["player"][1][f"@{k}"] != "False":
                    try:
                        val = Decimal(fixture_data["player"][1][f"@{k}"])
                    except:
                        val = 0
                else:
                    val = 0
                setattr(away_score,k,val)
            if fixture_data["player"][0]["@totalscore"] != "":
                try:
                    home_score.score = Decimal(fixture_data["player"][0]["@totalscore"])
                except ValueError:
                    home_score.score = 0
            else:
                home_score.score = 0

            if fixture_data["player"][1]["@totalscore"] != "":
                try:
                    away_score.score = Decimal(fixture_data["player"][1]["@totalscore"])
                except ValueError:
                    away_score.score = 0
            else:
                away_score.score = 0
            # print(home_score)
            await sync_to_async(lambda:home_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:away_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:home_score.save(),thread_sensitive=False)()
            await sync_to_async(lambda:away_score.save(),thread_sensitive=False)()


    async def get_tennis_fixtures(self,fetch_type="home"):
        turl = self.url_root + f"/tennis_scores/{fetch_type}?json=1"
        data = await self._fetch_with_retry(turl)
        if data:
            json_data = data.json()
            if json_data["scores"]["@sport"] != "tennis":
                raise ValidationError(f"Feed {turl} did not provide a tennis type score result!!")
            for cat in json_data["scores"]["category"]:
                if type(cat) == dict:
                    if "@id" in cat and cat["@id"] != "":
                        catObj,created = await sync_to_async(lambda:self.models.SportCategory.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                                name=cat["@name"],id=int(cat["@id"])),thread_sensitive=False)()
                        if created:
                            await sync_to_async(lambda:catObj.save(),thread_sensitive=False)()
                            self.logger.info(f"Category {cat['@name']} created.")
                        if "match" in cat:
                            if type(cat["match"]) == list:
                                # tasks = [self.process_tennis_fixture(row, catObj) for row in cat["match"]]
                                # await asyncio.gather(*tasks, return_exceptions=True)
                                await self.run_in_batches(
                                    items=cat["match"],
                                    handler=lambda row: self.process_tennis_fixture(row, catObj),
                                    batch_size=25,
                                    label="tennis:fixtures",
                                )
                            else:
                                await self.process_tennis_fixture(cat["match"], catObj)
            self.logger.info(f"Synced Tennis fixtures from {fetch_type}.")





    async def process_hockey_fixture(self,fixture_data,catObj):
        if self.verbose:
            self.logger.info(f"Processing Hockey Fixture {fixture_data['fix_id']}...")
        home_team = await self._get_team(fixture_data['localteam']["id"], fixture_data['localteam']["name"])
        away_team = await self._get_team(fixture_data['awayteam']["id"], fixture_data['awayteam']["name"])

        if fixture_data["id"] != "" and fixture_data["fix_id"] != "":
            try:
                fixtureObj,cc = await sync_to_async(lambda:self.models.HockeyFixture.objects.using("default").get_or_create(vhost=self.vhost,category=catObj,
                                                                                               id=fixture_data["id"],
                                                                                               fixture_id=fixture_data["fix_id"],
                                                                                               home_team=home_team,away_team=away_team,
                                                                                               date=datetime.datetime.strptime(fixture_data["date"],"%d.%m.%Y")),thread_sensitive=False)()
            except self.models.HockeyFixture.MultipleObjectsReturned:
                fixtureObj = await sync_to_async(
                    lambda: self.models.HockeyFixture.objects.using("default").filter(vhost=self.vhost, category=catObj,
                                                                            id=fixture_data["id"],
                                                                            fixture_id=fixture_data["fix_id"],
                                                                            home_team=home_team, away_team=away_team,
                                                                            date=datetime.datetime.strptime(
                                                                                fixture_data["date"], "%d.%m.%Y")).first(),
                    thread_sensitive=False)()

            fixtureObj.status = fixture_data["status"]
            fixtureObj.time = fixture_data["time"]
            fixtureObj.time = fixture_data["timer"]
            if "PM" in fixtureObj.time or "AM" in fixtureObj.time:
                cto = datetime.datetime.strptime(f"{fixture_data["date"]} {fixture_data["time"]}", "%d.%m.%Y %I:%M %p").replace(tzinfo=datetime.timezone.utc)
            else:
                cto = datetime.datetime.strptime(f"{fixture_data["date"]} {fixture_data["time"]}","%d.%m.%Y %H:%M").replace(tzinfo=datetime.timezone.utc)
            fixtureObj.commence_time = cto
            await sync_to_async(fixtureObj.save,thread_sensitive=False)()
            try:
                home_score,_ = await sync_to_async(lambda:self.models.HockeyFixtureScore.objects.using("default").get_or_create(fixture=fixtureObj,team=home_team,vhost=self.vhost),thread_sensitive=False)()
            except self.models.HockeyFixtureScore.MultipleObjectsReturned:
                home_score = await sync_to_async(
                    lambda: self.models.HockeyFixtureScore.objects.using("default").filter(fixture=fixtureObj, team=home_team, vhost=self.vhost).first(), thread_sensitive=False)()
            try:
                away_score,_ = await sync_to_async(lambda:self.models.HockeyFixtureScore.objects.using("default").get_or_create(fixture=fixtureObj,team=away_team,vhost=self.vhost),thread_sensitive=False)()
            except self.models.HockeyFixtureScore.MultipleObjectsReturned:
                away_score = await sync_to_async(
                    lambda: self.models.HockeyFixtureScore.objects.using("default").filter(fixture=fixtureObj, team=away_team,
                                                                     vhost=self.vhost).first(), thread_sensitive=False)()
            try:
                home_score.score = int(fixture_data["localteam"]["totalscore"])
            except ValueError:
                home_score.score = 0
            try:
                away_score.score = int(fixture_data["awayteam"]["totalscore"])
            except ValueError:
                away_score.score = 0
            await sync_to_async(lambda:home_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:away_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:home_score.save(), thread_sensitive=False)()
            await sync_to_async(lambda:away_score.save(), thread_sensitive=False)()
            if "events" in fixture_data and fixture_data["events"] != None:
                for ek in ["firstperiod","secondperiod","thirdperiod","overtime","penalties"]:
                    if "event" in fixture_data["events"][ek]:
                        for ev in list(fixture_data["events"][ek]["event"]):
                            if type(ev) == dict:
                                if ev["team"] == "visitorteam":
                                    eteam = away_team
                                else:
                                    eteam = home_team
                                try:
                                    evObj, _ = await sync_to_async(
                                        lambda: self.models.HockeyEvent.objects.using("default").get_or_create(vhost=self.vhost, fixture=fixtureObj, type=ev["type"],
                                                                                  team=eteam),
                                                                                  thread_sensitive=False)()
                                except self.models.HockeyEvent.MultipleObjectsReturned:
                                    evObj = await sync_to_async(
                                        lambda: self.models.HockeyEvent.objects.using("default").filter(vhost=self.vhost, fixture=fixtureObj, type=ev["type"],
                                                                                  team=eteam).first(),
                                                                                  thread_sensitive=False)()

                                if ev["playerid"] != "":
                                    evObj.player = ev["player"]
                                    evObj.player_id = int(ev["playerid"])

                                if ev["assistid"] != "":
                                    evObj.assist_id = ev["assistid"]
                                    evObj.assist = ev["assist"]
                                evObj.minute = ev["min"]
                                evObj.period = ek
                                evObj.result = ev["result"]
                                await sync_to_async(evObj.save,thread_sensitive=False)()





    async def get_hockey_fixtures(self,fetch_type="home"):
        turl = self.url_root + f"/hockey/{fetch_type}?json=1"
        data = await self._fetch_with_retry(turl)
        if data:
            json_data = data.json()
            if json_data["scores"]["sport"] != "hockey":
                raise ValidationError(f"Feed {turl} did not provide a soccer type score result!!")
            for cat in json_data["scores"]["category"]:
                catObj,created = await sync_to_async(lambda:self.models.SportCategory.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                        name=cat["name"],id=int(cat["id"] or 0),
                                                                                        file_group=cat["file_group"]),thread_sensitive=False)()

                if created:
                    await sync_to_async(lambda:catObj.save(),thread_sensitive=False)()
                    self.logger.info(f"Category {cat['name']} created.")
                if "match" not in cat:
                    self.logger.info(f"Category {cat['name']}: Matches?")
                    return False
                if "match" in cat:
                    if type(cat["match"]) == list:
                        # tasks = [self.process_hockey_fixture(row, catObj) for row in cat["match"]]
                        # await asyncio.gather(*tasks, return_exceptions=True)
                        await self.run_in_batches(
                            items=cat["match"],
                            handler=lambda row: self.process_hockey_fixture(row, catObj),
                            batch_size=25,
                            label="hockey:fixtures",
                        )
                    else:
                        await self.process_hockey_fixture(cat["match"], catObj)
            self.logger.info(f"Synced Hockey fixtures from {fetch_type}.")

    async def process_americanf_fixture(self,fixture_data,catObj):
        if self.verbose:
            self.logger.info(f"Processing American Football Fixture {fixture_data['contestID']}...")
        home_team = await self._get_team(fixture_data['hometeam']["id"], fixture_data['hometeam']["name"])
        away_team = await self._get_team(fixture_data['awayteam']["id"], fixture_data['awayteam']["name"])
        # print(fixture_data["contestID"])
        if fixture_data["contestID"] != "":
            dt = datetime.datetime.strptime(fixture_data["datetime_utc"], "%d.%m.%Y %H:%M")
            # Attach UTC timezone
            dt_utc = dt.replace(tzinfo=datetime.timezone.utc)
            # print("a")
            fixtureObj,cc = await sync_to_async(lambda:self.models.AmericanFBallFixture.objects.using("default").get_or_create(vhost=self.vhost,category=catObj,
                                                                                           fixture_id=fixture_data["contestID"],commence_time=dt_utc,
                                                                                           home_team=home_team,away_team=away_team,
                                                                                           date=datetime.datetime.strptime(fixture_data["date"],"%d.%m.%Y")),thread_sensitive=False)()

            # print("b")
            fixtureObj.status = fixture_data["status"]
            fixtureObj.time = fixture_data["time"]
            fixtureObj.timer = fixture_data["timer"]

            if "PM" in fixtureObj.time or "AM" in fixtureObj.time:
                cto = datetime.datetime.strptime(f"{fixture_data["date"]} {fixture_data["time"]}", "%d.%m.%Y %I:%M %p").replace(tzinfo=datetime.timezone.utc)
            else:
                cto = datetime.datetime.strptime(f"{fixture_data["date"]} {fixture_data["time"]}","%d.%m.%Y %H:%M").replace(tzinfo=datetime.timezone.utc)
            # print("ee")
            if "venue_id" in fixture_data:
                fixtureObj.venue_id = fixture_data["venue_id"]
                fixtureObj.venue = fixture_data["venue_name"]
            # print("ffff")
            await sync_to_async(lambda:fixtureObj.save(),thread_sensitive=False)()
            # print("aaa")
            home_score,_ = await sync_to_async(lambda:self.models.AmericanFBallScore.objects.using("default").get_or_create(fixture=fixtureObj,team=home_team,vhost=self.vhost),thread_sensitive=False)()
            away_score,_ = await sync_to_async(lambda:self.models.AmericanFBallScore.objects.using("default").get_or_create(fixture=fixtureObj,team=away_team,vhost=self.vhost),thread_sensitive=False)()

            for k in ["q1","q2","q3","q4","ot"]:
                # print(fixture_data["player"][0][f"@{k}"])
                if fixture_data["hometeam"][f"{k}"] != "" and fixture_data["hometeam"][f"{k}"] != "False":
                    val = int(fixture_data["hometeam"][f"{k}"])
                else:
                    val = 0
                setattr(home_score, k, val)
                if fixture_data["awayteam"][f"{k}"] != "" and fixture_data["awayteam"][f"{k}"] != "False":
                    val = int(fixture_data["awayteam"][f"{k}"])
                else:
                    val = 0
                setattr(away_score, k, val)

            try:
                home_score.score = int(fixture_data["hometeam"]["totalscore"])
            except ValueError:
                home_score.score = 0
            try:
                away_score.score = int(fixture_data["awayteam"]["totalscore"])
            except ValueError:
                away_score.score = 0

            # self.logger.info(f"Processed American Football Fixture {fixture_data['contestID']} HS {home_score.score} AS {away_score.score}")
            await sync_to_async(lambda:home_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:away_team.save(),thread_sensitive=False)()
            await sync_to_async(lambda:home_score.save(),thread_sensitive=False)()
            await sync_to_async(lambda:away_score.save(),thread_sensitive=False)()


    async def get_americanf_fixtures(self,fetch_type="nfl-scores"):
        turl = self.url_root + f"/football/{fetch_type}?json=1"
        data = await self._fetch_with_retry(turl)

        if data:
            try:
                json_data = data.json()
            except:
                self.logger.warning(f"Got data from {turl} but failed to parse as JSON - skipping.")
                return False
            if json_data["scores"]["sport"] != "football":
                raise ValidationError(f"Feed {turl} did not provide a football type score result!!")
            cat = json_data["scores"]["category"]
            # print(cat)
            if "id" in cat and cat["id"] != "":

                catObj,created = await sync_to_async(lambda:self.models.SportCategory.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                        name=cat["name"],id=int(cat["id"])),thread_sensitive=False)()
                if created:
                    await sync_to_async(lambda:catObj.save(),thread_sensitive=False)()
                    self.logger.info(f"Category {cat['name']} created.")
                # print("Ayiee")
                if "match" in cat:
                    if type(cat["match"]) == list:
                        # print("ayee")
                        # tasks = [self.process_americanf_fixture(row, catObj) for row in cat["match"]]
                        # await asyncio.gather(*tasks, return_exceptions=True)
                        await self.run_in_batches(
                            items=cat["match"],
                            handler=lambda row: self.process_americanf_fixture(row, catObj),
                            batch_size=25,
                            label="americanf:fixtures",
                        )
                else:
                    await self.process_americanf_fixture(cat["match"], catObj)
            self.logger.info(f"Synced American Football fixtures from {fetch_type}.")


    async def get_scores(self):
        # if not self.last_timestamp:
        #     for i in range(2,8,1):
        #         key = f"d-{i}"
        #         await asyncio.gather(
        #             self.get_soccer_fixtures(key),
        #             self.get_basketball_fixtures(key),
        #             self.get_baseball_fixtures(key),
        #             self.get_tennis_fixtures(key),
        #             self.get_hockey_fixtures(key),
        #
        #         )
        # else:
        key = "d-1"
        # date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        await asyncio.gather(
            self.get_soccer_fixtures(),
            self.get_soccer_fixtures(key),
            self.get_basketball_fixtures(),
            self.get_basketball_fixtures(key),
            self.get_baseball_fixtures(),
            self.get_baseball_fixtures(key),
            self.get_tennis_fixtures(),
            self.get_tennis_fixtures(key),
            self.get_hockey_fixtures(),
            self.get_hockey_fixtures(key),
            # self.get_americanf_fixtures(f'nfl-scores?date={date}'),
            # self.get_americanf_fixtures(f'fbs-scores?date={date}'),
            self.get_americanf_fixtures('nfl-scores'),
            self.get_americanf_fixtures('fbs-scores'),
            return_exceptions=True
    )
    async def _work_cycle(self):
        await asyncio.gather(
            # self.get_leagues(),
            # self.get_teams(),
            # self.get_players(),
            self.get_scores(),
            return_exceptions=True
        )
        self.last_timestamp = localtime()

        # print("Eat at Joes!")
        self.logger.info(f"GoalServeD Worker Tick!")
