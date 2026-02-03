import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import app.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

# Keep HTTP + WebSocket wiring explicit; Channels uses the ASGI router below.
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(app.routing.websocket_urlpatterns)),
    }
)
