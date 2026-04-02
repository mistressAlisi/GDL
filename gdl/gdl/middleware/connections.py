from asgiref.sync import sync_to_async
from django.db import connections
from django.utils.asyncio import async_unsafe


class CloseDBConnectionsMiddleware:
    """
    Aggressively close all DB connections after each ASGI scope.
    Safe with replicas and routers.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            return await self.app(scope, receive, send)
        finally:
            await sync_to_async(lambda:self.close_all(),thread_sensitive=False)()

    @async_unsafe
    def close_all(self):
        for conn in connections.all():
            conn.close()