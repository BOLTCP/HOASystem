from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect

def dashboardGlobal(request):
    return render(request, 'dashboardGlobal.html')

def login_options(request):
    return render(request, 'login_options.html')
