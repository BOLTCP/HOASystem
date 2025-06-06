from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from Контор.models import PaymentHistory, Utilities
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
import datetime, calendar
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models.functions import Extract
from itertools import groupby
from operator import attrgetter
from django.contrib.auth.hashers import make_password

def hoa_login(request):
    if request.method == 'POST':
        memberName = request.POST['memberName']
        password = request.POST['password']
        hashed_password = make_password(password)
        print(hashed_password)
        print(f"Attempting login with username: {memberName}, password: {password}")
        user = authenticate(request, username=memberName, password=password)

        if user is not None:
            print("User authenticated successfully.")
            try:
                # Check if there's a corresponding HOA_members entry for the user
                hoa_member = HOA_members.objects.get(memberName=user)
                print(f"Found HOA member: {hoa_member}")
            except HOA_members.DoesNotExist:
                print("HOA member does not exist.")
                return render(request, 'hoa_login.html', {'error': 'Invalid username or password.'})

            # Log the user in
            login(request, user)
            request.session['user_id'] = user.id
            print(f"User logged in. Session ID: {request.session['user_id']}")

            # Redirect based on category from HOA_members
            if hoa_member.category == 'Executive':
                return redirect('executive_dashboard', id=user.id)
            elif hoa_member.category == 'Directors':
                return redirect('directors_dashboard', id=user.id)
            elif hoa_member.category == 'Supervisory':
                return redirect('supervisory_dashboard', id=user.id)
        else:
            print("Authentication failed.")
            return render(request, 'hoa_login.html', {'error': 'Invalid username or password.'})
        
    return render(request, 'hoa_login.html')

def user_logged_in_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        
        if user_id is None:
            return redirect('hoa_login') 
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect('hoa_login') 

        return view_func(request, *args, **kwargs)

    return _wrapped_view

@user_logged_in_required
def executive_dashboard(request, id):
    executive = get_object_or_404(HOA_members, members_id=id)
    staffs = Staff.objects.filter().all()
    commonproperty = CommonProperty.objects.filter().all()
    apartmentblocks = ApartmentBlock.objects.all()
    number_of_residents = len(Resident.objects.all())
    capacity_of_all_blocks = 0
    other = CommonProperty.objects.filter(category='Other').all()
    securities = Security.objects.all().distinct()
    sharedamenities = SharedAmenity.objects.all().distinct()
    structuralelements = StructuralElement.objects.all().distinct()
    utilitysystems = UtilitySystem.objects.all().distinct()
    
    for apartmentblock in apartmentblocks:
        capacity_of_all_blocks += apartmentblock.units_per_story * apartmentblock.number_of_stories

    message = ""
    message1 = ""
    if len(staffs) == 0:
        message = "You have no staff! Please add staff."

    if len(commonproperty) == 0:
        message1 = "You have no Common Property! Please add Common Property."

    messages = {
        'message': message,
        'message1': message1,
    }
    context = {
        'executive': executive, 'id': id, 'messages': messages, 'number_of_blocks': len(apartmentblocks),
        'apartment_blocks': apartmentblocks,
        'capacity_of_all_blocks': capacity_of_all_blocks, 'number_of_residents': number_of_residents, 
        '1': len(other), '2': len(securities), '3': len(sharedamenities), '4': len(structuralelements),
        '5': len(utilitysystems)
    }
    if len(messages) != 0:
        return render(request, 'executive_dashboard.html', context)
    else: 
        field_names = [field.name for field in Staff._meta.get_fields()]
        return render(request, 'executive_dashboard.html', {'executive': executive, 'id': id, 'staffs': staffs, 'number_of_residents': number_of_residents,
                                                             'field_names': field_names, 'apartmentblocks': apartmentblocks, 'messages': messages})

@user_logged_in_required
def add_staff(request, id):

    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff_data = form.cleaned_data
            password = staff_data.get('RD')[6:]
            try:
                user = User.objects.create_user(
                    username=staff_data['fname'],  
                    password=password  
                )
                staff = form.save(commit=False)
                staff.user = user 
                staff.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Staff added successfully.',
                    'staff': {
                        'name': staff.fname,
                        'phone_number': staff.phone_number,
                        'RD': staff.RD,
                    },
                    'message': f'{staff.fname} - {staff.phone_number}'
                })

            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'errors': 'This story and unit combination is already occupied!'
                })

        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = StaffForm()
    return redirect('hoa_staffs', id)

@user_logged_in_required
def hoa_staffs(request, id):
    
    staffs = Staff.objects.filter().all()
    message = ''
    if len(staffs) == 0:
        message = 'You have no staff, Please add staff!'

    addform = StaffForm()
    editform = EditStaffForm()

    choices = Staff._meta.get_field('role').choices
    roles = [role[0] for role in choices]
   
    context = {
        'message': message, 
        'id': id,
        'addform': addform,
        'roles': roles, 
    }

    if len(staffs) == 0 :
        message = "You have no staff! Please add staff."
        return render(request, 'hoa_staffs.html', context)
    else: 
        field_names = [field.name for field in Staff._meta.get_fields()]
        return render(request, 'hoa_staffs.html', {'staffs': staffs, 'field_names': field_names, 
                                                   'id': id, 'addform': addform, 'roles': roles,
                                                    'editform': editform,})
    
@user_logged_in_required
def edit_staff(request, staff_id, id):
    staff = get_object_or_404(Staff, user_id=staff_id)
    
    if request.method == 'POST':
        form = EditStaffForm(request.POST, instance=staff)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Staff updated successfully.')
                return redirect('hoa_staffs', id)  
            except IntegrityError:
                messages.error(request, 'An error occurred while updating the staff information.')
        else:
            messages.error(request, f"Form is invalid: {form.errors}")
    else:
        form = EditStaffForm(instance=staff)

    form = EditStaffForm(instance=staff)
    return render(request, 'edit_staff.html', {
        'form': form,
        'staff': staff,
    })

@user_logged_in_required
def delete_staff(request, staff_id, id):
    staff = get_object_or_404(Staff, user_id=staff_id)

    if request.method == 'POST':
        staff.delete()
        messages.success(request, "Staff deleted successfully!")
        return redirect('hoa_staffs', id) 
    
    return render(request, 'delete_staff.html', {'staff': staff, 'id': id})

@user_logged_in_required
def add_common_properties(request, placeholder, placeholder1, exec_id):
    form = None
    selected_form = placeholder.replace(' ', '')
    apartment_block = get_object_or_404(ApartmentBlock, block_id=placeholder1[6:])
    stories = apartment_block.number_of_stories
    units = apartment_block.units_per_story
    number_of_stories = [i for i in range(1, stories+1)]
    units_per_story = [i for i in range(1, units+1)]

    if selected_form == 'StructuralElementForm':    
        form = StructuralElementForm()
    if selected_form == 'UtilitySystemForm':    
        form = UtilitySystemForm()
    if selected_form == 'SharedAmenityForm':    
        form = SharedAmenityForm()
    if selected_form == 'SecurityForm':    
        form = SecurityForm()
    return render(request, 'add_common_properties.html', { 
            'placeholder': selected_form, 'ui': placeholder, 'placeholder1': placeholder1, 'form': form, 'block_id': placeholder1[6:],
            'number_of_stories': number_of_stories, 'units_per_story': units_per_story, 'block_id': apartment_block.block_id, 'exec_id': exec_id,
        })

@user_logged_in_required
def property(request, story, unit, placeholder, placeholder1, exec_id):
    global globalID
    message = ''
    if story and unit:
        story = int(story)
        unit = int(unit)
        unit = story * 100 + unit
    if not story:
        story = None
    if not unit:
        unit = None
    
    if request.method == 'POST':

        if placeholder == 'StructuralElementForm':
            form = StructuralElementForm(request.POST)
            if form.is_valid():
                    apartment_block = get_object_or_404(ApartmentBlock, block_id=placeholder1[6:])
                    elem_type = request.POST.get('element_type')
                    cond = request.POST.get('condition')
                    insp = request.POST.get('inspection_date')
                    
                    StructuralElement.objects.create(
                        apartmentblock = apartment_block,
                        unit = unit,
                        story = story,
                        element_type = elem_type,
                        property_category = 'StructuralElement',
                        condition = cond,
                        inspection_date = insp, 
                    )
                    property = StructuralElement.objects.last()
                    message = f'Property {property} was successfully created!'
            else:   
                return redirect(property_of_apartment_block, placeholder1[6:], exec_id)
            
        if placeholder == 'UtilitySystemForm':
            form = UtilitySystemForm(request.POST)
            if form.is_valid():
                    apartment_block = get_object_or_404(ApartmentBlock, block_id=placeholder1[6:])
                    sys_type = request.POST.get('system_type')
                    op_stats = request.POST.get('operational_status')
                    lsd = request.POST.get('last_service_date')
                    UtilitySystem.objects.create(
                        apartmentblock = apartment_block,
                        system_type = sys_type,
                        property_category = 'UtilitySystem',
                        operational_status = op_stats,
                        last_service_date = lsd,
                        unit = unit,
                        story = story,
                    )
                    property = UtilitySystem.objects.last()
                    message = f'Property {property} was successfully created!'
            else:
                return redirect(property_of_apartment_block, placeholder1[6:], exec_id)
            
        if placeholder == 'SecurityForm':
            form = SecurityForm(request.POST)
            if form.is_valid():
                    apartment_block = get_object_or_404(ApartmentBlock, block_id=placeholder1[6:])
                    sec_type = request.POST.get('type')
                    sec_loc = request.POST.get('location')
                    sec_install_date = request.POST.get('installation_date')
                    sec_cond = request.POST.get('condition')
                    sec_notes = request.POST.get('notes')
                    Security.objects.create(
                        apartmentblock = apartment_block,
                        type = sec_type,
                        location = sec_loc,
                        installation_date = sec_install_date,
                        property_category = 'Security',
                        condition = sec_cond,
                        notes = sec_notes,
                        unit = unit,
                        story = story,
                    )
                    property = Security.objects.last()
                    message = f'Property {property} was successfully created!'
            else:
                return redirect(property_of_apartment_block, placeholder1[6:], exec_id)
            
        if placeholder == 'SharedAmenityForm':
            form = SharedAmenityForm(request.POST)
            if form.is_valid():
                    apartment_block = get_object_or_404(ApartmentBlock, block_id=placeholder1[6:])
                    amenity = request.POST.get('amenity_type')
                    usage_stat = request.POST.get('usage_status')
                    lcd = request.POST.get('last_cleaned_date')
                    SharedAmenity.objects.create(
                        apartmentblock = apartment_block,
                        amenity_type = amenity,
                        usage_status = usage_stat,
                        property_category = 'SharedAmenity',
                        last_cleaned_date = lcd,
                        unit = unit,
                        story = story,
                    )
                    property = SharedAmenity.objects.last()
                    message = f'Property {property} was successfully created!'
            else:
                return redirect(property_of_apartment_block(placeholder1[6:], exec_id))

    return redirect(property_of_apartment_block, placeholder1[6:], exec_id, message)

@user_logged_in_required
def property_maintenance(request, property_category, property_id, apartmentblock, exec_id):
    apartmentblock_obj = get_object_or_404(ApartmentBlock, block_id=apartmentblock[6:])
    context = {'property_category': property_category, 'apartmentblock': apartmentblock_obj, 'exec_id': exec_id, 'message': None}

    if property_category == 'StructuralElement':
        print("LL")
        property_obj = get_object_or_404(StructuralElement, id=property_id)
        context['property'] = property_obj
    elif property_category == 'UtilitySystems':
        print("L")
        property_obj = get_object_or_404(UtilitySystem, id=property_id)
        context['property'] = property_obj
    elif property_category == 'SharedAmenities':
        print("LLL")
        property_obj = get_object_or_404(SharedAmenity, id=property_id)
        context['property'] = property_obj
    elif property_category == 'Securities':
        print("LLLL")
        property_obj = get_object_or_404(Security, id=property_id)
        context['property'] = property_obj

    if Property_Maintenance.objects.filter(property_id=property_id, property_category=property_category).exists():
            context['msg'] = f'The maintenance record for {property_obj} ALREADY EXISTS!'
            return render(request, 'property_maintenance.html', context)
        
    
    if request:
        if request.method == 'POST':
            print(request.FILES) 
            maintenance_date = request.POST.get('maintenance_date')
            maintenance_cost = request.POST.get('maintenance_cost')
            on_ground_location = request.POST.get('on_ground_location')
            unit = request.POST.get('unit')
            story = request.POST.get('story')
            next_maintenance_date = request.POST.get('next_maintenance_date')
            property_image = request.FILES.get('property_image')
            print(maintenance_cost, maintenance_date, next_maintenance_date, on_ground_location, property_image)

            if not all([maintenance_date, maintenance_cost, next_maintenance_date]):
                messages.error(request, "Please fill in all required fields.")
                return render(request, 'property_maintenance.html', context)
            if unit == '' and story == '':
                unit = None
                story = None

            try:
                Property_Maintenance.objects.create(
                    apartmentblock=apartmentblock_obj,
                    property_category=property_category,
                    property_id = property_id,
                    maintenance_date=maintenance_date,
                    maintenance_cost=maintenance_cost,
                    property_image=property_image,
                    on_ground_location=on_ground_location,
                    unit = unit,
                    story = story,
                    next_maintenance_date=next_maintenance_date
                )
                context['msg'] = f'The maintenance record for {property_obj} was successfully created!'
                return render(request, 'property_maintenance.html', context) 
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return render(request, 'property_maintenance.html', context)
   
    return render(request, 'property_maintenance.html', context)
    

def view_apartments(request, id):
    message = None
    apartment_blocks = ApartmentBlock.objects.all()
    
    return render(request, 'view_apartments.html', { 'apartment_blocks': apartment_blocks, 'id': id, 'message': message})

def property_of_apartment_block(request, block_id, id, message):

    securities = Security.objects.filter(apartmentblock_id=block_id).all().distinct()
    sharedamenities = SharedAmenity.objects.filter(apartmentblock_id=block_id).all().distinct()
    structuralelements = StructuralElement.objects.filter(apartmentblock_id=block_id).all().distinct()
    utilitysystems = UtilitySystem.objects.filter(apartmentblock_id=block_id).all().distinct()

    securitiesmaint = Property_Maintenance.objects.filter(property_category='Securities').all().order_by('apartmentblock_id')
    sharedamenitiesmaint = Property_Maintenance.objects.filter(property_category='SharedAmenities').all().order_by('apartmentblock_id')
    structuralmaint = Property_Maintenance.objects.filter(property_category='StructuralElement').all().order_by('apartmentblock_id')
    utilitymaint = Property_Maintenance.objects.filter(property_category='UtilitySystems').all().order_by('apartmentblock_id')
    
    for maint in structuralmaint:
        print(maint.property_id)

    form1 = StructuralElementForm()
    form2 = UtilitySystemForm()
    form3 = SharedAmenityForm()
    form4 = SecurityForm()
    forms = {'Structural Element Form': form1, 'Utility System Form': form2, 
             'Shared Amenity Form': form3, 'Security Form': form4}
    
    context1 = { 'securities': securities, 'securitiesmaint': securitiesmaint, 'sharedamenities': sharedamenities, 'sharedamenitiesmaint': sharedamenitiesmaint,
                 'structuralelements': structuralelements, 'structuralmaint': structuralmaint, 'utilitysystems': utilitysystems, 'utilitymaint': utilitymaint
    }
    apartment_block = get_object_or_404(ApartmentBlock, block_id=block_id)

    if message == 'None':
         return render(request, 'property_of_apartment_block.html', { 'apartment_block': apartment_block, 'exec_id': id, 'context1': context1,
                                                                    'forms': forms, 'apartment_block': apartment_block})
    else:
        return render(request, 'property_of_apartment_block.html', { 'apartment_block': apartment_block, 'exec_id': id, 'context1': context1,
                                                                    'forms': forms, 'apartment_block': apartment_block, 'message': message})

def create_budget(request, id):
    if request.method == 'POST':
        budget_month = request.POST.get('budget_month')
        total_budget_amount = request.POST.get('total_budget_amount')
        staff_salaries_total = request.POST.get('staff_salaries_total')
        common_property_expenses_total = request.POST.get('common_property_expenses_total')
        additional_expenses = request.POST.get('additional_expenses')
        description = request.POST.get('description', '')
        pretext = request.POST.get('pretext')
        apartment_block_id = request.POST.get('apartment_block')

        apartment_block = ApartmentBlock.objects.get(block_id=apartment_block_id[6:])
        
        staff_salary_total = 0
        for staff in StaffSalary.objects.all():
            staff_salary_total += staff.salary_amount

        common_property_expenses_total = 0
        for common_property in CommonProperty.objects.all():
            staff_salary_total += staff.salary_amount    

        resident_utility_total = 0
        for resident_utility in Utilities.objects.all():
            resident_utility_total += resident_utility.monthly_payment  

        budget = BudgetOfApartmentBlock.objects.create(
            budget_month=budget_month,
            total_budget_amount=total_budget_amount,
            staff_salaries_total=staff_salaries_total,
            resident_utility_total=resident_utility_total,
            common_property_expenses_total=common_property_expenses_total,
            additional_expenses=additional_expenses,
            description=description,
            pretext=pretext,
            apartment_block=apartment_block,
        )

        messages.success(request, 'Budget created successfully!')
        return redirect('executive_dashboard', id)  

    else:
        staff_salary_total = 0
        for staff in StaffSalary.objects.all():
            staff_salary_total += staff.salary_amount

        resident_utility_total = 0
        for resident_utility in Utilities.objects.all():
            resident_utility_total += resident_utility.monthly_payment  
        
        apartment_blocks = ApartmentBlock.objects.all()

        return render(request, 'create_budget.html', {
            'staff_salary_total': staff_salary_total,  
            'apartment_blocks': apartment_blocks,
            'resident_utility_total': resident_utility_total,
            'id': id
        })

def budget_list(request):
    budgets = BudgetOfApartmentBlock.objects.all()
    return render(request, 'budget_list.html', {'budgets': budgets})


def create_staff_salary(request, staff_id, id):
    user = get_object_or_404(User, id=staff_id)

    if request.method == 'POST':
        salary_amount = request.POST.get('salary_amount')
        month = request.POST.get('month')
        paid_on = request.POST.get('paid_on') 
        bank_account = request.POST.get('bank_account')  
        type = request.POST.get('bank_type') 
        print(bank_account)

        if not salary_amount or not paid_on:
            messages.error(request, "Salary amount and payment date are required!")
        else:
            StaffSalary.objects.create(
                user=user,
                salary_amount=salary_amount,
                month=month,
                paid_on=paid_on,
                bank_account=bank_account,
                bank_type=type
            )
            messages.success(request, "Salary added successfully!")
            add_salary(user.id)
            return redirect('hoa_staffs', id)

    return render(request, 'create_staff_salary.html')

def add_salary(staff_id):
    staff = get_object_or_404(Staff, user_id=staff_id)
    salary = StaffSalary.objects.filter(user_id=staff_id).last()
    
    if salary:
        staff.staff_salary = salary.salary_amount  
        staff.save() 
        print(f"Updated staff salary: {staff.staff_salary}")
    else:
        print("No salary record found for this staff.")

def staff_salary_list(request):
    salaries = StaffSalary.objects.all()
    return render(request, 'staff_salary_list.html', {'salaries': salaries})

def see_budget_request(request, id):
    budget_requests = BudgetRequest.objects.filter(desicion='Pending').all()
    if len(budget_requests) == 0:
        message = 'There was no budget requests!'
        return render(request, 'see_budget_request.html', {'budget_requests': budget_requests, 'id': id, 'message': message})
    
    return render(request, 'see_budget_request.html', {'budget_requests': budget_requests, 'id': id})

def update_decision(request, request_id, id):
    print(id, request_id)
    if request.method == 'POST':
        desicion = request.POST.get('desicion')
        desicion_comment = request.POST.get('desicion_comment')

        if not desicion:
            messages.error(request, "Please select a decision.")
        else:
            budget_request = get_object_or_404(BudgetRequest, id=request_id)
            budget_request.desicion = desicion
            budget_request.desicion_comment = desicion_comment
            budget_request.save()
            messages.success(request, "Decision updated successfully!") 
            return redirect('executive_dashboard', id)

    return redirect('update_decision', request_id)

def create_monthly_timetable(request, staff_id, id):
    staff = get_object_or_404(Staff, user_id=staff_id)
    today = datetime.date.today()
    year, month = today.year, today.month

    first_day_of_month = datetime.date(year, month, today.day)
    timetable_message = ''
    
    calendar_month = calendar.monthcalendar(year, month)
    weekdays = [
        day for week in calendar_month for day in week[0:5] if day != 0
    ]  
    print(weekdays, len(weekdays))
    timetable = TimeTable.objects.filter(user_id=staff_id).all()
    if len(timetable) > 0:
        return redirect(see_timetable, id)

    if request.method == 'POST':
        if 'confirm' in request.POST:
            for day in weekdays:
                work_date = datetime.date(year, month, day)
                if work_date >= first_day_of_month:
                    if not TimeTable.objects.filter(date=work_date, user_id=staff.user_id).exists():
                            TimeTable.objects.create(
                                date=work_date,
                                user_id=staff_id,
                                job_type='General',
                                job_site=ApartmentBlock.objects.first(),
                                job_description='Generated timetable',
                                attendance='Pending / Shift Clock'
                            )
                    else:
                        timetable_message = f'Staff ID of {staff_id} already has a Timetable for this month!'
                        return redirect(update_timetable, staff_id, timetable_message)
                
            messages.success(request, "Timetable for this month created successfully!")
            timetable_message = f'Staff ID of {staff_id} Timetable was successfully created!'
            return redirect(update_timetable, staff_id, timetable_message, id)  
        else:
            return redirect(hoa_staffs, id)
    return render(request, 'timetable_confirm.html', {'staff': staff, 'year': year, 'month': month, 'id': id})

def update_timetable(request, staff_id, timetable_message, id):
    user_id = staff_id
    if request.method == 'POST':
        
        for key in request.POST:
            if key.startswith('timetable.date_'):
            
                suffix = key.split('_')[1]
                
                date = request.POST.get(f'timetable.date_{suffix}')
                staff_id = request.POST.get(f'timetable.staff_{suffix}')
                job_type = request.POST.get(f'timetable.job_type_{suffix}')
                job_site_id = request.POST.get(f'timetable.job_site_{suffix}')
                job_description = request.POST.get(f'timetable.job_description_{suffix}')


                staff = get_object_or_404(Staff, user_id=user_id)
                job_site = get_object_or_404(ApartmentBlock, block_id=job_site_id)

                timetable = TimeTable.objects.filter(user_id=user_id, date=date).first()
                if timetable:
                    timetable.job_type = job_type
                    timetable.job_site = job_site
                    timetable.job_description = job_description
                    timetable.save()
                    print("Timetable updated")
                else:
                    print("No timetable found for this staff and date")
                
        return redirect(see_timetable, id)

    staff = get_object_or_404(Staff, user_id=user_id)
    timetables = TimeTable.objects.filter(user_id=user_id).all()
    apartment_blocks = ApartmentBlock.objects.all()
    return render(request, 'update_timetable.html', {'staff': staff, 'apartment_blocks': apartment_blocks, 'id': id, 'timetable_message': timetable_message, 'timetables': timetables})

def see_timetable(request, id):
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    today = datetime.date.today()
    timetables = TimeTable.objects.filter(date__month=month, date__year=year).distinct().order_by('user_id')
    timetable = {
        staff_id: list(items) 
        for staff_id, items in groupby(timetables, key=attrgetter('user_id'))
    }
    return render(request, 'see_timetable.html', {'id': id, 'timetables': timetables, 'today': today, 'timetable': timetable})

def staff_timetable(request, user_id, timetable_id, id):
    print(user_id, timetable_id, id)
    if request.method == 'POST':
        attendance = request.POST.get('attendance')
        timetable = get_object_or_404(TimeTable, user_id=user_id, id=timetable_id)
        timetable.attendance = attendance
        timetable.save()
    return redirect(see_timetable, id)

def salary_processing(request, staff_id, id):
    staff = get_object_or_404(Staff, user_id=staff_id)
    salary = StaffSalary.objects.filter(user_id=staff_id).last()
    salary = float(salary.salary_amount)
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    timetables = TimeTable.objects.filter(date__month=month, date__year=year, user_id=staff_id).distinct()
    work_days = len(timetables)
    salary_of_month = round((salary / 22 * work_days), 2)
    ndm = round((salary_of_month * 0.115), 2)
    hhoat = round(((salary_of_month - salary_of_month * 0.115) * 0.10), 2)
    salary_at_hand = round(salary_of_month - salary_of_month * 0.115 - ((salary_of_month - salary_of_month * 0.115) * 0.10), 2)

    return render(
        request, 'salary_processing.html', {'staff': staff, 'salary_of_month': salary_of_month,
                                   'salary_at_hand': salary_at_hand, 'timetables': timetables,
                                   'ndm': ndm, 'hhoat': hhoat, 'id': id
                                    })

def logout_confirmation(request, id):
    logout(request)
    return render(request, 'logout_confirmation.html', { 'id': id })







def staff_login(request):
    if request.method == 'POST': 
        fname = request.POST['fname']
        password = request.POST['password']
        rd = request.POST['RD']

        user = authenticate(request, username=fname, password=password, rd=rd)
        
        if user is not None:
            print("User authenticated successfully.")
            try:
                hoa_member = Staff.objects.get(user=user)
                print(f"Found HOA member: {hoa_member}")
            except HOA_members.DoesNotExist:
                print("HOA member does not exist.")
                return render(request, 'staff_login.html', {'error': 'Invalid username or password.'})

            login(request, user)
            request.session['user_id'] = user.id
            print(f"User logged in. Session ID: {request.session['user_id']}")
            return redirect('staff_dashboard', id=user.id)
        else:
            print("Authentication failed.")
            return render(request, 'staff_login.html', {'error': 'Invalid username or password.'})
        
    return render(request, 'staff_login.html')

def user_logged_in_required_staff(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        
        if user_id is None:
            return redirect('staff_login') 
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect('staff_login') 

        return view_func(request, *args, **kwargs)

    return _wrapped_view

@user_logged_in_required_staff
def staff_dashboard(request, id):
    staff = get_object_or_404(Staff, user_id=id)
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    timetables = TimeTable.objects.filter(date__month=month, date__year=year, user_id=staff.user_id).distinct()
    for timetable in timetables:
        print(timetable)
        
    if len(timetables) == 0:
        return render(request, 'staff_dashboard.html', {'staff': staff, 'id': id})
    else :
        salary = StaffSalary.objects.filter(user_id=staff.user_id).last()
        salary = float(salary.salary_amount)
        work_days = len(timetables)
        salary_of_month = round((salary / 22 * work_days), 2)
        ndm = round((salary_of_month * 0.115), 2)
        hhoat = round(((salary_of_month - salary_of_month * 0.115) * 0.10), 2)
        salary_at_hand = round(salary_of_month - salary_of_month * 0.115 - ((salary_of_month - salary_of_month * 0.115) * 0.10), 2)

        days_worked = 0
        days_missing = 0
        days_to_work = 0
        for timetable in timetables:
            if timetable.attendance == 'Pending / Shift Clock':
                days_to_work += 1
            if timetable.attendance == 'Came To Work':
                days_worked += 1
            if timetable.attendance == 'Did Not Come To Work':
                days_missing += 1
            
        context = {
            'staff': staff, 'salary_of_month': salary_of_month, 'days_worked': days_worked, 'days_missing': days_missing,
            'salary_at_hand': salary_at_hand, 'timetables': timetables, 'days_to_work': days_to_work,
            'ndm': ndm, 'hhoat': hhoat, 'id': id, 'work_days': len(timetables), 'current_salary': round(days_worked * (salary_at_hand / len(timetables)), 2)
        }
        return render(
            request, 'staff_dashboard.html', context)
        
@user_logged_in_required_staff
def budget_request(request, id):

    choices = BudgetRequest._meta.get_field('request_type').choices
    request_types = [request_type[0] for request_type in choices]
    
    choices = BudgetRequest._meta.get_field('pretext').choices
    pretexts = [pretext[0] for pretext in choices]

    staff = get_object_or_404(User, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        request_type = request.POST.get('request_type')
        request_info = request.POST.get('request_info')
        pretext = request.POST.get('pretext')
        comment = request.POST.get('comment')
        
        budget_request = BudgetRequest.objects.create(
            name=name,
            user=staff,
            request_type=request_type,
            request_info=request_info,
            pretext=pretext,
            comment=comment,
        )
        messages.success(request, "Budget request submitted successfully!")
        return redirect('staff_dashboard', id=id)
    
    return render(request, 'budget_request.html', {'request_types': request_types, 'pretexts': pretexts})

@user_logged_in_required_staff
def request_state(request, id):
    budget_requests = BudgetRequest.objects.filter(user_id=id).all()
    print(budget_requests)
    if len(budget_requests) == 0:
        message = 'There was no request under you ID!'
        return render(request, 'request_state.html', {'budget_requests': budget_requests, 'id': id, 'message': message})
    else:
        return render(request, 'request_state.html', {'budget_requests': budget_requests, 'id': id })

@user_logged_in_required_staff
def logout_staff(request, id):
    logout(request)
    return render(request, 'logout_staff.html', { 'id': id })


