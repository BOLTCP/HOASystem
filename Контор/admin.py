from django.contrib import admin
from .models import Admin, ApartmentBlock  # Remove Resident if it doesn't exist

admin.site.register(Admin)
admin.site.register(ApartmentBlock)