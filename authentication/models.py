from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)

from django.contrib.auth import password_validation


from rest_framework.exceptions import ValidationError
from core.utils.validators import validate_phone_number, validate_required_arguments


from core.models import AbstractBaseModel

class UserManager(BaseUserManager):
    '''
    Custom manager to handle the User model methods.
    '''

    def create_user(
        self, full_name=None, password=None, phone_no=None, email=None, **kwargs
    ):
        REQUIRED_ARGS = ('full_name', 'password', 'phone_no')
        validate_required_arguments(
            {
                'full_name': full_name,
                'password': password,
                'phone_no': phone_no,
                'email': email
            },
            REQUIRED_ARGS,
        )
        # ensure that the passwords are strong enough.
        try:
            password_validation.validate_password(password)
        except ValidationError as exc:
            # return error accessible in the appropriate field, ie password
            raise ValidationError({'password': exc.messages}) from exc
        
        validate_phone_number(phone_no)

        user = self.model(
            full_name=full_name,
            email=self.normalize_email(email),
            phone_no=phone_no,
            **kwargs
        )
        # ensure phone number and all fields are valid.
        user.clean()
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, full_name=None, password=None, phone_no=None, email=None, **kwargs
    ):
        REQUIRED_ARGS = ('full_name', 'password', 'phone_no', 'email')
        validate_required_arguments(
            {
                'full_name': full_name,
                'password': password,
                'phone_no': phone_no,
                'email': email
            },
            REQUIRED_ARGS,
        )
        # ensure that the passwords are strong enough.
        try:
            password_validation.validate_password(password)
        except ValidationError as exc:
            # return error accessible in the appropriate field, ie password
            raise ValidationError({'password': exc.messages}) from exc
        
        validate_phone_number(phone_no)

        user = self.model(
            full_name=full_name,
            email=self.normalize_email(email),
            phone_no=phone_no,
            **kwargs
        )
        # ensure phone number and all fields are valid.
        user.clean()
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff=True
        user.save()
        return user


class User(AbstractBaseModel, AbstractBaseUser, PermissionsMixin):
    '''
    Custom user model to be used throughout the application.
    '''

    full_name = models.CharField(max_length=150)
    phone_no = models.CharField(unique=True, max_length=50, validators=[validate_phone_number])
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.full_name}'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'id_no']

    objects = UserManager()
