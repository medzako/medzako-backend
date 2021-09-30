from cloudinary import uploader, api_client, config

from rest_framework.exceptions import ValidationError

def raise_validation_error(message=None):
    raise ValidationError(message)
