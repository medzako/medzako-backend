from django.db import models
from cloudinary.models import CloudinaryField
from core.utils.constants import MEDICATION_TYPE

from core.utils.validators import validate_phone_number
from core.models import AbstractBaseModel


class Pharmacy(AbstractBaseModel):
    name = models.CharField(max_length=100)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6)
    location_long = models.DecimalField(max_digits=9, decimal_places=6)
    contact_no = models.CharField(unique=True, max_length=50, validators=[validate_phone_number])
    medication = models.ManyToManyField('medication.Medication', related_name='pharmacies')
    location_name = models.CharField(max_length=50, null=True)
    image = CloudinaryField('image')

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
    type  = models.CharField(max_length=50, choices=MEDICATION_TYPE)
    image = CloudinaryField('image')
    scientific_name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(AbstractBaseModel):
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
    stock = models.IntegerField(default=0)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    def __str__(self):
        return f'{self.pharmacy.name}-{self.medication.name}'
