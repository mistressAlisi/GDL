import asyncio
import os

import sys
import signal
from datetime import datetime, timedelta
from json import JSONDecodeError
from types import SimpleNamespace

from asgiref.sync import sync_to_async
from django.db import close_old_connections
from django.forms import model_to_dict
from django.utils.timezone import localtime, localdate, now


from asynctools.abc import AsyncWorkerABC


class CashierAsyncDaemon(AsyncWorkerABC):

    def __init__(self, vhost=None, logger=None, name: str = "worker", interval: float = 60, run_in_process: bool = True,loki_url=None,):
        AsyncWorkerABC.__init__(self, vhost, logger, name, interval, run_in_process,loki_url)

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from cashier.models import AccountBalance, CryptoCurrencyFXHistory, CryptoCurrency, AccountDailyBalance
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            AccountBalance=AccountBalance,
            CryptoCurrencyFXHistory=CryptoCurrencyFXHistory,
            CryptoCurrency=CryptoCurrency,
            AccountDailyBalance=AccountDailyBalance
        )
        self._midnight_task: asyncio.Task | None = None
        self.last_timestamp = localtime() -timedelta(minutes=1)

    async def _account_close_daily_balance(self,balanceObj):
        balance_data = await sync_to_async(lambda: SimpleNamespace(**model_to_dict(balanceObj)), thread_sensitive=False)()
        acctobj = await sync_to_async(lambda:balanceObj.account,thread_sensitive=False)()
        curr_date = localdate()
        adbObj,_ = await sync_to_async(lambda:self.models.AccountDailyBalance.objects.get_or_create(account=acctobj,date=curr_date,vhost=self.vhost),thread_sensitive=False)()
        await self._object_setattrs(adbObj,balance_data,rows=["available","deposits","withdrawals","fees","bonus","bonus_points",
                                                              "pending_deposits","pending_rollovers","rollovers","pending_withdraw","at_risk"])
        self.logger.info(f"Closed daily balance for {balance_data.account}.")


    async def _sync_crypto_cl_handle(self,crypto):
        id = await sync_to_async(lambda:crypto.coinlore_id,thread_sensitive=False)()
        symbol = await sync_to_async(lambda:crypto.symbol,thread_sensitive=False)()
        # print(id)
        turl = f"https://api.coinlore.net/api/ticker/?id={id}"
        try:
            data = await self._fetch_with_retry(turl)
            if not data: return False
            data = data.json()
        except JSONDecodeError:
            self.logger.info(f"For url {turl} - JSON decode error - skipping.")
            return False
        if len(data) == 0: return False

        data = data[0]
        # print(data,symbol)
        if data["symbol"] != symbol: return False
        if "price_usd" in data:
            crypto.current_usd_exr = data["price_usd"]
        # print(data["price_usd"])
        if "price_btc" in data:
            crypto.current_btc_exr = data["price_btc"]
        # print(data["price_btc"])
        await sync_to_async(lambda:crypto.save(),thread_sensitive=False)()
        cfx = await sync_to_async(lambda:self.models.CryptoCurrencyFXHistory.objects.create(vhost=self.vhost,crypto=crypto,current_usd_exr=data["price_usd"],current_btc_exr=data["price_btc"]),thread_sensitive=False)()
        await sync_to_async(lambda:cfx.save(),thread_sensitive=False)()
        # print("reeee")
        self.logger.info(f"Updated Crypto {symbol}.")
        return True

    async def sync_crypto_to_coinlore(self):
        cryptos = await sync_to_async(lambda: list(
            self.models.CryptoCurrency.objects.filter(vhost=self.vhost, active=True, coinlore_id__isnull=False)),thread_sensitive=False)()
        # print(cryptos)
        semaphore = asyncio.Semaphore(os.cpu_count())

        async def sem_task(fixture):
            async with semaphore:
                await self._sync_crypto_cl_handle(fixture)

        # --- Launch all tasks concurrently, respecting the semaphore ---
        tasks = [sem_task(f) for f in cryptos]
        await asyncio.gather(*tasks)

    async def _midnight_loop(self):

        while not self._shutdown_event.is_set():
            wait_seconds = await self._seconds_until_midnight()
            self.logger.info(f"Sleeping {wait_seconds:.2f}s until midnight...")
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=wait_seconds,
                )
                # shutdown event fired
                self.logger.info("Shutdown event received, exiting midnight loop")
                break

            except asyncio.TimeoutError:
                # timeout == midnight reached
                self.logger.info("Midnight reached, running job")

            try:
                acctObj = self.models.AccountBalance.objects.filter(vhost=self.vhost)
                accountBalances = await sync_to_async(list,thread_sensitive=False)(acctObj)
                await self.run_in_batches(
                    accountBalances,
                    self._account_close_daily_balance,
                    50,
                    "AccountDailyBalance",
                )
            except Exception:
                self.logger.exception("Error in midnight job")

    def setup_loop(self):
        """
        Called once before the main loop begins.
        Starts the midnight loop in the background so it doesn't block continuous work.
        """
        if getattr(self, "_midnight_task", None) is not None:
            return

        loop_fn = type(self)._midnight_loop  # ← unbound function
        self._midnight_task = asyncio.create_task(loop_fn(self))

        self.logger.info("Midnight loop started in background.")




    async def _do_continuous_work(self):
        try:
            await self.sync_crypto_to_coinlore()
        except Exception as e:
            self.logger.exception(f"[CashierAsyncDaemon] Error in continuous work: {e}")
        self.last_timestamp = localtime()
        self.logger.info("[CashierAsyncDaemon] Tock...")

    async def _work_cycle(self):
        """Main continuous worker tick."""
        await self._do_continuous_work()
        await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()

    async def _run(self):
        self.setup_loop()
        await AsyncWorkerABC._run(self)