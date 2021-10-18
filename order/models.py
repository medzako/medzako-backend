from re import match
from django.db import models

from core.models import AbstractBaseModel
from core.utils.constants import PAYMENTS

class Order(AbstractBaseModel):
    customer = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True
    )
    is_completed = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=9, decimal_places=2)
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
    is_payment_complete = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.customer.full_name} Order: {self.pk}'


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

    def __str__(self):
        return f'{self.medication.name} Item: {self.pk}'


class Payment(AbstractBaseModel):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    payment_type = models.CharField(choices=PAYMENTS, max_length=50)
