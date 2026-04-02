# applications/gdl/consumers.py

import json
import asyncio

import uuid
from datetime import timedelta

import websockets
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.utils.timezone import now

from account.models import Account
from game.gdlcore.utils.tickets import _store_ticket
from game.gdlfront.models import GDLTicketCartCache
from parameters.models import VHost, VHostDomain




class GDLTicketStreamConsumer(AsyncWebsocketConsumer):
    """
    Streams parlay tickets by proxying to the GPU daemon backend.
    One consumer per client → one websocket connection to the client.
    A new backend connection is created for each request.
    """



    async def connect(self):
        await self.accept()
        self.pending_ticket_tasks = set()
        self.backend_uri = settings.GDL_DAEMON_URI
        self.backend_ws = None
        self.backend_task = None
        self.old_uuid = None

    async def disconnect(self, close_code):
        await self._close_backend()

    async def receive(self, text_data):
        """
        Each message from client = new generation request or control command.
        """
        try:
            payload = json.loads(text_data)
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "error": f"Invalid JSON: {e}"
            }))
            return

        # --- handle ping / non-generation commands early ---
        if payload.get("type") == "ping" or payload.get("action") == "ping":
            await self.send(text_data=json.dumps({
                "type": "pong",
                "timestamp": now().isoformat(),
            }))
            return

        # --- ignore or reject unknown message types safely ---
        if "settings" not in payload:
            await self.send(text_data=json.dumps({
                "type": "error",
                "error": "Missing settings in request payload."
            }))
            return

        # --- safe numeric conversions ---
        try:
            settings_data = payload["settings"]
            settings_data["min_payout"] = float(settings_data.get("min_payout", 0))
            settings_data["stake"] = float(settings_data.get("stake", 0))
            settings_data["depth"] = int(settings_data.get("depth", 0))
            settings_data["count"] = int(settings_data.get("count", 0))
            if "events_within" not in settings_data:
                settings_data["events_within"] = 129600  # 36h
            settings_data.pop("csrfmiddlewaretoken", None)
            settings_data.pop("ruleset", None)
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "error": f"Invalid settings payload: {e}"
            }))
            return
        old_uuid = payload.get("old_uuid", None)
        self.old_uuid = old_uuid
        if self.old_uuid is not None:
            del(payload["old_uuid"])
        # print(f"OLD UUID {self.old_uuid}")
        # --- add defaults & backend metadata ---
        payload["use_gpu"] = True
        payload["debug"] = True
        payload["request_id"] = str(uuid.uuid4())
        payload.setdefault("neg_limit", -200)
        payload.setdefault("juice", 0.05)
        payload.setdefault("debug", True)

        # reset any old backend stream
        await self._close_backend()

        try:
            self.backend_ws = await websockets.connect(self.backend_uri)
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "error": f"Failed to connect to backend daemon: {e}"
            }))
            await self.close()
            return

        # send request to backend
        # print(payload)
        await self.backend_ws.send(json.dumps(payload))

        # start streaming results back to client
        self.backend_task = asyncio.create_task(self._proxy_backend_stream())

    async def _proxy_backend_stream(self):
        try:
            async for message in self.backend_ws:
                parsed = json.loads(message)
                if self.old_uuid:
                    parsed["old_uuid"] = str(self.old_uuid)
                await self.send(text_data=json.dumps(parsed))

                # stop when daemon signals completion
                try:
                    if parsed.get("type") == "complete":
                        self.backend_complete = True
                except Exception:
                    pass
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "error": f"Backend stream error: {e}"
            }))
        finally:
            await self._close_backend()

    async def _close_backend(self):
        if self.backend_task:
            self.backend_task.cancel()
            self.backend_task = None
        if self.backend_ws:
            try:
                await self.backend_ws.close()
            except Exception:
                pass
            self.backend_ws = None

class GDLTicketStoreStreamConsumer(GDLTicketStreamConsumer):
    """
    Subclass: same as GDLTicketStreamConsumer, but stores tickets in ORM.
    Only returns tickets that already have UUIDs in DB.
    """

    async def receive(self, text_data):
        # print("[DEBUG] StoreConsumer.receive called")
        try:
            payload = json.loads(text_data)
            # print(f"[DEBUG] Parsed payload: {payload}")
        except Exception as e:
            await self.send(text_data=json.dumps({
                "status": "error", "error": f"Invalid JSON: {e}"
            }))
            return

        # Grab vhost + account + vdomain directly from payload.settings
        print(payload)
        settings = payload.get("settings", {})
        print(settings)

        vhost_uuid = settings.get("vhost")
        account_uuid = settings.get("account")
        vdomain_uuid = settings.get("vdomain")

        # print(f"[DEBUG] settings vhost={vhost_uuid}, account={account_uuid}, vdomain={vdomain_uuid}")

        def fetch_context():
            # print("[DEBUG] fetch_context() called")
            if not vhost_uuid or not account_uuid or not vdomain_uuid:
                return None,None,None
            vhost = VHost.objects.get(uuid=vhost_uuid)
            vdomain = VHostDomain.objects.get(uuid=vdomain_uuid, vhost=vhost)
            account = Account.objects.get(uuid=account_uuid, vhost=vhost)
            # print(f"[DEBUG] fetch_context() done → vhost={vhost}, vdomain={vdomain}, account={account}")
            return vhost, vdomain, account

        self.account_context = await asyncio.to_thread(fetch_context)

        # print(f"[DEBUG] account_context set: {self.account_context}")

        # print("[DEBUG] Delegating to super().receive")
        await super().receive(text_data)
        # print("[DEBUG] super().receive finished")

    async def _proxy_backend_stream(self):
        # print("[DEBUG] StoreConsumer._proxy_backend_stream started")

        try:
            async for message in self.backend_ws:
                # print(f"[DEBUG] Received message from backend: {message[:200]}...")
                try:
                    parsed = json.loads(message)
                except Exception:
                    # print("[DEBUG] Failed to parse backend message as JSON, forwarding raw")
                    await self.send(text_data=message)
                    continue
                # print("Parsed Message back")
                if self.old_uuid:
                    parsed["old_uuid"] = str(self.old_uuid)
                # print(parsed)
                if parsed.get("type") == "ticket":

                    async def store_and_send(parsed):
                        vhost, vdomain, account = self.account_context
                        obj = await sync_to_async(
                            lambda: _store_ticket(parsed, vhost, vdomain, account),
                            thread_sensitive=False
                        )()
                        parsed["uuid"] = str(obj.uuid)
                        await self.send(text_data=json.dumps(parsed))

                    task = asyncio.create_task(store_and_send(parsed))
                    self.pending_ticket_tasks.add(task)
                    task.add_done_callback(self.pending_ticket_tasks.discard)

                elif parsed.get("type") == "complete":
                    # print("[DEBUG] Received complete signal from backend")

                    # Pull global totals from ORM
                    vhost, vdomain, account = self.account_context
                    if self.pending_ticket_tasks:
                        await asyncio.gather(*self.pending_ticket_tasks)
                    def fetch_totals():
                        qs = GDLTicketCartCache.objects.filter(
                            vhost=vhost, domain=vdomain, account=account
                        )
                        total_risk = sum(qs.values_list("risk", flat=True))
                        total_wins = sum(qs.values_list("returns", flat=True))
                        ticket_count = qs.count()
                        return ticket_count, total_risk, total_wins

                    ticket_count, total_risk, total_wins = await asyncio.to_thread(fetch_totals)

                    complete_frame = {
                        "type": "complete",
                        "ticket_count": ticket_count,
                        "total_risk": total_risk,
                        "total_wins": total_wins,
                    }
                    if self.old_uuid:
                        complete_frame["old_uuid"] = str(self.old_uuid)
                    # print(f"[DEBUG] Sending enriched complete frame: {complete_frame}")
                    await self.send(text_data=json.dumps(complete_frame))
                    self.generator_complete = True

                else:
                    # print(f"[DEBUG] Non-ticket message: {parsed}")
                    await self.send(text_data=message)

        except Exception as e:
            # print(f"[DEBUG] Exception in _proxy_backend_stream: {e}")
            await self.send(text_data=json.dumps({
                "type": "error", "error": f"Backend stream error: {e}"
            }))
        finally:
            # print("[DEBUG] Closing backend stream")
            await self._close_backend()
