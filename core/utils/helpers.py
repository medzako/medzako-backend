from geopy.distance import distance
import random
import string
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from channels.db import database_sync_to_async

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


class JWTAuth:

    def __init__(self, *args, **kwargs):
        self.user_model = get_user_model()

    async def authenticate(self, raw_token):

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token)

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        })

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user


@database_sync_to_async
def get_user(raw_token):
    jwt_auth = JWTAuth()
    return jwt_auth.authenticate(raw_token)


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))  
