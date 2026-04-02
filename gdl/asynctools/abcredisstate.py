# asynctools/abcredisstate.py
import json
import redis.asyncio as redis
from django.conf import settings


class RedisStateMixin:
    redis_url = settings.REDIS_URL
    redis_prefix = "state"

    async def _redis_start(self):
        self.redis = redis.from_url(
            self.redis_url,
            decode_responses=True,
        )

        # sanity check
        await self.redis.ping()

    async def _redis_stop(self):
        if getattr(self, "redis", None):
            await self.redis.close()

    # -------------------------------------------------
    # key helpers
    # -------------------------------------------------

    def _redis_key(self, vhost, model, uuid):
        return f"{self.redis_prefix}:{vhost}:{model}:{uuid}"

    # -------------------------------------------------
    # write path (publisher)
    # -------------------------------------------------

    async def set_state_many(self, vhost, model, rows):
        """
        rows = list of SERIALISED dicts (must include uuid)
        """
        pipe = self.redis.pipeline(transaction=False)

        for row in rows:
            key = self._redis_key(vhost, model, row["uuid"])
            pipe.set(key, json.dumps(row))

        await pipe.execute()

    # -------------------------------------------------
    # read path
    # -------------------------------------------------

    async def get_state(self, vhost, model, uuid):
        key = self._redis_key(vhost, model, uuid)
        val = await self.redis.get(key)
        return json.loads(val) if val else None

    async def has_state(self, vhost, model, uuid):
        key = self._redis_key(vhost, model, uuid)
        return bool(await self.redis.exists(key))

    async def read_state_many(self, model, ids):
        """
        Retrieve multiple objects from Redis by model and list of IDs.
        """
        # Assuming self.redis is an async Redis client
        keys = [f"{model.__name__}:{id_}" for id_ in ids]
        values = await self.redis.mget(*keys)  # returns list of serialized objects
        # deserialize if needed
        return [json.loads(v) for v in values if v is not None]
