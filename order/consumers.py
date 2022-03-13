# Built in imports.
import json
from telnetlib import STATUS
from asgiref.sync import sync_to_async
# Third Party imports.
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
# Django imports.
from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async
from authentication.models import User

from core.utils.constants import RECEIVED
from order.serializers import FetchOrderSerializer, OrderSerializer, SocketOrderSerializer

# Local imports.
from .models import Order
from medication.models import Pharmacy


@database_sync_to_async
def fetch_order(order_id):
    return Order.objects.get(pk=order_id)

@database_sync_to_async
def fetch_rider(rider_id):
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


class RiderOrderTrackingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.order_name = f'Order_{self.order_id}'

        await self.channel_layer.group_add(
            self.order_name,
            self.channel_name
        )
        # If invalid order id then deny the connection.
        try:
            self.order = await fetch_order(self.order_id)
        except ObjectDoesNotExist:
            raise DenyConnection("Invalid Order Id")
        await self.accept()

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
            order_location = data.get('order_location')
            tracking_id = data.get('tracking_id')
            await self.channel_layer.group_send(
                self.order_name,
                {
                    'type': 'order_location',
                    'tracking_id': tracking_id,
                    'order_id': self.order_id,
                    'order_location': order_location
                }
            )
        except Exception:
            pass
        

    async def order_location(self, event):
        lat = long = None
        messages = []
        is_successful = True

        order_location = event['order_location']
        tracking_id = event['tracking_id']

        if type(order_location) == dict:
            lat = order_location.get('lat')
            long = order_location.get('long')
        else:
            messages.append('Order location value must be a dictionary')
            is_successful = False

        if not lat or not long:
            messages.append('Latitude or longitude not present in payload')
            is_successful = False
            
        db_tracking_id = await get_tracking_id(self)

        if tracking_id == db_tracking_id:
            await update_tracking_loc(self, lat=lat, long=long)
            messages.append('Update succesful')
            is_successful = True
        else:
            messages.append('Invalid tracking id')
            is_successful = False

        data = {
            'success': is_successful,
            'messages': messages
        }

        text_data = json.dumps(data)

        # Here helper function fetches data from DB.
        await self.send(text_data)

    async def websocket_disconnect(self, message):
            # Leave room group
            await self.channel_layer.group_discard(
                self.order_name,
                self.channel_name
            )
    

class ClientOrderTrackingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.order_name = f'Order_{self.order_id}_fetch'
        # if self.scope['user'] == AnonymousUser():
        #     raise DenyConnection("Invalid User")
        await self.channel_layer.group_add(
            self.order_name,
            self.channel_name
        )
        # If invalid order id then deny the connection.
        try:
            self.order = await fetch_order(self.order_id)
        except ObjectDoesNotExist:
            raise DenyConnection("Invalid Order Id")
        await self.accept()

    async def receive(self, text_data):

        try:
            tracking_id = json.loads(text_data).get('tracking_id')
            await self.channel_layer.group_send(
                self.order_name,
                {
                    'type': 'fetch_order_location',
                    'orer_id': self.order_id,
                    'tracking_id': tracking_id,
                }
            )
        except Exception:
            pass
        

    async def fetch_order_location(self, event):
        tracking_id = event['tracking_id']
        is_successful = False
        message = None
        lat = long = None

        db_tracking_id = await get_tracking_id(self)
        if tracking_id == db_tracking_id:
            lat, long = await fetch_current_loc(self)
            message = 'Fetch succesful'
            is_successful = True
        else:
            message = 'Invalid tracking id'
            is_successful = False
            
        data = {
            'success': is_successful,
            'message': message,
            'order_location': {
                'lat': lat,
                'long': long
            }  
            }

        text_data = json.dumps(data)
        
        await self.send(text_data)

    async def websocket_disconnect(self, message):
            # Leave room group
            await self.channel_layer.group_discard(
                self.order_name,
                self.channel_name
            )


class PharmacyReceivedOrders(AsyncWebsocketConsumer):

    async def connect(self):
        self.pharmacy_id = self.scope['url_route']['kwargs']['pharmacy_id']
        self.pharmacy_name = f'Pharmacy_{self.pharmacy_id}'
     
        await self.channel_layer.group_add(
            self.pharmacy_name,
            self.channel_name
        )
        # If invalid pharmacy id then deny the connection.
        try:
            self.pharmacy = await fetch_pharmacy(self.pharmacy_id)
        except ObjectDoesNotExist:
            raise DenyConnection("Invalid pharmacy Id")
        await self.accept()

    async def receive(self, text_data):

        try:
            security_code = json.loads(text_data).get('security_code')
            await self.channel_layer.group_send(
                self.pharmacy_name,
                {
                    'type': 'fetch_pharmacy_unaccepted_orders',
                    'pharmacy_id': self.pharmacy_id,
                    'security_code': security_code,
                }
            )
        except Exception:
            pass


    async def fetch_pharmacy_unaccepted_orders(self, event):
        security_code = event['security_code']
        is_successful = False
        message = None
        orders = []

        db_security_code = await get_pharmacy_security_code(self)
        if security_code == db_security_code:
            orders = await fetch_pharmacy_orders(self)
            message = 'Fetch succesful'
            is_successful = True
        else:
            message = 'Invalid pharmacy id'
            is_successful = False
            
        data = {
            'success': is_successful,
            'message': message,
            'orders': orders
            }

        text_data = json.dumps(data)
        await self.send(text_data)

    async def websocket_disconnect(self, message):

            await self.channel_layer.group_discard(
                self.pharmacy_name,
                self.channel_name
            ) 


class RiderReceivedOrders(AsyncWebsocketConsumer):

    async def connect(self):
        self.rider_id = self.scope['url_route']['kwargs']['rider_id']
        self.rider_name = f'Rider_{self.rider_id}'
     
        await self.channel_layer.group_add(
            self.rider_name,
            self.channel_name
        )

        try:
            self.rider = await fetch_rider(self.rider_id)
        except ObjectDoesNotExist:
            raise DenyConnection("Invalid Rider Id")
        await self.accept()

    async def receive(self, text_data):

        try:
            security_code = json.loads(text_data).get('security_code')
            await self.channel_layer.group_send(
                self.rider_name,
                {
                    'type': 'fetch_unaccepted_orders',
                    'rider_id': self.rider_id,
                    'security_code': security_code,
                }
            )
        except Exception:
            pass
        

    async def fetch_unaccepted_orders(self, event):
        security_code = event['security_code']
        is_successful = False
        message = None
        orders = []

        db_security_code = await get_rider_security_code(self)
        if security_code == db_security_code:
            orders = await fetch_riders_orders(self)
            message = 'Fetch succesful'
            is_successful = True
        else:
            message = 'Invalid security code'
            is_successful = False
            
        data = {
            'success': is_successful,
            'message': message,
            'orders': orders
            }

        text_data = json.dumps(data)
        
        await self.send(text_data)

    async def websocket_disconnect(self, message):
            # Leave room group
            await self.channel_layer.group_discard(
                self.rider_name,
                self.channel_name
            ) 
