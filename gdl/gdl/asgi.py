"""
ASGI config for gdl project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdl.settings')
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application

from gdl.middleware import CloseDBConnectionsMiddleware
from gdl.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()

application = CloseDBConnectionsMiddleware(
    ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            SessionMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    })
)
