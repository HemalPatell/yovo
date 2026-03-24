"""
ASGI config for YOVO project.
Handles both HTTP and WebSocket connections via Django Channels.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import marketplace.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yovo_project.settings')

application = ProtocolTypeRouter({
    # Standard HTTP requests
    'http': get_asgi_application(),
    # WebSocket connections for real-time chat
    'websocket': AuthMiddlewareStack(
        URLRouter(
            marketplace.routing.websocket_urlpatterns
        )
    ),
})
