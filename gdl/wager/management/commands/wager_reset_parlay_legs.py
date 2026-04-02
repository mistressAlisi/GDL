import json
import logging

from django.core.management import BaseCommand
from django.utils.timezone import now
from tabulate import tabulate

from dataengine.engine.core import DataEngine

from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from grader.modules.abc import GraderModuleABC
from parameters.models import VHost
from daemon.main import DaemonManager
from wager.models import Wager


class Command(BaseCommand):
    help = 'Dataengine Daemon Runner.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("wager", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        wagerObj = Wager.objects.get(pk=options["wager"][0],vhost=vHost)
        self.stdout.write(self.style.MIGRATE_HEADING("Vhost: {vhost} Wager: {wager} - Leg Data:".format(vhost=vHost,wager=wagerObj)))
        nodes = []
        if "root_wager" in wagerObj.bet_data:
            root = wagerObj
        elif "parent" in wagerObj.bet_data:
            root = Wager.objects.get(uuid=wagerObj.bet_data["parent"])
        nodes.append(root)
        for _node in root.bet_data["nodes"]:
            nodeObj = Wager.objects.get(uuid=_node)
            nodes.append(nodeObj)
        node_table = []
        for node in nodes:
            node.status = 'P'
            node.closed = False
            node.grade_outcome = None
            node.executed = False
            node.save()
            node_table.append([node.uuid,
                               node.match.uuid,
                               node.match.name,
                               node.match.commence_time,
                               node.match.winner.name if (node.match.winner != None) else "",
                               node.team_1.name,
                               node.risk,
                               node.win,
                               node.match.status_short,
                               node.status,
                               node.grade_outcome
                               ])

        self.stdout.write(
            tabulate(
                node_table,
                headers=["UUID","MUUID","Match","Commence Time","Outcome","Bet on","Risk","Win","Match Status","Wager Status","Grade Outcome"],
                tablefmt="grid",
            )
        )
