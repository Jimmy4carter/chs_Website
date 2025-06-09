
import django
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.conf import settings
from django.core.mail import send_mail
from paystackpayments.forms import PaymentForm
from paystackpayments.models import Payment
from publicsite.models import CBTresult, Events, JobApp
from accounts.models import CustomUser, ContactForm, Staff, Students, StudentApplication
from operator import attrgetter
from chs_Website import settings
from .forms import ContactForms


def ShowHomePage(request):
    all_events=Events.objects.all()
    return render(request,"public_template/index.html",{"all_events":all_events})

def about_us(request):
    return render(request, "public_template/about_us.html")
    
def our_programs(request):
    return render(request, "public_template/our_programs.html")

def school_facilities(request):
    return render(request, "public_template/school_facilities.html")

def our_gallery(request):
    return render(request, "public_template/our_gallery.html")

def our_events(request):
    all_events=Events.objects.all()
    return render(request, "public_template/our_events.html",{"all_events":all_events})

def our_team(request):
    team=Staff.objects.all().order_by('post_held')
    boards=team.filter(post_held__spec__contains=1)
    acad=team.filter(post_held__spec__contains=2)
    nonacad=team.filter(post_held__spec__contains=3)
    return render(request, "public_template/our_team1.html",{"boards":boards,"acad":acad,"nonacad":nonacad})


def contact_us(request):
    if request.method == 'POST':
        form = ContactForms(request.POST)

        # Check if the reCAPTCHA field is valid
        if form.is_valid() and form.cleaned_data['captcha']:
            messsage_sender = form.cleaned_data['messsage_sender']
            messsage_email = form.cleaned_data['messsage_email']
            messsage_phone = form.cleaned_data['messsage_phone']
            messsage_title = form.cleaned_data['messsage_title']
            messsage = form.cleaned_data['messsage']
    
            mail_subject = "Thank you for contacting CHS."  # subject
            message = "We have received your message and will review it. We will get back to you as soon as possible."  # message
    
            try:
                from_emails = settings.EMAIL_HOST_USER
                messsage_email = messsage_email.split()
                send_mail(mail_subject, message, from_emails, messsage_email)
    
                ContactForm.objects.create(name=messsage_sender, email=messsage_email, phone=messsage_phone,
                                           title=messsage_title, message=messsage)
    
                messages.success(request, "Message received. We'll get back to you shortly.")
                return HttpResponseRedirect(reverse("contact_us"))
            except Exception as e:
                messages.error(request, f"Failed to send message: {str(e)}")
                return HttpResponseRedirect(reverse("contact_us"))
        else:
            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue
                messages.error(request, error)
    else:
        form = ContactForms()
    return render(request, "public_template/contact_us.html", {'form': form})



def apply_action(request):
    return render(request, "public_template/apply_action.html")

def apply_job(request):
    if request.method=="POST":
        name=request.POST.get('name')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        qualification=request.POST.get('qualification')
        
        try:
            letter = request.FILES['letter']
            fs=FileSystemStorage()
            filename=fs.save(letter.name,letter)
            letter_url=fs.url(filename)

            cv = request.FILES['cv']
            fs=FileSystemStorage()
            filename=fs.save(cv.name,cv)
            cv_url=fs.url(filename)

            JobApp.objects.create(name=name,phone=phone,email=email,qualification=qualification,letter=letter_url,cv=cv_url)

            messages.success(request,"You Have Successfully Applied!")
            return HttpResponseRedirect(reverse("apply_job"))
        except:
            messages.error(request,"Application Failed, Please Try Again")
            return HttpResponseRedirect(reverse("apply_job"))
    else:
        return render(request, "public_template/apply_job.html")


# def apply_school(request):
#     if request.method=="POST":
#         surname=request.POST.get('surname')
#         other_name=request.POST.get('other_name')
#         dob=request.POST.get('dob')
#         gender=request.POST.get('gender')
#         SOO=request.POST.get('SOO')
#         religion=request.POST.get('religion')
#         email=request.POST.get('email')
#         contact_phone=request.POST.get('contact_phone')
#         former_school=request.POST.get('former_school')
#         former_shcool_phone=request.POST.get('phone')
#         applying_for=request.POST.get('applying_for')

#         # StudentApplication.objects.create(surname=surname,other_name=other_name,dob=dob,gender=gender,soo=SOO,religion=religion,contact_email=email,contact_phone=contact_phone,former_school=former_school,school_phone=former_shcool_phone,applying_for=applying_for)
#         # data={"fullName":surname+" "+other_name,"amount":7500,"email":email,"reg_no":"Application Form"}
#         # payment_form = PaymentForm(data)

#         # if payment_form.is_valid():
#         #     payment=payment_form.save()
#         #     return render(request, 'application_payment.html', {'payment': payment, 'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY})
            
#         return render(request, 'application_payment.html', {'paystack_public_key': "A payment of #7,500 most be made for your application will be processed"})


#     else:
#         return render(request, "public_template/apply_school.html")


def apply(request):
    if request.method == "POST":
        # Retrieve data from the form
        surname = request.POST.get("surname")
        other_name = request.POST.get("other_name")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        soo = request.POST.get("SOO")
        religion = request.POST.get("religion")
        contact_email = request.POST.get("email")
        contact_phone = request.POST.get("contact_phone")
        former_school = request.POST.get("former_school")
        school_phone = request.POST.get("phone")
        applying_for = request.POST.get("applying_for")

        # Save data to the StudentApplication model
        student_application = StudentApplication(
            surname=surname,
            other_name=other_name,
            dob=dob,
            gender=gender,
            soo=soo,
            religion=religion,
            contact_email=contact_email,
            contact_phone=contact_phone,
            former_school=former_school,
            school_phone=school_phone,
            applying_for=applying_for,
        )
        student_application.save()

        # Redirect to success page
        return render(request, 'public_template/schoolsucces.html')

    # If the request method is not POST, render the form
    return render(request, 'public_template/apply_school.html')

def apply_success(request):
    if request.method=="POST":
        exam_date=request.POST.get('exam_date')
        ref = request.POST.get('ref')

        messages.success(request, "Entrance Exam scheduled for "+ str(exam_date))
        return HttpResponseRedirect(reverse("contact_us"))





def application_notice(request):
    return render(request, "public_template/application_note.html")


def faqs(request):
    return render(request, "public_template/faqs.html")
    
    
def jambcbt(request):
    if request.method=="POST":
        stdid = request.POST.get('stdid')
        # try:
        reg = CustomUser.objects.get(username = stdid)
        
        student_results = []
        if reg.user_type == '3':
            student = Students.objects.get(admin=reg)
            
            cbt_results = CBTresult.objects.filter(student_id = student)
            
            student_results.append({
                'student': student,
                'cbt_results': cbt_results,
            }) 
            
            
            return render(request, "public_template/jambcbt.html",{"student_results": student_results})
        else:
            
            students_class_6 = Students.objects.filter(class_id=6)
            # Create a list to store student information along with their CBT results

            for student in students_class_6:
                # Retrieve CBT results for the current student
                cbt_results = CBTresult.objects.filter(student_id=student)

                # Check if the student has CBT results
                if cbt_results.exists():
                    cbt_result = sorted(cbt_results, key=attrgetter('entrydate'), reverse=False)
                    # Append the student and their CBT results to the list
                    student_results.append({
                        'student': student,
                        'cbt_results': cbt_result,
                    })               
                    
            return render(request, "public_template/jambcbt.html",{"student_results": student_results})
                
        # except:
        #     messages.error(request,"Invalid registration number. Please check and try again")
        #     return HttpResponseRedirect(reverse("jambcbt"))
    else:
        return render(request, "public_template/jambcbt.html")

    
    