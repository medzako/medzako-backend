from geopy.distance import distance
from decimal import Decimal
from rest_framework.exceptions import ValidationError

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
