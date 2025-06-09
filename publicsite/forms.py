from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class ContactForms(forms.Form):
    messsage_sender = forms.CharField(label='Your Name', required=True, widget=forms.TextInput(attrs={'class': 'form-control valid-character'}))
    messsage_email = forms.EmailField(label='Your Email Address', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    messsage_phone = forms.CharField(label='Your Phone', required=True, widget=forms.TextInput(attrs={'class': 'form-control int-value'}))
    messsage_title = forms.CharField(label='Subject', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    messsage = forms.CharField(label='Type Message', required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    captcha = ReCaptchaField()
