import json
from geopy.distance import distance
import random
import string
from decimal import Decimal
import logging

from django.conf import settings
from rest_framework.exceptions import ValidationError
from firebase_admin.messaging import Message, Notification

from fcm_django.models import FCMDevice
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from core.utils.constants import RIDER
from medzako.celery import app

import secrets



logger = logging.getLogger(__name__)

def logInfo(data):
    logger.info(data)

def format_fcm_data(data):
    newData = {}
    for key in data:
        newData[str(key)] = str(data[key])
    return newData

def raise_validation_error(message=None):
    raise ValidationError(message)

def get_coordinate_distance(cood1, cood2):
    """Return coordinate to cooardinate distance in KM"""
    return distance(cood1, cood2).km

def add_distance_to_pharmacy(pharmacy_dict, cood2):
    pharmacy_dict = dict(pharmacy_dict)
    lat1 = Decimal(pharmacy_dict['location_lat'])
    long1 = Decimal(pharmacy_dict['location_long'])
    distance = get_coordinate_distance((lat1, long1), cood2)
    pharmacy_dict['distance'] = distance
    return pharmacy_dict


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))

@app.task()
def get_rider(destination, order=None):
    from authentication.models import CurrentRiderLocation, User
    from order.models import RiderHistory

    maximum_radius = settings.MAXIMUM_RADIUS
    rider_locations = CurrentRiderLocation.objects.filter(rider__rider_profile__is_online=True)
    riders_distances = [(rider_location.rider, get_coordinate_distance((rider_location.lat, rider_location.long), destination)) for rider_location in rider_locations]
    riders_distances.sort(key=lambda x: x[1])
    for riders_distance in riders_distances:
        has_already_rejected = False
        if order:
            has_already_rejected = RiderHistory.objects.filter(rider=riders_distance[0], is_accepted=None).exists()
        
        has_pending = RiderHistory.objects.filter(order=order, rider=riders_distance[0]).exists()
        if riders_distance[1] < maximum_radius and not has_already_rejected and not has_pending:
            return riders_distance[0]

    return User.objects.filter(user_type=RIDER, pk=19).first()


@app.task()
def sendFCMMessage(users, data, title, body, image_url=""): 
    """Send FCM data"""  
    data = format_fcm_data(data)

    for user in users: 
        devices = FCMDevice.objects.filter(user=user)
        messageObj = Message(
            data=data,
            notification=Notification(title=title, body=body, image=image_url)
        )
        logInfo(devices.send_message(messageObj))


@app.task()
def sendFCMNotification(users, title, body, image_url=""):
    """Send FCM notifications"""
    mesageObj = Message(notification=Notification(title=title, body=body, image=image_url))
    for user in users:
        devices = FCMDevice.objects.filter(user=user)
        logger.info(devices.send_message(mesageObj))


def parseStockData(stockData):
    categories = {}
    category_id_mapping = {}
    category_listing = []


    for stockItem in stockData:
        in_stock = category = stockItem['in_stock']
        if in_stock:
            category = stockItem['medication']['category']['name']
            category_id = stockItem['medication']['category']['id']
            stockItem['medication']['category'] = category_id
            category_id_mapping[category] = category_id
            stockItem['medication']['price'] = stockItem['price']

            if categories.get(category):
                categories.append(stockItem['medication'])
            else:
                categories[category] = [stockItem['medication']]
    
    for category_name in categories.keys():
        category = {
            'name': category_name,
            'id': category_id_mapping[category_name],
            'medication': categories[category_name]
        }
        category_listing.append(category)

    return category_listing
            

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_email_verified))


def generate_token(length):
    """Generate token
    args:
        lenght - integer
    returns: string
    """
    first = random.choice(range(1, 10))
    leftover = set(range(10)) - {first}
    rest = random.sample(leftover, length-1)
    digits = [first] + rest
    return str(digits)

def get_pharmacy_users(pharmacy):
    user_profiles = pharmacy.user_profiles.all()
    return [profile.user for profile in user_profiles]

def send_order_pharmacy_notifications(order, title = 'Rider found', message=None):
    from order.serializers import FCMOrderSerializer

    if not message: 
        message = f'The rider {order.rider.first_name} {order.rider.second_name} found for order no. {order.id}'
    order_serializer = FCMOrderSerializer(instance=order)
    users = get_pharmacy_users(order.pharmacy)

    sendFCMMessage.delay(users, order_serializer.data, title, message)


def send_order_customer_notifications(order, title = 'Rider found', message=None):
    from order.serializers import FCMOrderSerializer

    if not message: 
        message = f'The rider {order.rider.first_name} {order.rider.second_name} found for order no. {order.id}'
    order_serializer = FCMOrderSerializer(instance=order)

    sendFCMMessage.delay([order.customer], order_serializer.data, title, message)


def send_order_rider_notifications(user, order, history_id, title='New Order', message=None):
    from order.serializers import FCMOrderSerializer

    if not message:
        message = f'You have been assigned to deliver order no. {order.id} from {order.pharmacy.name} pharmacy'
    
    order_serializer = FCMOrderSerializer(instance=order)
    data = order_serializer.data
    data['rider_response_id'] = history_id

    sendFCMMessage.delay([user], data, title, message)
