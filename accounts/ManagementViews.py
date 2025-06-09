from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def management_home(request):
    return render(request,"admin_template/promote_class.html")
