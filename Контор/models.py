from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Utilities(models.Model):
    resident_id = models.IntegerField()
    water_bill = models.FloatField() 
    electricity_bill = models.FloatField()  
    monthly_payment = models.FloatField()  
    fees = models.FloatField(null=True, blank=True) 

    def __str__(self):
        return f"Utilities - Water: {self.water_bill}, Electricity: {self.electricity_bill}, Monthly: {self.monthly_payment}, Fees: {self.fees if self.fees else 'No Fees'}"


class ApartmentBlock(models.Model):
    block_id = models.AutoField(primary_key=True)
    number_of_stories = models.IntegerField()
    units_per_story = models.IntegerField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE) 

    def __str__(self):
        return f"Block {self.block_id}"

class Resident(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=False)
    phone_number = models.CharField(max_length=15)
    apartment_block = models.ForeignKey(ApartmentBlock, related_name='residents', on_delete=models.CASCADE)
    password = models.CharField(max_length=15)
    story = models.IntegerField()
    unit = models.IntegerField()

    class Meta:
        unique_together = ('apartment_block', 'story', 'unit')

class UtilityRates(models.Model):
    water_cubic_meter = models.DecimalField(max_digits=20, decimal_places=2)  # Price per cubic meter of water
    fixed = models.DecimalField(max_digits=20, decimal_places=2)  # Fixed charge for utilities
    taxes = models.DecimalField(max_digits=20, decimal_places=2)  # Tax on utilities
    electricity_base = models.DecimalField(max_digits=20, decimal_places=2)  # Base rate for electricity
    electricity_excess = models.DecimalField(max_digits=20, decimal_places=2)
    fixed_e = models.DecimalField(max_digits=20, decimal_places=2) # Fixed charge for utilities
    taxes_e = models.DecimalField(max_digits=20, decimal_places=2)  # Tax on utilities  # Rate for excess electricity consumption
    monthly = models.DecimalField(max_digits=20, decimal_places=2)  # Monthly utility charges

    def __str__(self):
        return f"Rates - Water: {self.water_cubic_meter}, Electricity Base: {self.electricity_base}, Monthly: {self.monthly}"

class MonthlyUsage(models.Model):
    id = models.IntegerField(primary_key=True)
    water = models.DecimalField(max_digits=20, decimal_places=2)
    electricity = models.DecimalField(max_digits=20, decimal_places=2)  
    monthly_payment = models.DecimalField(max_digits=20, decimal_places=2)
    fees = models.FloatField(null=True, blank=True) 

    recorded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Utilities - Water: {self.water}, Electricity: {self.electricity}, Monthly: {self.monthly_payment}, Fees: {self.fees if self.fees else 'No Fees'}"

class Utilities(models.Model):
    resident_id = models.IntegerField()
    water_bill = models.DecimalField(max_digits=20, decimal_places=2) 
    electricity_bill = models.DecimalField(max_digits=20, decimal_places=2) 
    monthly_payment = models.DecimalField(max_digits=20, decimal_places=2)  
    fees = models.FloatField(null=True, blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Utilities - Water: {self.water_bill}, Electricity: {self.electricity_bill}, Monthly: {self.monthly_payment}, Fees: {self.fees if self.fees else 'No Fees'}"

class UsageHistory(models.Model):
    resident = models.ForeignKey('Resident', on_delete=models.CASCADE, related_name='usage_history')
    apartment_block = models.ForeignKey('ApartmentBlock', on_delete=models.CASCADE, related_name='usage_history')
    
    water_usage = models.DecimalField(max_digits=20, decimal_places=2)
    electricity_usage = models.DecimalField(max_digits=20, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=20, decimal_places=2)
    fees = models.DecimalField(max_digits=20, decimal_places=2)

    recorded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"UsageHistory for Resident {self.resident.name} on {self.recorded_at}"
    
class PaymentHistory(models.Model):
    resident_id = models.IntegerField()

    water_bill = models.DecimalField(max_digits=20, decimal_places=2)
    electricity_bill = models.DecimalField(max_digits=20, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=20, decimal_places=2)
    fees = models.DecimalField(max_digits=20, decimal_places=2)
    payment_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('in_deficit', 'In-Deficit')], default='pending')

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"PaymentHistory for Resident ID {self.resident_id} on {self.created_at}"
    
    

