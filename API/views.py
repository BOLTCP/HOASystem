from decimal import Decimal
import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from Контор.models import Utilities, Resident, PaymentHistory
from Контор.views import payment_history
import random, string, logging
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
import json, requests
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, PaymentSerializer
from django.views.decorators.http import require_POST

@api_view(['GET'])
def make_payment_monthly_usage(request, resident_id, payment_id):
    logger = logging.getLogger(__name__)

    payment_exists = Payment.objects.filter(transaction_id=payment_id).exists()
    
    if payment_exists:
        logger.info(f"Payment with transaction_id {payment_id} already exists.")
        return JsonResponse({"error": "Payment with this ID already exists."}, status=400)

    payment_details = Utilities.objects.filter(resident_id=resident_id).last()
    if not payment_details:
        return JsonResponse({"error": "No usage details found for this resident."}, status=404)

    resident = get_object_or_404(Resident, id=resident_id)
    usage = get_object_or_404(MonthlyUsage, id=resident_id)

    payment_amount = Decimal(payment_details.water_bill + payment_details.electricity_bill + payment_details.monthly_payment + payment_details.fees).quantize(Decimal('0.01'))
    net_util = Decimal(payment_details.water_bill + payment_details.electricity_bill).quantize(Decimal('0.01'))
    monthly = Decimal(payment_details.monthly_payment).quantize(Decimal('0.01'))
    water = Decimal(payment_details.water_bill).quantize(Decimal('0.01'))
    electricity = Decimal(payment_details.electricity_bill).quantize(Decimal('0.01'))

    payment = Payment.objects.create(
        monthly_overview=usage,
        monthly_overview_payment=payment_details,
        net_amount=payment_amount,
        hoa_monthly=monthly,
        net_utilities=net_util,
        transaction_id=payment_id,
        water=water,
        electricity=electricity,
        user=resident,
        created_at=datetime.datetime.now(),
        updated_at=None,
        status='Pending'
    )

    payment_serializer = PaymentSerializer(payment)
    payment_data = payment_serializer.data

    logger.info("Serialized Payment Data: %s", payment_data)

    external_url = "https://jsonplaceholder.typicode.com/posts" 
    try:
        response = requests.get(external_url, params=payment_data)
        print(payment_data)
        if response.status_code == 200:
            logger.info("Successfully sent payment data to external system.")
        else:
            logger.warning(f"Failed to send data to external system. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in sending data to external system: {e}")

    return render(request, 'make_payment_monthly_usage.html', {
        'resident': resident,
        'payment_details': payment_details,
        'net_util': net_util,
        'resident_id': resident_id,
        'payment_amount': payment_amount,
        'payment_data': payment_data 
    })

@require_POST
@csrf_exempt  
def processing_payment(request, resident_id):
    print(request)
    try:
        data = json.loads(request.body)
        print(data)
        payment_id = data.get('payment_id')
        amount = Decimal(data.get('amount')).quantize(Decimal('0.01'))
        user_id = data.get('user_id')
        hoa_monthly = Decimal(data.get('hoa_monthly')).quantize(Decimal('0.01'))
        transaction_id = data.get('transaction_id')
        net_utilities = Decimal(data.get('net_utilities')).quantize(Decimal('0.01'))
        water = Decimal(data.get('water')).quantize(Decimal('0.01'))
        electricity = Decimal(data.get('electricity')).quantize(Decimal('0.01'))

        if not all([amount, transaction_id, user_id]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        payment = get_object_or_404(Payment, user_id=resident_id)
        id = payment.id
        payment.net_amount -= amount
        payment.hoa_monthly -= hoa_monthly
        payment.net_utilities -= net_utilities
        payment.water -= water
        payment.electricity -= electricity
        payment.updated_at = datetime.datetime.now()

        update_status = get_object_or_404(PaymentHistory, resident_id=resident_id)
        if payment.net_amount == 0:
            payment.status = 'Completed'
            update_status.payment_status = payment.status
            update_status.created_at = datetime.datetime.now()
            update_status.save()
            payment.delete()

        else:
            payment.status = 'In Deficit'
            update_status.payment_status = payment.status
            update_status.save()
            payment.save()

        return JsonResponse({
            "message": "Payment processed successfully",
            "payment_id": id
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


