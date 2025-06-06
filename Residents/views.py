from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from API.models import Payment
from Контор.models import Resident, MonthlyUsage, Utilities, UtilityRates, UsageHistory, PaymentHistory
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            try:
                resident = Resident.objects.get(name=name, phone_number=phone_number)

                if resident.password == password:
                    return redirect('user_dashboard', resident_id = resident.id)  
                else:
                    return render(request, 'user_login.html', {'form': form, 'error': 'Invalid password.'})
            except Resident.DoesNotExist:
                return render(request, 'user_login.html', {'form': form, 'error': 'User not found in HOA residents.'})
                
    else:
        form = LoginForm()
    
    return render(request, 'user_login.html', {'form': form})

def user_dashboard(request, resident_id):
    resident = get_object_or_404(Resident, id=resident_id)
    usage = MonthlyUsage.objects.filter(id=resident_id).last()
    utilities = Utilities.objects.filter(resident_id=resident_id).last()
    payment_status = PaymentHistory.objects.filter(resident_id=resident_id).last()
    remainder = Payment.objects.filter(user_id=resident_id).last()
    rates = get_object_or_404(UtilityRates, id=1)
    try:
        total = utilities.water_bill + utilities.electricity_bill + utilities.fees + utilities.monthly_payment
    except:
        total= 0

    context = {
        'resident': resident, 'usage' : usage, 'utilities': utilities, 'rates': rates, 'total': total, 'payment_status': payment_status, 'remainder': remainder
    }

    return render(request, 'user_dashboard.html', context)

def user_profile(request, resident_id):
    resident = get_object_or_404(Resident, id=resident_id)

    context = {

        'resident': resident,

    }

    return render(request, 'user_profile.html', context)

@login_required
def logout_confirmation_user(request, id ):
    return render(request, 'logout_confirmation_user.html', { 'id': id })

"""
def usage_history(request, id):

    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    history = UsageHistory.objects.filter(resident_id=id, recorded_at__gte=six_months_ago)

    return render(request, 'usage_history.html', { 'history': history })
"""

def usage_history(request, id):
    usage_history = UsageHistory.objects.filter(resident_id=id).values()


    context = {
        'usage_history': usage_history,
    }

    return render(request, 'usage_history.html', context)

def payment_history(request, id):
    current_payment = PaymentHistory.objects.filter(resident_id=id, payment_status__in=['pending', 'In Deficit']).order_by('-created_at').first()

    history = PaymentHistory.objects.filter(resident_id=id, payment_status__in=['Completed']).order_by('-created_at')
    print(history)
    if history:
        context = { 'resident_id': id, 'current_payment': current_payment, 'history': history }
    
    else:
        context = { 'resident_id': id, 'current_payment': current_payment }

    return render(request, 'payment_history.html', context)









