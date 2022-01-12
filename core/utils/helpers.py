from geopy.distance import distance
import random
import string
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from medzako.celery import app

def raise_validation_error(message=None):
    raise ValidationError(message)


def get_coordinate_distance(cood1, cood2):
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

app.task()
def get_rider(destination, rider_locations, maximum_radius):
    riders_distances = [(rider_location.rider, get_coordinate_distance((rider_location.lat, rider_location.long), destination)) for rider_location in rider_locations]
    riders_distances.sort(key=lambda x: x[1])
    if riders_distances[0][1] < maximum_radius:
        return riders_distances[0]
