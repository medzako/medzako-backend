from decimal import Decimal
from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
from core.utils.constants import MEDICATION_TYPE

from core.utils.validators import validate_phone_number
from core.models import AbstractBaseModel


class Pharmacy(AbstractBaseModel):
    name = models.CharField(max_length=100)
    location_lat = models.DecimalField(max_digits=45, decimal_places=40)
    location_long = models.DecimalField(max_digits=45, decimal_places=40)
    contact_no = models.CharField(unique=True, max_length=50, validators=[validate_phone_number])
    location_name = models.CharField(max_length=50, null=True)
    image = CloudinaryField('image')
    rating = models.DecimalField(default=0, decimal_places=1, max_digits=1)
    completed_orders = models.IntegerField(default=0)

    @property
    def get_rating(self):
        ratings = self.ratings.all()
        total_rating = 0

        for rating in ratings:
            total_rating += rating.rating
        if ratings:
            rating = total_rating/len(ratings)
            return Decimal(round(rating, 1))
        return 0

    def save(self, *args, **kwargs):
        self.rating = self.get_rating
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Medication(AbstractBaseModel):
    name = models.CharField(max_length=100)
    category =  models.ForeignKey(
        'medication.Category',
        related_name ='medications',
        on_delete=models.SET_NULL,
        null=True
    )
    description = models.TextField(blank=True)
    usage = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    type  = models.CharField(max_length=50, choices=MEDICATION_TYPE)
    image = CloudinaryField('image')
    scientific_name = models.CharField(max_length=50, null=True)
    units_moved = models.IntegerField(default=0)
    measurement = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    scientific_name = models.CharField(max_length=50, null=True)
    image = CloudinaryField('image')

    def __str__(self):
        return self.name


class PharmacyStock(AbstractBaseModel):
    medication = models.ForeignKey(
        'medication.Medication',
         related_name='stock',
         on_delete=models.CASCADE,
         )
    pharmacy = models.ForeignKey(
        'medication.Pharmacy', 
        related_name='available_stock',
        on_delete=models.CASCADE
        )
    in_stock = models.BooleanField(default=False)
    price = models.DecimalField(decimal_places=2, max_digits=9, null=True)


    def __str__(self):
        return f'{self.pharmacy.name}-{self.medication.name}'

    class Meta:
        unique_together = ['medication', 'pharmacy']


class Rating(AbstractBaseModel):
    pharmacy = models.ForeignKey(
        'medication.Pharmacy', 
        related_name='ratings',
        on_delete=models.CASCADE
        )
    customer = models.ForeignKey(
        'authentication.User',
        related_name='rating',
        on_delete=models.CASCADE
    )
    rating = models.IntegerField()
