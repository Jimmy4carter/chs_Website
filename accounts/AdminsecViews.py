import json
from textwrap import indent
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage


from django.http import HttpResponse

from django.core.mail import send_mass_mail, send_mail, EmailMultiAlternatives
import requests
from accounts.models import BilItems, Classes, ContactForm, CustomUser, FeedBackStaff, JuniorCost, MailMessage, SeniorCost, SessionYearModel, Staff, StaffPost, StudentAccount, StudentApplication, Students, Subjects, Subscribers, Terms
from chs_Website import settings
from publicsite.models import Events, JobApp
from django_pandas.io import read_frame

@login_required
def adminsec_home(request):
    get_students = Students.objects.all()
    all_students = get_students.count()
    active_student = get_students.filter(class_id__in=(1,2,3,4,5,6)).count()
    all_staff = Staff.objects.all().count()
    all_subjects = Subjects.objects.all().count()

    return render(request,"adminsec_template/adminsec_home.html", {"all_students":all_students,"active_student":active_student,"all_staff":all_staff,"all_subjects":all_subjects})

@csrf_exempt
def payment_history(request):



    headers = {
    'Content-type': 'application/json',
    'Authorization': 'Bearer sk_test_d208030e48844de7fa38521c170827f11e7a8766'
    }

    response = requests.get('https://api.paystack.co/transaction', headers=headers)

    response=response.json()['data']
    return render(request,"adminsec_template/payment_history.html",{"response":response})


    headers = {
    'Content-type': 'application/json',
    'Authorization': 'Bearer sk_test_d208030e48844de7fa38521c170827f11e7a8766'
    }

    response = requests.get('https://api.paystack.co/transaction', headers=headers)

    response=response.json()['data']
    return render(request,"adminsec_template/payment_history.html",{"response":response})

@login_required
def breakdown_action(request):
    items=BilItems.objects.all()
    list_data=[]
    if items!=None:
        for item in items:  
            se= SeniorCost.objects.get(reference_item=item)
            ju=JuniorCost.objects.get(reference_item=item)
            small_data={"id":item.id,"name":item.name,"fst_snew":se.first_new,"fst_sold":se.first_old,"sec_snew":se.second_new,"sec_sold":se.second_old,"trd_snew":se.third_new,"trd_sold":se.third_old,"fst_jnew":ju.first_new,"fst_jold":ju.first_old,"sec_jnew":ju.second_new,"sec_jold":ju.second_old,"trd_jnew":ju.third_new,"trd_jold":ju.third_old}
            list_data.append(small_data)

        return render(request,"adminsec_template/breakdown_action.html",{"list_data":list_data})
    else:
        messages.Error(request,"No Records Found")

@login_required
def breakdown_item_save(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        items=request.POST.get("item_name")
        fst_jnew=request.POST.get("fst_jnew")
        fst_jold=request.POST.get("fst_jold")
        sec_jnew=request.POST.get("sec_jnew")
        sec_jold=request.POST.get("sec_jold")
        trd_jnew=request.POST.get("trd_jnew")
        trd_jold=request.POST.get("trd_jold")
        fst_snew=request.POST.get("fst_snew")
        fst_sold=request.POST.get("fst_sold")
        sec_snew=request.POST.get("sec_snew")
        sec_sold=request.POST.get("sec_sold")
        trd_snew=request.POST.get("trd_snew")
        trd_sold=request.POST.get("trd_sold")

        try:
            item=BilItems.objects.create(name=items)
            
            senior=SeniorCost(first_new=fst_snew,first_old=fst_sold,second_new=sec_snew,second_old=sec_sold,third_new=trd_snew,third_old=trd_sold,reference_item=item)
            
            junior=JuniorCost(first_new=fst_jnew,first_old=fst_jold,second_new=sec_jnew,second_old=sec_jold,third_new=trd_jnew,third_old=trd_jold,reference_item=item)
            senior.save()
            junior.save()
            messages.success(request,items+"  Successfully Added")
            return HttpResponseRedirect(reverse("breakdown_action"))
        except:
            messages.error(request,"Failed To Addd Item")
            return HttpResponseRedirect(reverse("breakdown_action"))

@login_required
def delete_item(request,item_id):
    BilItems.objects.get(id=item_id).delete()
    return HttpResponseRedirect(reverse("breakdown_action"))

@login_required
def edit_items(request,item_id):
    items=BilItems.objects.all()
    list_data=[]
    if items!=None:
        for item in items:  
            se= SeniorCost.objects.get(reference_item=item)
            ju=JuniorCost.objects.get(reference_item=item)
            small_data={"id":item.id,"name":item.name,"fst_snew":se.first_new,"fst_sold":se.first_old,"sec_snew":se.second_new,"sec_sold":se.second_old,"trd_snew":se.third_new,"trd_sold":se.third_old,"fst_jnew":ju.first_new,"fst_jold":ju.first_old,"sec_jnew":ju.second_new,"sec_jold":ju.second_old,"trd_jnew":ju.third_new,"trd_jold":ju.third_old}
            list_data.append(small_data)

        return render(request,"adminsec_template/edit_breakdown_item.html",{"item_info":list_data})

@login_required
def item_edit_save(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        class_id=request.POST.get("class_id")
        class_category=request.POST.get("class_category")
        form_tutors=request.POST.get("form_tutor")
        classes=Classes.objects.get(id=class_id)
        form_tutor=CustomUser.objects.get(id=form_tutors)

        try:
            check_exist=ClassCategories.objects.filter(class_id=classes.id,name=class_category)
            if check_exist:
                category=ClassCategories.objects.get(class_id=classes,name=class_category)
                category.form_tutor=form_tutor
                category.save()
                messages.success(request,classes.name+" "+class_category+"  Successfully Updated")
                return HttpResponseRedirect(reverse("edit_class",kwargs={"class_id":class_id}))
            else:
                category=ClassCategories(class_id=classes,form_tutor=form_tutor,name=class_category)
                category.save()
                messages.success(request,classes.name+" "+class_category+"  Successfully Added")
                return HttpResponseRedirect(reverse("edit_class",kwargs={"class_id":class_id}))
        except:
            messages.error(request,"Failed To Update Class")
            return HttpResponseRedirect(reverse("edit_class",kwargs={"class_id":class_id}))


@login_required
def billing_action(request):
    return render(request,"adminsec_template/billing_action.html")

@login_required
def manual_bill(request):
    sessions=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"adminsec_template/man_bill.html",{"sessions":sessions,"classes":classes})

@login_required
def manual_pay(request):
    sessions=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"adminsec_template/man_pay.html",{"sessions":sessions,"classes":classes})

@csrf_exempt
def get_class(request):
    session_id=request.POST.get("session_id")
    class_ids=request.POST.get("classid")

    students=Students.objects.filter(class_id=class_ids,session_year_id=session_id)

    if students!=None:
        list_data=[]
        for student in students:
            check_exist=StudentAccount.objects.filter(students=student.admin)
            if check_exist:
                account=StudentAccount.objects.get(students=student.admin)
                last_update=str(account.updated_at)
                data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"to_pay":account.to_pay,"surplus":account.surplus,"last_update":last_update}
            else:
                data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"to_pay":"Null","surplus":"Null","last_update":"Null"}
            
            list_data.append(data_small)
            
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    else:
        messages.error(request,"No Records Found")


@csrf_exempt
def bill_class(request):
    session_id=request.POST.get("session_id")
    class_ids=request.POST.get("classid")
    username=request.POST.get("username")
    amount=int(request.POST.get("amount"))
    students=CustomUser.objects.get(username=username)

    try:
        account=StudentAccount.objects.filter(students=students)
        if account:
            acc=StudentAccount.objects.get(students=students)
            if acc.surplus>amount:
                balance=acc.surplus - amount
                acc.surplus=balance
                acc.latest_bill=amount
                acc.save()
            elif amount>acc.surplus:
                bal=amount - acc.surplus
                balance=bal + acc.to_pay
                acc.surplus=0
                acc.to_pay=balance
                acc.latest_bill=amount
                acc.save()
            elif amount==acc.surplus:
                acc.to_pay=0
                acc.surplus=0
                acc.latest_bill=amount
                acc.save()
        
        else:
            StudentAccount.objects.create(students=students,to_pay=amount,surplus=0)

        students=Students.objects.filter(class_id=class_ids,session_year_id=session_id)
        if students!=None:
            list_data=[]
            for student in students:
                check_exist=StudentAccount.objects.filter(students=student.admin)
                if check_exist:
                    account=StudentAccount.objects.get(students=student.admin)
                    last_update=str(account.updated_at)
                    data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"to_pay":account.to_pay,"surplus":account.surplus,"last_update":last_update}
                else:
                    data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"to_pay":"Null","surplus":"Null","last_update":"Null"}
                
                list_data.append(data_small)
                
            return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    except:
        messages.error(request,"Failed to bill Student")
        return HttpResponseRedirect(reverse("manual_bill"))

@csrf_exempt
def pay_save (request):
    session_id=request.POST.get("session_id")
    class_ids=request.POST.get("classid")
    username=request.POST.get("username")
    amount=int(request.POST.get("amount"))
    students=CustomUser.objects.get(username=username)

    try:
        std_account = StudentAccount.objects.get(students_id=students)
        std_account.total_payed =  std_account.total_payed + amount
        if amount >= std_account.to_pay:
            surplus = amount - std_account.to_pay
            std_account.surplus = std_account.surplus + surplus
            std_account.to_pay = 0
        else:
             std_account.to_pay = std_account.to_pay - amount

        std_account.save()

        students=Students.objects.filter(class_id=class_ids,session_year_id=session_id)
        if students!=None:
            list_data=[]
            for student in students:
                check_exist=StudentAccount.objects.filter(students=student.admin)
                if check_exist:
                    account=StudentAccount.objects.get(students=student.admin)
                    last_update=str(account.updated_at)
                    data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"to_pay":account.to_pay,"surplus":account.surplus,"last_update":last_update}
                else:
                    data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"to_pay":"Null","surplus":"Null","last_update":"Null"}
                
                list_data.append(data_small)
                
            return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    except:
        messages.error(request,"Failed to bill Student")
        return HttpResponseRedirect(reverse("manual_bill"))



@login_required
# To be implemented later
def billings(request):
    sessions=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"adminsec_template/get_students.html",{"sessions":sessions,"classes":classes})

@login_required
def bill_student(request,students_id):
    student_info = Students.objects.get(admin=students_id)
    session_year=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"adminsec_template/billings.html",{"student_info":student_info,"session_year":session_year,"classes":classes})


@login_required
def bill_student_save(request):
    term=int(request.POST.get('terms'))
    std_type=int(request.POST.get('std_type'))
    student_id=request.POST.get('student_id')
    session_year=request.POST.get('session_id')
    discount=request.POST.get('discounts')
    class_id=int(request.POST.get('class_id'))

    student_info=Students.objects.get(id=student_id)
    term=Terms.objects.get(id=term)
    session_year=SessionYearModel.objects.get(id=session_year)
    
    items=BilItems.objects.all()
    if class_id>3:
        if term==1:
            if std_type==1:
                for item in items:
                    cost=SeniorCost.objects.get(reference_item=item.id)

                    print(item.name,cost.first_new)
            elif std_type==2:
                for item in items:
                    cost=SeniorCost.objects.get(reference_item=item.id)

                    print(item.name,cost.first_old)

        elif term==2:
            if std_type==1:
                for item in items:
                    cost=SeniorCost.objects.get(reference_item=item.id)

                    print(item.name,cost.second_new)
            elif std_type==2:
                for item in items:
                    cost=SeniorCost.objects.get(reference_item=item.id)

                    print(item.name,cost.second_old)
        elif term==3:
            if std_type==1:
                for item in items:
                    cost=SeniorCost.objects.get(reference_item=item.id)

                    print(item.name,cost.third_new)
            elif std_type==2:
                for item in items:
                    cost=SeniorCost.objects.get(reference_item=item.id)

                    print(item.name,cost.third_old)
    else:
        for item in items:
            cost=JuniorCost.objects.get(reference_item=item.id)
            print(item.name,cost.first_new)


    messages.error(request,"Failed To Addd Item")
    return HttpResponseRedirect(reverse("bill_student"))

# to be implemented later ends






@login_required
def adminsec_students(request):
    sessions=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"adminsec_template/adminsec_students.html",{"sessions":sessions,"classes":classes})

@csrf_exempt
def adminsec_get_students(request):
    session_id=request.POST.get("session_id")
    class_ids=request.POST.get("classid")
    all_stud=class_ids+session_id
    if all_stud=='00':
        students=Students.objects.all()
    elif  session_id=='0':
        the_class=Classes.objects.get(id=class_ids)
        students=Students.objects.filter(class_id=the_class)
    elif class_ids=='0':   
        the_session=SessionYearModel.objects.get(id=session_id)
        students=Students.objects.filter(session_year_id=the_session)
    else:
        students=Students.objects.filter(class_id=class_ids,session_year_id=session_id)

    if students!=None:
        list_data=[]
        for student in students:
            data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"gender":student.gender,"profile_pic":str(student.profile_pic)}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    else:
        messages.Error(request,"No Records Found")

@login_required
def adminsec_profile(request):
    return render(request,"adminsec_template/adminsec_profile.html")

@login_required
def adminsec_feedback(request):
    staff_id=Staff.objects.get(admin=request.user.id)
    feedback_data=FeedBackStaff.objects.filter(staff_id=staff_id)
    return render(request,"adminsec_template/adminsec_feedback_template.html",{"feedback_data":feedback_data})

@login_required
def adminsec_feedback_save(request):

    if request.method!="POST":
        return HttpResponseRedirect(reverse("adminsec_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaff(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
             
            messages.success(request,"Feedback Successfully Sent")
            return HttpResponseRedirect(reverse("adminsec_feedback"))
        except:
            messages.error(request,"Failed To Send Feedback")
            return HttpResponseRedirect(reverse("adminsec_feedback"))

@login_required
def adminsec_view_subjects(request):
    subjects=Subjects.objects.all()
    return render(request,"public_template/index.html",{"subjects":subjects})

@login_required
def newsletter_compose(request):
    if request.method!="POST":
        return render(request,"adminsec_template/newsletter.html")
    else:
        title=request.POST.get('title')
        subject=request.POST.get('subject')
        message=request.POST.get('message')


        messsage_emails=settings.EMAIL_HOST_USER


        try:
            if title=="all":
                parent = Students.objects.values_list('parent_email', flat=True)
                p_list = list(parent)
    
                none = Subscribers.objects.values_list('email', flat=True)
                s_list = list(none)
                mail_list=p_list+s_list
                
                html_content=message
                msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
                msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
                msg.send()
                
    
            elif title=="parent":
                parent = Students.objects.values_list('parent_email', flat=True)
                mail_list = list(parent)
                html_content=message
                msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
                msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
                msg.send() 
    
    
            elif title=="non_parent":
                none=Subscribers.objects.values_list('email', flat=True)
                mail_list = list(none)
                html_content=message
                msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
                msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
                msg.send() 
            
            elif title=="staff":
                none=CustomUser.objects.exclude(user_type =3)
                df = none.values_list('email', flat=True)
                mail_list = list(df)
                html_content=message
                msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
                msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
                msg.send() 
            
            elif title=="test":
                mail_list=['christhighschool2015@gmail.com','jimmy4carter@gmail.com']
                html_content=message
                msg = EmailMultiAlternatives(subject, message, messsage_emails, mail_list,)                                      
                msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
                msg.send()
    
            messages.success(request,"Mail Sent")
            return HttpResponseRedirect(reverse("newsletter_compose"))

        # try:
        res=[]
        if title=="all":
            parent=Students.objects.all()       
            df = read_frame(parent, fieldnames=['parent_email'])
            p_list = df['parent_email'].values.tolist()

            none=Subscribers.objects.all()
            df = read_frame(none, fieldnames=['email'])
            s_list = df['email'].values.tolist()
            mail_list=p_list+s_list
            
            html_content=message
            msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
            msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
            msg.send()
            

        elif title=="parent":
            parent=Students.objects.all()       
            df = read_frame(parent, fieldnames=['parent_email'])
            mail_list = df['parent_email'].values.tolist()
            html_content=message
            msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
            msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
            msg.send() 


        elif title=="non_parent":
            none=Subscribers.objects.all()
            df = read_frame(none, fieldnames=['email'])
            mail_list = df['email'].values.tolist()
            html_content=message
            msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
            msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
            msg.send() 
        
        elif title=="staff":
            none=CustomUser.objects.exclude(user_type =3)
            df = read_frame(none, fieldnames=['email'])
            mail_list = df['email'].values.tolist()
            html_content=message
            msg = EmailMultiAlternatives(subject, message, messsage_emails, bcc=mail_list,)                                      
            msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
            msg.send() 
        
        elif title=="test":
            mail_list=['christhighschool2015@gmail.com','jimmy4carter@gmail.com']
            html_content=message
            msg = EmailMultiAlternatives(subject, message, messsage_emails, mail_list,)                                      
            msg.attach_alternative(html_content, "text/html")                                                                                                                                                                             
            msg.send()


        messages.success(request,"Mail Sent")
        return HttpResponseRedirect(reverse("newsletter_compose"))

        # except:
        #     messages.error(request,"Failed to send mail")
        #     return HttpResponseRedirect(reverse("newsletter_compose"))


@csrf_exempt
def adminsec_message(request):
    if request.method!="POST":
        mes=ContactForm.objects.all()
        return render(request,"adminsec_template/messages.html",{"mes":mes})
    else:
        # try:
        reply_id=request.POST.get('id')
        subject_mail=request.POST.get('title')
        reply_message=request.POST.get('message')
        reply_email=request.POST.get('email')

        from_emails=settings.EMAIL_HOST_USER
        send_mail(subject_mail, reply_message,from_emails,reply_email)
        reply=ContactForm.objects.get(id=reply_id)
        reply.reply=reply_message
        reply.save()
        return HttpResponse("True")
        # except:
        #     return HttpResponse("False")

@csrf_exempt
def student_application(request):
    if request.method!="POST":
        job=StudentApplication.objects.all()
        return render(request,"adminsec_template/student_applications.html",{'job':job})
    else:
        try:
            job_id=int(request.POST.get('id'))
            job=StudentApplication.objects.get(id=job_id)
            job.status=1
            job.save()
            return HttpResponse("OK")
        except:
            return HttpResponse("False")

@csrf_exempt
def job_application(request):
    if request.method!="POST":
        jobs=JobApp.objects.all()
        return render(request,"adminsec_template/job_applications.html",{"jobs":jobs})
    else:
        try:
            job_id=int(request.POST.get('id'))
            job=JobApp.objects.get(id=job_id)
            job.status=1
            job.save()
            return HttpResponse("OK")
        except:
            return HttpResponse("False")

@login_required
def add_event(request):
    if request.method!="POST":
        all_events=Events.objects.all()
        return render(request,"adminsec_template/add_events.html",{"all_events":all_events})

    else:
        title=request.POST.get('title')
        location=request.POST.get('location')
        year=request.POST.get('year')
        month=request.POST.get('months')
        day=request.POST.get('day')
        blog_post=request.POST.get('blog_post')
         
        future_image = request.FILES['future_image']
        fs=FileSystemStorage()
        filename=fs.save(future_image.name,future_image)
        future_image_url=fs.url(filename)

        try:
           Events.objects.create(event_title=title,event_location=location,event_year=year,event_month=month,event_day=day,blog_post=blog_post,future_image=future_image_url)
           messages.success(request,"Event Cataloged")
           return HttpResponseRedirect(reverse("add_event"))
        except:
            messages.error(request,"Failed To Catalog Event")
            return HttpResponseRedirect(reverse("add_event"))


@login_required
def adminsec_staff_todo(request):
    return render(request,"adminsec_template/adminsec_staff_todo.html")

@login_required
def add_posts(request):
    if request.method!="POST":
        return render(request,"adminsec_template/add_posts.html")
    else:
        # try:
            name=request.POST.get('name')
            spec=request.POST.get('spec')
            StaffPost.objects.update_or_create(post_name=name,spec=spec)
            messages.success(request,"Staff Post Updated Seccessfully")
            return HttpResponseRedirect(reverse("add_posts"))
        # except:
        #     messages.error(request,"Failed To Update Staff Post")
        #     return HttpResponseRedirect(reverse("add_posts"))


@login_required
def assign_post(request):
    if request.method!="POST":
        staff=Staff.objects.all()
        posts=StaffPost.objects.all()
        return render(request,"adminsec_template/assign_post.html",{"staff":staff,"posts":posts})
    else:
        staff_id=request.POST.get("staff")
        posts=request.POST.get("posts")
        try:
            Staff.objects.filter(id=staff_id).update(post_held=posts)
            messages.success(request,"Staff Post Updated Seccessfully")
            return HttpResponseRedirect(reverse("assign_post"))
        except:
            messages.error(request,"Failed To Update Staff Post")
            return HttpResponseRedirect(reverse("assign_post"))

@login_required
def adminsec_staff(request):
    staff=Staff.objects.all()
    return render(request,"adminsec_template/adminsec_staff.html",{"staff":staff})

def assign_task(request):
    staff=Staff.objects.all()
    return render(request,"adminsec_template/adminsec_staff.html",{"staff":staff})
