from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import RiderOrderTrackingConsumer, ClientOrderTrackingConsumer


websockets = URLRouter([
    path(
        "ws/update-order-location/<int:order_id>", RiderOrderTrackingConsumer.as_asgi(),
        name="location-update",
    ),
    path(
        "ws/fetch-order-location/<int:order_id>", ClientOrderTrackingConsumer.as_asgi(),
        name="fetch-order-location",    
    ),
])
