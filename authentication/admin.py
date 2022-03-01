from django.contrib import admin
from .models import PharmacyLicense, RiderLicense, User,CustomerProfile, PharmacistProfile, RiderProfile

admin.site.register(PharmacyLicense)
admin.site.register(RiderLicense)
admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(PharmacistProfile)
admin.site.register(RiderProfile)
