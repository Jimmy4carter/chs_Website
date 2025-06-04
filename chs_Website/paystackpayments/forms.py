from django.forms.widgets import EmailInput
from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model =Payment
        fields=( "fullName", "reg_no", "email", "amount")
        widgets = {'fullName': forms.HiddenInput(),'reg_no': forms.HiddenInput(),'email': forms.HiddenInput() }