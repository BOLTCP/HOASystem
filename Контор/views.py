from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Admin.objects.create(user=user)  
            login(request, user)  
            return redirect('dashboard') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        hashed_password = make_password(password)
        print(hashed_password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user) 
            user = get_object_or_404(User, username=username)
            return redirect('dashboard', user.id)  
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid username or password.'})
    return render(request, 'admin_login.html')

def dashboard(request, id):
    blocks = ApartmentBlock.objects.filter(admin_id=id)
    context = {
        'blocks': blocks,
        'id': id,
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_apartment_block(request, id):
    if request.method == 'POST':
        form = ApartmentBlockForm(request.POST)
        if form.is_valid():
           
            apartment_block = form.save(commit=False)
            apartment_block.admin = request.user  
            apartment_block.save()
            return redirect('dashboard', id)  
    else:
        form = ApartmentBlockForm()
    
    return render(request, 'add_apartment_block.html', {'form': form})

def edit_apartment_block(request, block_id, id):
   
    block = get_object_or_404(ApartmentBlock, block_id=block_id)
    
    try:
        if request.method == 'POST':
            form = ApartmentBlockForm(request.POST, instance=block)
            if form.is_valid():
                form.save()  
                messages.success(request, 'Apartment updated successfully.')
                return redirect('dashboard', id) 
    except IntegrityError:
                    messages.error(request, 'This story and unit combination is already occupied!')
        
    form = ApartmentBlockForm(instance=block)

    return render(request, 'edit_apartment_block.html', {
        'form': form,
        'number_of_stories' : block.number_of_stories,
        'units_per_story' : block.units_per_story,
    })

@login_required
def view_apartment_block(request, block_id, id):
    block = get_object_or_404(ApartmentBlock, block_id=block_id)
    residents = Resident.objects.filter(apartment_block=block).values()
    story = block.number_of_stories
    units = block.units_per_story
    
    for resident in residents:
        resident['unit'] = resident['unit'] % 100 
    
    form = ResidentForm()

    context = {
        'form' : form,
        'block': block,
        'id': id,
        'block_id' : block_id,
        'number_of_stories' : story,
        'units_per_story' : units,
        'residents': residents,
    }
    return render(request, 'view_apartment_block.html', context)

@login_required
def add_resident(request, block_id):
    if request.method == 'POST':
        form = ResidentForm(request.POST)
        if form.is_valid():
            resident = form.save(commit=False)  
            resident.apartment_block = get_object_or_404(ApartmentBlock, block_id=block_id)

            username = form.cleaned_data['name'] 
            password = form.cleaned_data['password'] 

            try:
                existing = Resident.objects.filter(unit=resident.story * 100 + resident.unit, story=resident.story)
                if len(existing) != 0 :
                    return JsonResponse({
                    'success': False,
                    'errors': 'Username or email already exists!',
                    })
                else:
                    user = User.objects.create_user(username, password)
                    resident.user = user  
                    resident.save() 
                    return JsonResponse({
                        'success': True,
                        'message': 'Resident added successfully.',
                        'resident': {
                            'name': resident.name,
                            'phone_number': resident.phone_number,
                            'story': resident.story,
                            'unit': resident.unit,
                        },
                    })
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'errors': 'Username or email already exists!',
                })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = ResidentForm()
    return render(request, 'add_resident.html', {'form': form, 'block_id': block_id})
            

def edit_resident(request, resident_id, block_id):
    block =  get_object_or_404(ApartmentBlock, block_id=block_id)
    resident = get_object_or_404(Resident, id=resident_id)
    
    if request.method == 'POST':
        form = EditResidentForm(request.POST, instance=resident)
        
        if form.is_valid():
            try:
                existing = Resident.objects.filter(unit=resident.story * 100 + resident.unit, story=resident.story)
                if len(existing) == 0:
                    print(existing)
                else:
                    print(len(existing))
                resident.unit = resident.story * 100  + resident.unit
                form.password=resident.password
                form.save()
                messages.success(request, 'Resident updated successfully.')
                return redirect('view_apartment_block', block_id=block_id)
            except IntegrityError:
                messages.error(request, 'This story and unit combination is already occupied!')
        else:
            
            messages.error(request, f"Form is invalid: {form.errors}")

    else:    
        form = EditResidentForm(instance=resident)

    
    return render(request, 'edit_resident.html', {
        'form': form,
        'resident': resident,
        'block': block,
    })


@login_required
def delete_resident(request, resident_id, block_id):
    block = get_object_or_404(ApartmentBlock, block_id=block_id)
    resident = get_object_or_404(Resident, id = resident_id)

    if request.method == 'POST':
        resident.delete()
        messages.success(request, "Resident deleted successfully!")
        return redirect('view_apartment_block', block_id, 1)
    
    return render(request, 'delete_resident.html', {'resident': resident, 'block_id': block_id})
    
@login_required
def delete_apartment_block(request, block_id, id):
    block = get_object_or_404(ApartmentBlock, block_id = block_id)

    if request.method == 'POST':
        block.delete()
        messages.success(request, "Resident deleted successfully!")
        return redirect('dashboard', id)
    
    return render(request, 'delete_apartment_block.html', {'block_id': block_id, 'id': id}) 

@login_required
def logout_confirmation(request):
    return render(request, 'logout_confirmation.html')

def add_utility_rates(request):
    if request.method == 'POST':
        form = UtilityRatesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard') 
    else:
        form = UtilityRatesForm()
    return render(request, 'add_utility_rates.html', {'form': form})

@login_required
def monthly_usage(request, resident_id, block_id):
    rates = get_object_or_404(UtilityRates, id=1) 
    if request.method == 'POST':
        form = MonthlyUsageForm(request.POST)
        if form.is_valid():

            monthly_usage = form.save(commit=False)
            monthly_usage.id = resident_id  
            monthly_usage.monthly_payment = rates.monthly
            monthly_usage.save()
            save_monthly_usage(request, resident_id, block_id)
            return redirect('utilities', resident_id=resident_id, block_id=block_id)
    else:
        form = MonthlyUsageForm()
    
    return render(request, 'monthly_usage.html',{
        'form': form, 
        'resident_id': resident_id, 
        "block_id": block_id
    })


@login_required
def utilities(request, resident_id, block_id):
    resident = get_object_or_404(Resident, id=resident_id)
    rates = get_object_or_404(UtilityRates, id=1) 
    monthly_usage = get_object_or_404(MonthlyUsage, id=resident_id) 

    current_month = timezone.now().month
    current_year = timezone.now().year
    
    existing_entry = Utilities.objects.filter(
        resident_id=resident_id,
        created_at__month=current_month,
        created_at__year=current_year
    ).first()

    if monthly_usage.electricity > 100:
        electricity_bill = (
            rates.electricity_excess * (monthly_usage.electricity - 100) +
            rates.fixed_e + rates.taxes_e + (100 * rates.electricity_base)
        )
    else:
        electricity_bill = (
            rates.electricity_base * monthly_usage.electricity +
            rates.fixed_e + rates.taxes_e
        )

    utilities = Utilities(
        resident_id=resident_id,
        water_bill=(rates.water_cubic_meter * monthly_usage.water + rates.fixed + rates.taxes),
        electricity_bill=electricity_bill,
        monthly_payment=rates.monthly,
        fees=monthly_usage.fees
    )
    
    if existing_entry:
        update = get_object_or_404(Utilities, resident_id=resident_id) 
        update.water_bill=utilities.water_bill
        update.electricity_bill=utilities.electricity_bill
        update.monthly_payment=utilities.monthly_payment
        update.fees=utilities.fees
        update.save()
        payment_history(request, resident_id)
        return redirect('view_apartment_block', block_id, 1)
    else:
        try:
            utilities.save()
            payment_history(request, resident_id)
            print("Utilities saved successfully") 
            return redirect('view_apartment_block', block_id, 1)
        except IntegrityError:
            
            print("An error occurred while saving Utilities.")  
            return redirect('view_apartment_block', block_id=block_id)

@login_required
def save_monthly_usage(request, resident_id, block_id):
    monthly_usage = get_object_or_404(MonthlyUsage, id=resident_id) 

   
    existing_entry = UsageHistory.objects.filter(resident_id=resident_id).last()

    if existing_entry: 
        print("Updating existing entry...")
        
        
        if existing_entry.recorded_at.month == monthly_usage.recorded_at.month:    
            print(f"Month matched: {existing_entry.recorded_at.month} == {monthly_usage.recorded_at.month}")
            
            existing_entry.water_usage = monthly_usage.water
            existing_entry.electricity_usage = monthly_usage.electricity
            existing_entry.monthly_payment = monthly_usage.monthly_payment
            existing_entry.fees = monthly_usage.fees
            existing_entry.recorded_at = monthly_usage.recorded_at
            existing_entry.save()  
            print("Entry updated successfully")
        else:
            print("New month detected, creating new entry...")
            
            usage = UsageHistory(
                resident_id=resident_id,
                apartment_block_id=block_id,
                water_usage=monthly_usage.water,
                electricity_usage=monthly_usage.electricity,
                monthly_payment=monthly_usage.monthly_payment,
                fees=monthly_usage.fees,
                recorded_at=monthly_usage.recorded_at
            )
            usage.save() 
            print("New usage history entry saved successfully")
        
    else:
        print("No existing entry found, creating new entry...")
        
        usage = UsageHistory(
            resident_id=resident_id,
            apartment_block_id=block_id,
            water_usage=monthly_usage.water,
            electricity_usage=monthly_usage.electricity,
            monthly_payment=monthly_usage.monthly_payment,
            fees=monthly_usage.fees,
            recorded_at=monthly_usage.recorded_at
        )
        usage.save()  
        print("New usage history entry saved successfully")

    return redirect('view_apartment_block', block_id, 1) 


@login_required
def payment_history(request, resident_id):
    payment = get_object_or_404(Utilities, resident_id=resident_id)  

    existing_entry = PaymentHistory.objects.filter(resident_id=resident_id).last()

    if existing_entry: 
        print("Updating existing entry...")
        
        
        if existing_entry.created_at.month == payment.created_at.month:    
            print(f"Month matched: {existing_entry.created_at.month} == {payment.created_at.month}")
            
            existing_entry.water_bill = payment.water_bill
            existing_entry.electricity_bill = payment.electricity_bill
            existing_entry.monthly_payment = payment.monthly_payment
            existing_entry.fees = payment.fees
            existing_entry.created_at = payment.created_at
            existing_entry.save()  
            print("Entry updated successfully")
        else:
            print("New month detected, creating new entry...")
            
            payment = PaymentHistory(
                resident_id=resident_id,
                water_bill=payment.water_bill,
                electricity_bill=payment.electricity_bill,
                monthly_payment=payment.monthly_payment,
                fees=payment.fees,
                created_at=payment.created_at
            )
            payment.save()  
            print("New usage history entry saved successfully")
        
    else:
        print("No existing entry found, creating new entry...")
        
        payment = PaymentHistory(
                resident_id=resident_id,
                water_bill=payment.water_bill,
                electricity_bill=payment.electricity_bill,
                monthly_payment=payment.monthly_payment,
                fees=payment.fees,
                created_at=payment.created_at
        )
        payment.save()
        print("New usage history entry saved successfully")

@login_required
def payment_history(request, resident_id):
    
    payment = get_object_or_404(Utilities, resident_id=resident_id)  

   
    existing_entry = PaymentHistory.objects.filter(resident_id=resident_id).last()

    if existing_entry: 
        print("Updating existing entry...")

   
        if existing_entry.created_at.month == payment.created_at.month:    
            print(f"Month matched: {existing_entry.created_at.month} == {payment.created_at.month}")

            existing_entry.water_bill = payment.water_bill
            existing_entry.electricity_bill = payment.electricity_bill
            existing_entry.monthly_payment = payment.monthly_payment
            existing_entry.fees = payment.fees
            existing_entry.created_at = payment.created_at
            existing_entry.save()  
            print("Entry updated successfully")
        else:
            print("New month detected, creating new entry...")

            new_payment = PaymentHistory(
                resident_id=resident_id, 
                water_bill=payment.water_bill,
                electricity_bill=payment.electricity_bill,
                monthly_payment=payment.monthly_payment,
                fees=payment.fees,
                created_at=payment.created_at
            )
            new_payment.save() 
            print("New payment history entry saved successfully")
        
    else:
        print("No existing entry found, creating new entry...")
      
        new_payment = PaymentHistory(
                resident_id=resident_id,  
                water_bill=payment.water_bill,
                electricity_bill=payment.electricity_bill,
                monthly_payment=payment.monthly_payment,
                fees=payment.fees,
                created_at=payment.created_at
        )
        new_payment.save()  
        print("New payment history entry saved successfully")










