from django.contrib import admin
from .models import Medication, Category, Pharmacy, PharmacyStock

admin.site.register(Medication)
admin.site.register(Category)
admin.site.register(Pharmacy)
admin.site.register(PharmacyStock)
