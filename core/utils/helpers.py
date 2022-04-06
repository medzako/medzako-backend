from geopy.distance import distance
import random
import string
from decimal import Decimal

from django.conf import settings
from rest_framework.exceptions import ValidationError
from firebase_admin.messaging import Message, Notification

from fcm_django.models import FCMDevice
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from medzako.celery import app


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
def get_rider(destination):
    from authentication.models import CurrentRiderLocation

    maximum_radius = settings.MAXIMUM_RADIUS
    rider_locations = CurrentRiderLocation.objects.all()
    riders_distances = [(rider_location.rider, get_coordinate_distance((rider_location.lat, rider_location.long), destination)) for rider_location in rider_locations]
    riders_distances.sort(key=lambda x: x[1])
    if riders_distances[0][1] < maximum_radius:
        return riders_distances[0]


@app.task()
def sendFCMMessage(users, data): 
    """Send FCM data"""  
    for user in users: 
        devices = FCMDevice.objects.filter(user=user)
        messageObj = Message(
            data=data
        )
        devices.send_message(messageObj)


@app.task()
def sendFCMNotification(users, title, body, image_url=""):
    """Send FCM notifications"""
    mesageObj = Message(notification=Notification(title=title, body=body, image=image_url))
    for user in users:
        devices = FCMDevice.objects.filter(user=user)
        devices.send_message(mesageObj)


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


def send_order_pharmacy_notifications(order, title = 'Rider found'):
    from order.serializers import FCMOrderSerializer

    message = f'The rider {order.rider.first_name} {order.rider.second_name} found for order no. {order.order.id}'

    user_profiles = order.pharmacy.user_profiles.all()
    users = [profile.user for profile in user_profiles]
    order_serializer = FCMOrderSerializer(instance=order)


    sendFCMNotification.delay(users, title, message)
    sendFCMMessage.delay(users, order_serializer.data)


def send_order_rider_notifications(user, order, history_id):
    from order.serializers import FCMOrderSerializer

    message = f'You have been assigned to deliver order no. {order.id} from {order.pharmacy.name} pharmacy'
    title = 'New Order'
    order_serializer = FCMOrderSerializer(instance=order)
    data = order_serializer.data
    data['rider_response_id'] = history_id

    sendFCMNotification.delay([user], title, message)
    sendFCMMessage.delay([user], data)


generate_token = TokenGenerator()
