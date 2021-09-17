from core.utils.helpers import raise_validation_error
from rest_framework.exceptions import ValidationError
import re


def validate_phone_number(phone):
    """
    Validate an phone number.
    - Number must contain no spaces
    - Number must be of correct length
    - Number must have no letters

    https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers

    return True if number is valid. False otherwise.
    """

    regex_pattern = r"^254\d{9}$"

    match = re.search(regex_pattern, phone)

    if not match:
        raise_validation_error('Invalid phone number. Use 254XXXXXXXXX format.')
    else:
        return True


def validate_required_arguments(kwargs, required_args):
    """
    This function takes a dictionary that contains arguments and their values. The second parameter is a list or tuple which contains arguments that:
        - Must be present in kwargs.
        - Must be truthy

    Consider I have a function that accepts keyword arguments.
        f(a=None, b=None, c=None):
            pass
    If all keyword arguments should be truthy at runtime, we would have to
    create loops to check if each condition is truthy:
        ...
        if not a:
            raise Exception
        ...etc

    This function loops through the passed kwargs(dict) and ensures that they are not empty and that they are truthy.
    returns kwargs or raises Django Validation Error.
    """

    for arg in required_args:
        if arg not in kwargs.keys():  # arg must be present
            raise ValidationError({arg: "This field is required."})
        elif not kwargs.get(arg):  # arg must be truthy
            raise ValidationError({arg: "This field cannot be empty."})
    return kwargs
