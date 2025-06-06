from django import forms
from Контор.models import Resident
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput())
