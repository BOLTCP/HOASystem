from django import forms
from HOA.models import *
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['fname', 'lname', 'RD', 'phone_number', 'role', 'description', 'since']

class EditStaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['fname', 'lname', 'RD', 'phone_number', 'role', 'description']

class DeleteStaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['fname', 'lname', 'RD', 'phone_number', 'role', 'description', 'since']

class CommonPropertyForm(forms.ModelForm):
    class Meta:
        model = CommonProperty
        fields = ['block', 'category', 'description', 'maintenance_status', 'last_maintenance_date']

class StructuralElementForm(forms.ModelForm):
    class Meta:
        model = StructuralElement
        fields = ['element_type', 'condition', 'inspection_date']

class UtilitySystemForm(forms.ModelForm):
    class Meta:
        model = UtilitySystem
        fields = ['system_type', 'operational_status', 'last_service_date']

class SharedAmenityForm(forms.ModelForm):
    class Meta:
        model = SharedAmenity
        fields = ['amenity_type', 'usage_status', 'last_cleaned_date']

class SecurityForm(forms.ModelForm):
    class Meta:
        model = Security
        fields = ['type', 'location', 'installation_date', 'condition', 'notes']

class FormSelection(forms.ModelForm):
    class Meta:
        fields = ['StructuralElementForm', 'UtilitySystemForm', 'SharedAmenityForm', 'SecurityForm', 'Other']

class BudgetForm(forms.ModelForm):
    class Meta:
        model = BudgetOfApartmentBlock
        fields = ['budget_month', 'total_budget_amount', 'staff_salaries_total', 'common_property_expenses_total',
                  'additional_expenses', 'description', 'pretext', 'apartment_block']

        widgets = {
            'budget_month': forms.DateInput(attrs={'type': 'month'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_budget_month(self):
        budget_month = self.cleaned_data.get('budget_month')
        if not budget_month:
            raise ValidationError("Budget month is required.")
        return budget_month

    def clean_total_budget_amount(self):
        total_budget_amount = self.cleaned_data.get('total_budget_amount')
        if total_budget_amount <= 0:
            raise ValidationError("Total budget amount must be a positive number.")
        return total_budget_amount

    def clean_staff_salaries_total(self):
        staff_salaries_total = self.cleaned_data.get('staff_salaries_total')
        if staff_salaries_total < 0:
            raise ValidationError("Staff salaries total cannot be negative.")
        return staff_salaries_total

    def clean_common_property_expenses_total(self):
        common_property_expenses_total = self.cleaned_data.get('common_property_expenses_total')
        if common_property_expenses_total < 0:
            raise ValidationError("Common property expenses cannot be negative.")
        return common_property_expenses_total

    def clean_additional_expenses(self):
        additional_expenses = self.cleaned_data.get('additional_expenses')
        if additional_expenses < 0:
            raise ValidationError("Additional expenses cannot be negative.")
        return additional_expenses

    def clean_apartment_block(self):
        apartment_block = self.cleaned_data.get('apartment_block')
        if not apartment_block:
            raise ValidationError("Apartment block is required.")
        return apartment_block

class TimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = ['date', 'user', 'job_type', 'job_site', 'job_description']

class BudgetRequestForm(forms.ModelForm):
    class Meta:
        model = BudgetRequest
        fields = ['name', 'user', 'request_type', 'request_info', 'pretext', 'comment', 'request_date']





