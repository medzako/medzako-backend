from channels.routing import ProtocolTypeRouter
from authentication.sockets_middleware import  TokenAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator

from order.routing import websockets 

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(websockets),
    )
})
