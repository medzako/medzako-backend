# Built in imports.
import json
from asgiref.sync import sync_to_async
# Third Party imports.
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
# Django imports.
from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async

# Local imports.
from .models import Order

@database_sync_to_async
def fetch_order(order_id):
    return Order.objects.get(pk=order_id)

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
def get_tracking_id(consumer_obj):
    return consumer_obj.order.tracking_object.tracking_id


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
            