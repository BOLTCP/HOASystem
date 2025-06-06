from django.db import models
from rest_framework import serializers
from Контор.models import Resident, Utilities, MonthlyUsage

class Payment(models.Model):
    user = models.ForeignKey(Resident, on_delete=models.CASCADE)
    monthly_overview = models.ForeignKey(MonthlyUsage, on_delete=models.CASCADE)
    monthly_overview_payment = models.ForeignKey(Utilities, on_delete=models.CASCADE)
    net_amount = models.DecimalField(max_digits=20, decimal_places=2)
    hoa_monthly = models.DecimalField(max_digits=20, decimal_places=2)
    net_utilities = models.DecimalField(max_digits=20, decimal_places=2)
    water = models.DecimalField(max_digits=20, decimal_places=2)
    electricity = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('in_deficit', 'In-Deficit')], default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.net_amount} for {self.monthly_overview} - {self.status}"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'