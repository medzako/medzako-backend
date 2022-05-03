from django.db import models
from cloudinary.models import CloudinaryField

from core.models import AbstractBaseModel
from core.utils.constants import PAYMENTS, RECEIVED, STATUSES


class Order(AbstractBaseModel):
    customer = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True
    )   
    total_price = models.DecimalField(max_digits=9, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    payment = models.OneToOneField(
        'order.Payment',
        on_delete=models.SET_NULL,
        related_name='order',
        null=True
    ),
    pharmacy = models.ForeignKey(
        'medication.Pharmacy',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True
    )
    status = models.CharField(
        choices=STATUSES,
        default=RECEIVED,
        max_length=30
    )
    is_payment_complete = models.BooleanField(default=False)
    is_rider_found = models.BooleanField(default=False)

    prescription = models.OneToOneField(
        'order.Image',
        related_name='order',
        on_delete=models.SET_NULL,
        null=True
    )

    delivery_fee = models.DecimalField(max_digits=9, decimal_places=2)

    location = models.ForeignKey(
        'order.Location',
        on_delete=models.CASCADE,
        related_name='location_orders',
        null=True
    )
    action_reason = models.TextField(null=True)
    rider = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        related_name='rider_orders',
        null=True
    )

    def __str__(self):
        return f'{self.customer.first_name} Order: {self.pk}'


class OrderItem(AbstractBaseModel):
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.CASCADE,
        related_name='items',
    )
    medication = models.ForeignKey(
        'medication.Medication', 
        on_delete=models.CASCADE, 
        related_name='order'
        )
    quantity =  models.IntegerField()

    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f'{self.medication.name} Item: {self.pk}'


class Payment(AbstractBaseModel):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    payment_type = models.CharField(max_length=30)
    event_id = models.CharField(max_length=50, unique=True)
    charged_amount = models.DecimalField(max_digits=6, decimal_places=2)
    customer_email = models.EmailField()
    customer_phone_no = models.CharField(max_length=30)
    status = models.CharField(max_length=30)



class Location(models.Model):
    customer = models.ForeignKey(
        'authentication.User',
        related_name='locations',
        on_delete=models.CASCADE
    )
    lat = models.DecimalField(max_digits=45, decimal_places=40)
    long = models.DecimalField(max_digits=45, decimal_places=40)
    general_area = models.CharField(max_length=50)
    apartment_name = models.CharField(max_length=50, null=True)
    room_no = models.CharField(max_length=20, null=True)


class Image(models.Model):
    image = CloudinaryField('image')


class CurrentOrderLocation(AbstractBaseModel):
    order = models.OneToOneField(
        'order.Order',
        on_delete=models.CASCADE,
        related_name='tracking_object',
    )
    tracking_id = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=45, decimal_places=40)
    long = models.DecimalField(max_digits=45, decimal_places=40)

class OrderEarning(AbstractBaseModel):
    order = models.OneToOneField(
        'order.Order',
        on_delete=models.SET_NULL,
        related_name='earning',
        null=True
    )
    pharmacy = models.ForeignKey(
        'medication.Pharmacy',
        on_delete=models.SET_NULL,
        related_name='pharmacy_earnings',
        null=True
    )
    rider = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        related_name='rider_earnings',
        null=True
    )

    rider_earning = models.DecimalField(max_digits=9, decimal_places=2)
    pharmacy_earning = models.DecimalField(max_digits=9, decimal_places=2)


class RiderHistory(AbstractBaseModel):
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.SET_NULL,
        related_name='riders_history',
        null=True
    )
    rider = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        related_name='riders_history',
        null=True
    )
    is_accepted = models.BooleanField(null=True)
