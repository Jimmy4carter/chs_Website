from django.urls import path
from paystackpayments import views

urlpatterns = [
     path('initiate_payment/', views.initiate_payment, name="initiate_payment"),
     path('initiate_payment/<str:ref>/', views.verify_payment, name="verify_payment"),
     path('paystack_webhook', views.paystack_webhook, name="paystack_webhook"),
     path('verify_application/<str:ref>/', views.verify_application, name="verify_application"),

]
