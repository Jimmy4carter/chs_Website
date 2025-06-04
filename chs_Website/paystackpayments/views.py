import json
from django.http.request import HttpRequest
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CustomUser, StudentAccount
from . import forms
from django.contrib import messages
from django.conf import settings
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
# Create your views here.

def initiate_payment(request):
    if request.method=="POST":
        payment_form = forms.PaymentForm(request.POST)
        if payment_form.is_valid():
            payment=payment_form.save()
            return render(request, 'make_payment.html', {'payment': payment, 'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY})
    return HttpResponseRedirect(reverse("tuition_preview"))

def verify_payment(request, ref:str):
    payment= get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, "Payment Verification Successful")
        student_id=CustomUser.objects.get(username=payment.reg_no)
        std_account = StudentAccount.objects.get(students_id=student_id)
        std_account.total_payed =  std_account.total_payed + payment.amount
        if payment.amount >= std_account.to_pay:
            std_account.surplus = payment.amount - std_account.to_pay
            std_account.to_pay = 0
        else:
             std_account.to_pay = std_account.to_pay - payment.amount

        std_account.save()


    else:
        messages.error(request, "Payment Verification Failed Please Contact Admin")
    return HttpResponseRedirect(reverse("tuition_preview"))

def verify_application(request, ref:str):
    payment= get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, " Payment Verification Successful")
        return render(request, "public_template/apply_succes.html",{'ref':ref})
    else:
        messages.error(request, "Payment Verification Failed")
        return render(request, "public_template/apply_succes.html",{'ref}':ref})



@csrf_exempt
@require_POST
def paystack_webhook(request):
    jsondata = request.body

    data_recieved = json.loads(jsondata)
    print("hooked")

    return HttpResponse(status=200)