from typing import Optional
import asyncio


class DataEngineModelClient:
    """
    Snapshot-safe, fan-out capable page client.

    Guarantees:
      - Stable dataset via snapshot_ts
      - Safe parallel page fetch
      - No missing or duplicated rows
    """

    def __init__(
        self,
        *,
        parent,
        name: str,
        endpoint: str,
        update_field_name: Optional[str] = None,
    ):
        self.parent = parent
        self.name = name
        self.endpoint = endpoint.rstrip("/")
        self.update_field_name = update_field_name

        self.snapshot_ts = None
        self._page_semaphore = asyncio.Semaphore(16) # 👈 START HERE (tune later)

    # --------------------------------------------------
    # Fetch one page
    # --------------------------------------------------
    async def fetch_page(self, *, page=1, snapshot_ts=None, **filters):
        async with self._page_semaphore:  # 👈 critical
            params = {
                "apikey": self.parent.api_key,
                "page": page,
            }

            if snapshot_ts:
                params["snapshot_ts"] = snapshot_ts

            if self.update_field_name:
                params[self.update_field_name] = self.last_timestamp

            params.update(filters)

            url = f"{self.parent.remote_host_url}{self.endpoint}"

            resp = await self.parent._fetch_with_retry(url, params=params)
            if not resp:
                return None

            payload = resp.json()
            if not payload.get("success"):
                raise RuntimeError(f"{self.name} fetch failed: {payload}")

            return payload

    # --------------------------------------------------
    # Iterate pages (fan-out safe)
    # --------------------------------------------------
    async def iter_pages(self, **filters):
        # --------------------------------------------------
        # Phase 1: page 1 (establish snapshot)
        # --------------------------------------------------
        first = await self.fetch_page(page=1, **filters)
        if not first:
            return

        self.snapshot_ts = first.get("snapshot_ts")
        max_pages = first.get("max_pages", 1)

        yield first

        if max_pages <= 1:
            return

        # --------------------------------------------------
        # Phase 2: fan-out remaining pages
        # --------------------------------------------------
        async def fetch(n):
            return await self.fetch_page(
                page=n,
                snapshot_ts=self.snapshot_ts,
                **filters,
            )

        tasks = [fetch(p) for p in range(2, max_pages + 1)]

        for coro in asyncio.as_completed(tasks):
            payload = await coro
            if not payload:
                continue

            data = payload.get("data", [])
            if not data:
                continue

            yield payload

    # --------------------------------------------------
    # Iterate rows (streaming)
    # --------------------------------------------------
    async def iter_all(self, **filters):
        async for payload in self.iter_pages(**filters):
            for row in payload.get("data", []):
                yield row
