from django.views import View
from django.shortcuts import render

def EditResultViewClass(View):
    def get(self,request,*args, **kwargs):
        return render(request,"edit_student_result.html")

    def post(self,request,*args, **kwargs):
        pass