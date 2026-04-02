import asyncio
import base64
import json
import os
from datetime import timedelta
from types import SimpleNamespace
from typing import Optional

import httpx
from asgiref.sync import sync_to_async
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings
from django.db import IntegrityError
from django.db.models import OuterRef, Exists, Subquery, F
from django.utils.timezone import now


from asynctools.abc import AsyncWorkerABC
from dataengine.consumer.modelclient import DataEngineModelClient
from minerve.toolkit.serialisers import filtered_serialiser_many


class DataEngineWinnersPublisher(AsyncWorkerABC):
    # ----------------------
    # Child bootstrap
    # ----------------------
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from wager.models import Wager
        from account.models import Account
        from parameters.models import VHostParameterRegistry
        self.models = SimpleNamespace(
            Account=Account,
            Wager=Wager
        )
        parameters,c = VHostParameterRegistry.objects.get_or_create(vhost=self.vhost,name="api_keys",application="dataengine.publisher.winners")

        if c:
            parameters.save()
        self.parameters = parameters
        parameters, c = VHostParameterRegistry.objects.get_or_create(vhost=self.vhost, name="url",
                                                                     application="dataengine.publisher.winners")
        if c:
            parameters.save()
        self.url_parameters = parameters

    def build_winner_data(self):
        cutoff = now() - timedelta(days=60)
        winning_wagers = self.models.Wager.objects.filter(
            account=OuterRef("pk"),
            vhost=self.vhost,
            grade_outcome="W",
            hide_in_reports=False,
            graded_at__gte=cutoff,
        ).order_by("-graded_at")
        account_winners = self.models.Account.objects.filter(vhost=self.vhost).annotate(
            has_win=Exists(winning_wagers),
            win_amount=Subquery(winning_wagers.values("win")[:1]),
            last_win_at=Subquery(winning_wagers.values("graded_at")[:1]),
            source_vhost=F("vhost"),
        ).filter(has_win=True).order_by("-last_win_at")[:60]
        winners = self.models.Wager.objects.filter(vhost=self.vhost, grade_outcome='W', hide_in_reports=False,
                                                   graded_at__gte=cutoff).order_by(
            'graded_at', 'win')[0:50]
        winners_data, _, _ = filtered_serialiser_many(account_winners,
                                                      ["holder", "acctnum", "win_amount", "acctname", "pronouns",
                                                       "avatar"], [],
                                                      {"win_amount": "Win Amount", "last_win_at": "Last Win Date",
                                                       "source_vhost": "Source VHost"}, date_isoformat=True,
                                                      include_files=True)
        wagers_data, _, _ = filtered_serialiser_many(winners,
                                                     ["uuid", "account", "risk", "win", "graded_at", "created_at"],
                                                     date_isoformat=True)
        return winners_data,wagers_data

    async def _work_cycle(self):
        if not self.parameters.value_text:
            self.logger.warning("Cannot Publish Winners to winnerboard, no apikey")
            return False
        if not self.url_parameters.value_text:
            self.logger.warning("Cannot Publish Winners to winnerboard, no url setting")
            return False

        winners_data,wagers_data = await sync_to_async(lambda:self.build_winner_data(),thread_sensitive=False)()
        aes = AESGCM(self.parameters.value_bin)
        nonce = os.urandom(12)  # MUST be unique per message

        plaintext = json.dumps(
            {"winners": winners_data, "wagers": wagers_data},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        ciphertext = aes.encrypt(nonce, plaintext, None)
        output_data = {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        }
        try:
            response = await self.client.post(f"{self.url_parameters.value_text}/api/v1/create/winner/{self.parameters.value_text}",data=output_data)
            self.logger.info(f"Response: {response}")
        except httpx.HTTPStatusError as e:
            self.logger.warning(f"Cannot Publish Winners to winnerboard: HTTPx error: {e}")

        self.logger.info("Winner Publisher Tick.")