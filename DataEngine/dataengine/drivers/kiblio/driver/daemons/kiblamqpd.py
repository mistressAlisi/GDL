import json
import logging
import multiprocessing
from types import SimpleNamespace

import pika
from django.utils.timezone import localtime


class KIBLAMQPd(multiprocessing.Process):
    connection = None
    node_url  = None
    vhost = None
    logger = False
    dataEngine = None
    def setup(self, vhost,logger,verbose=False,**kwargs):
        self.vhost = vhost
        self.verbose = verbose
        self.logger = logger.getLogger("dataengine.drivers.kiblio.daemons.kiblamqpd")
        # self.logger.info("Setting up KIBLAMQPd")
        self.node_url = pika.URLParameters('amqps://miker:MikeR88!@rabbitmq.kibl.io/')
        # self.dataEngine._load_driver(DataEngineVHostConfig.objects.get(vhost=vhost,active=True,driver__class_name="dataengine.drivers.kiblio").driver)

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.kiblio.models import Sportsbook, Fixture, Participant, FixtureMarket
        from dataengine.engine import DataEngine
        from dataengine.models import DataEngineVHostConfig
        from parameters.models import Timezone, VHostParameterRegistry
        self.last_timestamp = localtime()
        from ...api.common import process_fixture_market_data, KIBL_MARKET_UPDATE_FIELDS, process_fixture_data, \
            process_fixture_outcomes_data
        self.process_fixture_market_data = process_fixture_market_data
        self.KIBL_MARKET_UPDATE_FIELDS = KIBL_MARKET_UPDATE_FIELDS
        self.process_fixture_data = process_fixture_data
        self.process_fixture_outcomes_data = process_fixture_outcomes_data
        self.models = SimpleNamespace(
            Sportsbook=Sportsbook,
            Fixture=Fixture,
            Participant=Participant,
            FixtureMarket=FixtureMarket,
            DataEngine=DataEngine,
            DataEngineVHostConfig=DataEngineVHostConfig,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,
        )
        self.dataEngine = DataEngine(self.vhost)
    def on_mkt_message(self, channel, method_frame, header_frame, body):
        # print(method_frame.delivery_tag)
        mkt_msg = json.loads(body.decode('utf-8'))
        fmxObj = False
        fixtureObj = False
        for entry in mkt_msg["result"]:
            # print(entry)
            for participant in entry["participants"]:

                # print(Fixture.objects.filter(fixture_id=participant["fixture_id"]))
                # print("**********")
                try:
                    sbkObj =  self.models.Sportsbook.objects.get(feed_source_id=participant["feed_source_id"],vhost=self.vhost)
                    fixtureObj = self.models.Fixture.objects.get(fixture_id=participant["fixture_id"],vhost=self.vhost)
                # print(self.vhost)
                    fmxObj = self.process_fixture_market_data(participant, self.vhost, fixtureObj, sbkObj)
                    if self.verbose:
                        self.logger.info(f"Updated Markets for fixture {fixtureObj.fixture_id}")
                except self.models.Fixture.MultipleObjectsReturned:
                    print("Multiple fixtures found!!!")
                    print(self.models.Fixture.objects.filter(fixture_id=participant["fixture_id"]))
                    raise Exception('Die die die')
                except self.models.Fixture.DoesNotExist:
                    # This is tricky, use the Participant to try and reverse lookup the league for a given fixture using the markets:
                    # This situation happens so often in the AMPQd streams that it makes sense to handle it this way:
                #     try:
                #         try:
                #             partObj = Participant.objects.get(feed_source_id=participant["participant_id"],vhost=self.vhost)
                #         except Participant.DoesNotExist:
                #             partObj = False
                #         if partObj:
                #             mktsObj = FixtureMarket.objects.filter(vhost=self.vhost,participant=partObj)
                #             if len(mktsObj) > 0:
                #                 leagueObj = mktsObj[0].league
                #                 fmxObj = Fixture.objects.get_or_create(fixture_id=participant["fixture_id"],vhost=self.vhost,parent_fixture_id=participant["fixture_id"],league=leagueObj)[0]
                # except Sportsbook.DoesNotExist:
                    self.logger.info(f"Sportsbook {participant["feed_source_id"]} does not exist - not synced yet: AMQPd will keep trying. HTTPd can resolve by fixture_run.")
                    fmxObj = False
        if fmxObj and fixtureObj:
            # Call a DataEngine Sync for this match and its markets:
            # self.dataEngine.sync_matches(True, provider_match_objs=[fixtureObj])
            # self.dataEngine.sync_markets(True, provider_match_objs=[fixtureObj])
            # FIXME: Not sure yet... but do this.
            pass
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)


    def on_fxt_message(self, channel, method_frame, header_frame, body):
        # print(method_frame.delivery_tag)
        fxt_msg = json.loads(body.decode('utf-8'))
        if fxt_msg["api_key"] != 'get_sport_market_info_by_interest:fixtures':
            self.logger.info(f"on_fxt_message is ignoring message {fxt_msg}: Api key is not recognised.")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return False
        for entry in fxt_msg["result"]:
            fixtureObj = self.process_fixture_data(entry, self.vhost)
            if self.verbose:
                self.logger.info(f"Updated fixture {fixtureObj.fixture_id}")
            print(f"Updated fixture {fixtureObj.fixture_id}")
            # Call a data sync for the match:
            # FIXME: DATA SYNC?
            # self.dataEngine.sync_matches(True, provider_match_objs=[fixtureObj])
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)


    def on_outc_message(self, channel, method_frame, header_frame, body):
        # print(method_frame.delivery_tag)
        outc_msg = json.loads(body.decode('utf-8'))
        if outc_msg["api_key"] != 'get_sport_market_info_by_interest:outcomes':
            self.logger.info(f"on_outc_message is ignoring message {outc_msg}: Api key is not recognised.")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return False
        for entry in outc_msg["result"]:
            # print(entry)
            outcomeObj,_,_ = self.process_fixture_outcomes_data(entry, self.vhost)
            if outcomeObj:
                if self.verbose:
                    self.logger.info(f"Updated fixture {outcomeObj.fixture.fixture_id} outcomes.")
                # print(f"Updated fixture {outcomeObj.fixture.fixture_id} outcomes.")
                # Call a DataEngine Sync for this match and its outcomes:
                # FIXME: DATA SYNC?
                # self.dataEngine.sync_matches(True, provider_match_objs=[outcomeObj.fixture])
                # self.dataEngine.sync_outcomes(True, provider_match_objs=[outcomeObj.fixture])
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)


    def run(self):
        self.connection = pika.BlockingConnection(self.node_url)
        channel = self.connection.channel()
        # Market Queue basic consumer:
        channel.basic_consume('miker.get.info.markets', self.on_mkt_message)
        # Fixture Queue basic consumer:
        channel.basic_consume('miker.get.info.fixtures', self.on_fxt_message)
        # Fixture Outcome basic consumer:
        channel.basic_consume('miker.get.info.outcomes', self.on_outc_message)
        self.logger.info("Starting Pika Consumer....")
        print("Athena, (c) 2024-2025 Solstic Systems B.V.")
        print("... Starting KIBL AMQPd ...")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        self.connection.close()


