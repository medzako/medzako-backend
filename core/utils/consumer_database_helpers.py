from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from jwt import decode

from authentication.models import User
from core.utils.constants import RECEIVED
from order.serializers import SocketOrderSerializer
from order.models import Order
from medication.models import Pharmacy

@database_sync_to_async
def get_user(token):
    payload = decode(token, settings.SECRET_KEY, algorithms=['HS512'])
    user_id = payload['user_id']
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


@database_sync_to_async
def fetch_order(order_id):
    return Order.objects.get(pk=order_id)

@database_sync_to_async
def fetch_user(rider_id):
    return User.objects.get(pk=rider_id)

@database_sync_to_async
def fetch_pharmacy(pharmacy_id):
    return Pharmacy.objects.get(pk=pharmacy_id)

@database_sync_to_async
def update_tracking_loc(consumer_obj, lat, long):
    consumer_obj.order.tracking_object.lat = lat
    consumer_obj.order.tracking_object.long = long
    consumer_obj.order.tracking_object.save()

@database_sync_to_async
def fetch_current_loc(consumer_obj):
    lat = consumer_obj.order.tracking_object.lat
    long = consumer_obj.order.tracking_object.long 
    return float(lat), float(long)

@database_sync_to_async
def fetch_pharmacy_orders(consumer_obj):
    orders = consumer_obj.pharmacy.orders.all().filter(status=RECEIVED)
    serializer = SocketOrderSerializer(orders, many=True)
    return serializer.data

@database_sync_to_async
def fetch_riders_orders(consumer_obj):
    orders = consumer_obj.rider.rider_orders.all()
    serializer = SocketOrderSerializer(orders, many=True)
    return serializer.data

@database_sync_to_async
def get_tracking_id(consumer_obj):
    return consumer_obj.order.tracking_object.tracking_id

@database_sync_to_async
def get_pharmacy_security_code(consumer_obj):
    return consumer_obj.pharmacy.socket_security_code

@database_sync_to_async
def get_rider_security_code(consumer_obj):
    return consumer_obj.rider.rider_profile.socket_security_code
