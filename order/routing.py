from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import RiderOrderTrackingConsumer, ClientOrderTrackingConsumer, PharmacyReceivedOrders, RiderReceivedOrders


websockets = URLRouter([
    path(
        "ws/update-order-location/<int:order_id>", RiderOrderTrackingConsumer.as_asgi(),
        name="location-update",
    ),
    path(
        "ws/fetch-order-location/<int:order_id>", ClientOrderTrackingConsumer.as_asgi(),
        name="fetch-order-location",    
    ),
    path(
        "ws/fetch-pharmacy-received-orders/<int:pharmacy_id>", PharmacyReceivedOrders.as_asgi(),
        name="fetch-pharmacy-received_orders",
    ),
    path(
        "ws/fetch-rider-received-orders/<int:rider_id>", RiderReceivedOrders.as_asgi(),
        name="fetch-rider-received_orders",    
    ),
])
