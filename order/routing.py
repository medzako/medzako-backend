from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import RiderOrderTrackingConsumer, PharmacyReceivedOrders, Notifications


websockets = URLRouter([
    path(
        "ws/order-location/<int:order_id>", RiderOrderTrackingConsumer.as_asgi(),
        name="location-update",
    ),
    path(
        "ws/fetch-pharmacy-received-orders/<int:pharmacy_id>", PharmacyReceivedOrders.as_asgi(),
        name="fetch-pharmacy-received_orders",
    ),
    path(
        "ws/notifications", Notifications.as_asgi(),
        name="fetch-rider-received_orders",
    ),
])
