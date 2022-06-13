from datetime import datetime
from decimal import Decimal

from jwt import encode

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)

from django.contrib.auth import password_validation
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string

from rest_framework.exceptions import ValidationError

from cloudinary.models import CloudinaryField

from core.utils.constants import CUSTOMER, PHARMACIST, PHARMACY_LICENSES, RIDER, RIDER_LICENSES, USER_TYPES
from core.utils.helpers import generate_random_string, generate_token
from core.utils.validators import validate_phone_number, validate_required_arguments

from core.models import AbstractBaseModel

class UserManager(BaseUserManager):
    '''
    Custom manager to handle the User model methods.
    '''

    def create_user(
        self, first_name=None, second_name=None, password=None, phone_no=None, email=None, user_type=None, **kwargs
    ):
        REQUIRED_ARGS = ('first_name', 'second_name', 'password', 'phone_no')
        validate_required_arguments(
            {
                'first_name': first_name,
                'second_name': second_name,
                'password': password,
                'phone_no': phone_no,
                'email': email,
                'user_type': user_type
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
            first_name=first_name,
            second_name=second_name,
            email=self.normalize_email(email),
            phone_no=phone_no,
            user_type=user_type,
            **kwargs
        )
        # ensure phone number and all fields are valid.
        user.clean()
        user.set_password(password)
        user.save()
        self.create_profile(user_type, user)
        return user

    def create_profile(self, user_type, user):
        profile_mapper = {
            CUSTOMER: CustomerProfile,
            RIDER: RiderProfile,
            PHARMACIST: PharmacistProfile
        }

        profile = profile_mapper[user_type].objects.create(user=user)
        return profile

    def create_superuser(
        self, first_name=None, second_name=None,password=None, phone_no=None, email=None, **kwargs
    ):
        REQUIRED_ARGS = ('password', 'phone_no', 'email')
        validate_required_arguments(
            {
                'first_name': first_name,
                'second_name': second_name,
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
            first_name=first_name,
            second_name=second_name,
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
    phone_no = models.CharField(unique=True, max_length=50, validators=[validate_phone_number])
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    d_o_b = models.DateField(null=True)
    user_type = models.CharField(choices=USER_TYPES, max_length=30, default='customer')
    first_name = models.CharField(max_length=30, default='first')
    second_name = models.CharField(max_length=30, default='second')
   
    def __str__(self):
        return f'{self.email}'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'second_name', 'phone_no']

    objects = UserManager()


class RiderProfile(AbstractBaseModel):
    """
    Rider information
    """
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE, 
        related_name='rider_profile',
        null=True)
    is_approved = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    rating = models.DecimalField(default=0, decimal_places=1, max_digits=1)

    @property
    def get_rating(self):
        ratings = self.user.rider_ratings.all()
        total_rating = 0

        for rating in ratings:
            total_rating += rating.rating
        if ratings:
            rating = total_rating/len(ratings)
            return Decimal(round(rating, 1))
        return 0

    def save(self, *args, **kwargs) -> None:
        self.rating = self.get_rating
        return super().save(*args, **kwargs)

    

class CustomerProfile(AbstractBaseModel):
    """
    Customer information
    """
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE, 
        related_name='customer_profile',
        null=True)


class PharmacistProfile(AbstractBaseModel):
    """
    Pharmacist information
    """
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE, 
        related_name='pharmacist_profile'
        )
    pharmacy = models.ForeignKey(
        'medication.Pharmacy',
        on_delete=models.CASCADE,
        related_name='user_profiles',
        null=True
    )
    is_approved = models.BooleanField(default=False)


class PharmacyLicense(AbstractBaseModel):
    pharmacy = models.ForeignKey(
        'medication.Pharmacy',
        on_delete=models.CASCADE, 
        related_name='licenses'
    )
    license_image = CloudinaryField('image')
    name = models.CharField(max_length=50, choices=PHARMACY_LICENSES)

    def __str__(self) -> str:
        return f'{self.name} Pharmacy id: {self.pharmacy.pk} Pharmacy name: {self.pharmacy.name}'


class RiderLicense(AbstractBaseModel):
    rider_profile = models.ForeignKey(
        'RiderProfile',
        on_delete=models.CASCADE, 
        related_name='rider_licenses',
        null=True
    )
    license_image = CloudinaryField('image')
    name = models.CharField(max_length=50, choices=RIDER_LICENSES)


class RiderProfileImage(AbstractBaseModel):
    rider_profile = models.OneToOneField(
        'RiderProfile',
        on_delete=models.CASCADE, 
        related_name='profile_pic',
        null=True
    )
    profile_picture = CloudinaryField('image')


class CurrentRiderLocation(AbstractBaseModel):
    rider = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='current_location',
    )
    lat = models.DecimalField(max_digits=45, decimal_places=40, null=True)
    long = models.DecimalField(max_digits=45, decimal_places=40, null=True)


class ResetPasswordToken(models.Model):

    @staticmethod
    def generate_key():
        """ generates a pseudo random 4 digit code"""
        return generate_token(4)

    user = models.ForeignKey(
        User,
        related_name='password_reset_tokens',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    key = models.CharField(
        max_length=10,
        db_index=True,
        unique=True
    )
   
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ResetPasswordToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)


@receiver(post_save, sender=User, dispatch_uid="create_user_varification_token")
def send_activation_email(sender, instance, **kwargs):
    if instance.is_superuser:
        return

    subject = "Medzako email verification link"
    payload = { 
            "email": instance.email,
            "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
             }
    token = encode(payload, settings.SECRET_KEY)
    print(token)
    message = settings.FRONTEND_LINK + '/verify/' + token
    email_from = settings.COMPANY_EMAIL
    receipient_list = [instance.email]
    send_mail( subject, message, email_from, receipient_list )


@receiver(post_save, sender=ResetPasswordToken, dispatch_uid="send-reset-email")
def password_reset_token_created(sender, instance, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': instance.user,
        'name': instance.user.first_name,
        'email': instance.user.email,
        'reset_password_code': instance.key
    }

    # render email text
    email_html_message = render_to_string('authentication/reset_password_template.html', context)
    email_plaintext_message = render_to_string('authentication/reset_password_template.txt', context)
    subject = "Medzako Password Reset"
    send_mail(subject, email_plaintext_message, settings.COMPANY_EMAIL, [instance.user.email], html_message=email_html_message)
