
import json
from django.db.models.query_utils import subclasses
from django.http.response import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser, Subscribers
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from accounts.EmailBackEnd import EmailBackEnd

# Create your views here.
def error_404(request, exception):
    return render(request, "404.html")

def ShowDemoPage(request):
    return render(request,"demo.html")

def ShowLoginPage(request):
    return render(request,"login.html")

def doLogin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user!=None:
            login(request,user)
            if user.user_type=="1":
                login(request,user)
                return HttpResponseRedirect('/admin_home')
            elif user.user_type=="3":
                return HttpResponseRedirect(reverse("students_home"))
            elif user.user_type=="2":
                return HttpResponseRedirect(reverse("tutors_home"))
            elif user.user_type=="4":
                return HttpResponseRedirect(reverse("principal_home"))
            elif user.user_type=="5":
                return HttpResponseRedirect(reverse("adminsec_home"))
            elif user.user_type=="6":
                return HttpResponseRedirect(reverse("management_home"))
            elif user.user_type=="7":
                return HttpResponseRedirect(reverse("hostel_home"))
            elif user.user_type=="8":
                return HttpResponseRedirect(reverse("tuckshop_home"))
            else:
                messages.error(request,"You Are Not Authorised For Login")
                return HttpResponseRedirect("/login")
        else:
            messages.error(request,"Invalid Login Details")
            return HttpResponseRedirect("/login")


def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+request.user.user_type)
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/login")

def showFirebaseJs(request):
    data=   'importScripts("https://www.gstatic.com/firebasejs/8.8.1/firebase-app.js");'\
            'importScripts("https://www.gstatic.com/firebasejs/8.8.1/firebase-messaging.js");'\
            'var firebaseConfig = {'\
            '    apiKey: "AIzaSyDtfwAKSON_fi5_bta3Cc8B0SDz24oSRos",'\
            '    authDomain: "chswebsite-ebd88.firebaseapp.com",'\
            '    projectId: "chswebsite-ebd88",'\
            '    storageBucket: "chswebsite-ebd88.appspot.com",'\
            '    messagingSenderId: "97644228824",'\
            '    appId: "1:97644228824:web:da392dab4d7c222ff6e7ad",'\
            '    measurementId: "G-XB1DDKLBG4"'\
            '};'\
            'firebase.initializeApp(firebaseConfig);'\
            'const messaging=firebase.messaging();'\
            'messaging.setBackgroundMessageHandler(function (payload){'\
            '    console.log(payload)'\
            '    const notification=JSON.parse(payload);'\
            '    const notificationOption={'\
            '        body:notification.body,'\
            '        icon:notification.icon,'\
            '    };'\
            '    return self.registration.showNotification(payload.notification.title,notification);'\
            '});'
    return HttpResponse(data)

@csrf_exempt
def new_subcriber(request):
    if request.method=='POST':
        emails = request.POST.get('email')
        check=Subscribers.objects.filter(email=emails)
        if check:
            return HttpResponse("Exist")
        else:
            subscriber=Subscribers(email=emails)
            subscriber.save()
            return HttpResponse("OK")