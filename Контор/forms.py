from django import forms
from Контор.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ApartmentBlockForm(forms.ModelForm):
    class Meta:
        model = ApartmentBlock
        fields = ['number_of_stories', 'units_per_story', 'admin']  # Include the admin field

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']  # Add more fields if needed

class ResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = ['name', 'phone_number', 'password', 'story', 'unit']

class EditResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = ['name', 'phone_number', 'story', 'unit']

class UtilityRatesForm(forms.ModelForm):
    class Meta:
        model = UtilityRates
        fields = ['water_cubic_meter', 'fixed', 'taxes', 'electricity_base', 'electricity_excess', 'fixed_e', 'taxes_e', 'monthly']

class MonthlyUsageForm(forms.ModelForm):
    class Meta:
        model = MonthlyUsage
        fields = ['water', 'electricity', 'monthly_payment', 'fees', 'recorded_at']

class UtilitiesForm(forms.ModelForm):
    class Meta:
        model = Utilities
        fields = ['water_bill', 'electricity_bill', 'monthly_payment', 'fees']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['readonly'] = 'readonly'


