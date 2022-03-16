# Built in imports.
import json
from telnetlib import STATUS
from asgiref.sync import sync_to_async
# Third Party imports.
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
# Django imports.
from django.core.exceptions import ObjectDoesNotExist

from core.utils.consumer_database_helpers import *

class RiderOrderTrackingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.order_name = f'Order_{self.order_id}'

        await self.channel_layer.group_add(
            self.order_name,
            self.channel_name
        )
       
        try:
            self.order = await fetch_order(self.order_id)
        except ObjectDoesNotExist:
            raise DenyConnection("Invalid Order Id")
        await self.accept()

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
            order_location = data.get('order_location')
            method = data.get('method', 'fetch')
            tracking_id = data.get('tracking_id')
            await self.channel_layer.group_send(
                self.order_name,
                {
                    'type': 'order_location',
                    'tracking_id': tracking_id,
                    'order_id': self.order_id,
                    'order_location': order_location,
                    'method': method
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
        method = event['method']

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
            if method == 'update':
                await update_tracking_loc(self, lat=lat, long=long)
                messages.append('Update succesful')
            elif method =='fetch':
                lat, long = await fetch_current_loc(self)
                messages.append('Fetch succesful')

            is_successful = True
        else:
            messages.append('Invalid tracking id')
            is_successful = False

        data = {
            'is_successful': is_successful,
            'messages': messages,
            'order_location': {
                'lat': lat,
                'long': long
            },
            'method': method

        }

        text_data = json.dumps(data)

      
        await self.send(text_data)

    async def websocket_disconnect(self, message):
           
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


class Notifications(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.user_name = f'User{self.user.pk}'
     
        await self.channel_layer.group_add(
            self.user_name,
            self.channel_name
        )
    
        await self.accept()

    async def receive(self, text_data):
        payload = json.loads(text_data)
        data = payload.get('data')
        notification_type = payload.get('notification_type')

        try:
            await self.channel_layer.group_send(
                self.user_name,
                {
                    'type': 'get_notifications',
                    'data': data,
                    'notification_type': notification_type
                }
            )
        except Exception:
            pass
        

    async def get_notifications(self, event):
      
        event.pop('type')

        text_data = json.dumps(event)
        
        await self.send(text_data)


    async def websocket_disconnect(self, message):
            # Leave room group
            await self.channel_layer.group_discard(
                self.user_name,
                self.channel_name
            ) 
