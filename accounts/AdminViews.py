
import json
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from accounts.forms import AddStudentForm, EditStudentForm, StudyMaterialForm
from os import name
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from accounts.models import Attendance, AttendanceReport, ClassCategories, Classes,CombineEndTerm, CombineMidTerm, CombineSubjects, CustomUser, EntryAttestation, ExamFile, FeedBackStaff, FeedBackStudent, LeaveReport, NotificationStaff, NotificationStudent, OldCummulative, OldResults, SiteControls, SessionYearModel,Staff, StudentExitReport, Students, Subjects, StudyMaterial, Terms,SubjectsAllo, EndTerm, MidTerm,ClassAverage,AffectiveDomain,Psycomotor
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from hostel.models import Hostel, Rooms, Logbook, Allocations, StudentEthosRecords
from onlinecbt.models import ObjectiveQuestion, Quiz, QuizSchedule, TheoryQuestion
from django.db.models import Sum
from django.template.defaultfilters import linebreaksbr
from publicsite.models import CBTresult
from django.db import transaction
import math
from datetime import datetime



@login_required
def admin_home(request):
    student_count=Students.objects.all().count()
    subject_count=Subjects.objects.all().count()
    class_count=Classes.objects.all().count()
    staff_count=Staff.objects.all().count()

    class_all=Classes.objects.all()
    class_name_list=[]
    subject_count_list=[]
    student_count_list_in_class=[]
    for classes in class_all:
        subjects=Subjects.objects.filter(class_id=classes.id).count()
        students=Students.objects.filter(class_id=classes.id).count()
        class_name_list.append(classes.name)
        subject_count_list.append(subjects)
        student_count_list_in_class.append(students)
    

    subjects_all=Subjects.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        classs=Classes.objects.get(id=subject.class_id.id)
        students_count=Students.objects.filter(class_id=classs.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(students_count)


    staffs=Staff.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subjects.objects.filter(tutor=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves=LeaveReport.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)


    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=StudentExitReport.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)


    return render(request,"admin_template/home_content.html",{"student_count":student_count,"staff_count":staff_count,"subject_count":subject_count,"class_count":class_count,"class_name_list":class_name_list,"subject_count_list":subject_count_list,"student_count_list_in_class":student_count_list_in_class,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"staff_name_list":staff_name_list,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student})

@login_required
def staff_action(request):
    return render(request, "admin_template/staff_action.html")

@login_required
def view_staffs(request):
    staffs=Staff.objects.all()
    return render(request,"admin_template/view_staff.html",{"staffs":staffs})

@login_required
def add_staff(request):
    return render(request, "admin_template/add_staff_template.html")

@login_required
def add_staff_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        staff_type=request.POST.get("staff_type")
        staff_phone=request.POST.get("staff_phone")
        staff_role=request.POST.get("staff_role")
        dob=request.POST.get("dob")
        contact_name=request.POST.get("contact_name")
        contact_phone=request.POST.get("contact_phone")
        relationship=request.POST.get("relationship")

        staff_type=int(staff_type)

        profile_pic = request.FILES['profile_pic']
        fs=FileSystemStorage(location="/home/chrijpdc/public_html/media/")
        filename=fs.save(profile_pic.name,profile_pic)
        profile_pic_url=fs.url(filename)

        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=staff_type)
            user.staff.address=address
            user.staff.profile_pic=profile_pic_url
            user.staff.phone=staff_phone
            user.staff.role=staff_role
            user.staff.dob=dob
            user.staff.contact_name=contact_name
            user.staff.contact_phone=contact_phone
            user.staff.contact_rel=relationship
            user.save()
            messages.success(request,"Staff Successfully Added")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request,"Failed to Save")
            return HttpResponseRedirect(reverse("add_staff"))

@login_required
def manage_staff(request):
    staff = Staff.objects.all()
    return render(request, "admin_template/manage_staff_template.html",{"staff":staff})

@login_required
def edit_staff(request,staff_id):
    staff = Staff.objects.get(admin=staff_id)
    return render (request, "admin_template/edit_staff_template.html",{"Staff":staff,"id":staff_id})

@login_required
def edit_staff_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            staff_id=request.POST.get("staff_id")
            first_name=request.POST.get("first_name")
            last_name=request.POST.get("last_name")
            email=request.POST.get("email")
            password=request.POST.get("password")
            address=request.POST.get("address")
            staff_type=request.POST.get("staff_type")
            staff_phone=request.POST.get("staff_phone")
            staff_role=request.POST.get("staff_role")
            contact_name=request.POST.get("contact_name")
            contact_phone=request.POST.get("contact_phone")
            relationship=request.POST.get("relationship")

            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            if staff_type!=None and staff_type!="":
                user.user_type=staff_type
            if password!=None and password!="":
                user.set_password(password)

            user.staff.phone=staff_phone
            if staff_role!=None and staff_role!="":
                user.staff.role=staff_role
            user.staff.contact_name=contact_name
            user.staff.contact_phone=contact_phone
            user.staff.contact_rel=relationship
            user.save()

            staff_model=Staff.objects.get(admin=staff_id)
            staff_model.address=address
            staff_model.save()
            messages.success(request,"Profile Successfully Updated")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))
        except:
            messages.error(request,"Failed To Update Profile")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))

@login_required
def add_classes(request):
    staff=CustomUser.objects.filter(user_type=2)
    return render(request, "admin_template/add_classes_template.html",{"staff":staff})

@login_required
def add_class_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")

    else:
        class_name=request.POST.get("class_name")


        try:
            classes=Classes(name=class_name)
            classes.save()

            messages.success(request,class_name+"  Successfully Added")
            return HttpResponseRedirect(reverse("add_classes"))
        except:
            messages.error(request,"Failed To Add New Class")
            return HttpResponseRedirect(reverse("add_classes"))


@login_required
def manage_classes(request):
    classes = Classes.objects.all()
    class_category=ClassCategories.objects.all()
    return render(request, "admin_template/manage_class_template.html",{"classes":classes,"class_category":class_category})

@login_required
def edit_class(request,class_id):
    classes=Classes.objects.get(id=class_id)
    tutors=CustomUser.objects.filter(user_type=2)
    return render(request, "admin_template/edit_class_template.html",{"classes":classes,"staff":tutors })

@login_required
def edit_class_save(request):
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
def add_subjects(request):
    classes=Classes.objects.all()
    staff=CustomUser.objects.filter(user_type=2).order_by('last_name')
    mainsub=Subjects.objects.all().order_by('outline')
    return render(request, "admin_template/add_subjects_template.html",{"classes":classes,"staff":staff,"mainsub":mainsub})

@login_required
def add_subject_save(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        subject_name=request.POST.get("subject_name")
        classes_id=request.POST.get("classes")
        classes=Classes.objects.get(id=classes_id)
        staff_id=request.POST.get("tutor")
        outline=request.POST.get("subject_code")
        term1_res = request.FILES['term1_resources']
        term2_res = request.FILES['term2_resources']
        term3_res = request.FILES['term3_resources']

        fs=FileSystemStorage(location="/home/chrijpdc/public_html/media/subject_resources/")
        term1=fs.save(term1_res.name,term1_res)
        term2=fs.save(term2_res.name,term2_res)
        term3=fs.save(term3_res.name,term3_res)
        term1_resources=fs.url("subject_resources/"+term1)
        term2_resources=fs.url("subject_resources/"+term2)
        term3_resources=fs.url("subject_resources/"+term3)
        
        
        try:
            subject=Subjects(subject_name=subject_name,outline=outline,class_id=classes,tutor_id=staff_id,term1_resources=term1_resources,term2_resources=term2_resources,term3_resources=term3_resources)
            subject.save()
            messages.success(request,"Subject Successfully Added")
            return HttpResponseRedirect(reverse("add_subjects"))
        except:
            messages.error(request,"Failed To Save")
            return HttpResponseRedirect(reverse("add_subjects"))

@login_required            
def add_combinesubject(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        subject_name=request.POST.get("subject_name")
        mainsubject=request.POST.get('mainsub')
        mainsubject=Subjects.objects.get(id=mainsubject)
        staff_id=request.POST.get('tutor')
  
        try:
            subject=CombineSubjects(name=subject_name,subject_main=mainsubject,tutor_id=staff_id)
            subject.save()
            messages.success(request,"Subject Successfully Added")
            return HttpResponseRedirect(reverse("add_subjects"))
        except:
            messages.error(request,"Failed To Save")
            return HttpResponseRedirect(reverse("add_subjects"))


@login_required
def view_classes(request):
    classes=Classes.objects.all()
    class_category=ClassCategories.objects.all()
    return render(request,"admin_template/view_classes.html",{'classes':classes,"class_category":class_category})

@login_required
def manage_subjects(request):
    subjects = Subjects.objects.all()
    combinesub=CombineSubjects.objects.all()
    return render(request, "admin_template/manage_subjects_template.html",{"subjects":subjects,"combinesub":combinesub})

@login_required
def edit_subjects(request,subject_id):
    subject=Subjects.objects.get(id=subject_id)
    classes=Classes.objects.all()
    staff=CustomUser.objects.filter(user_type=2)
    class_c = ClassCategories.objects.filter(class_id=subject.class_id)
    return render(request, "admin_template/edit_subjects_template.html",{"subject":subject,"classes":classes,"staff":staff,"id":subject_id,"class_c":class_c})

@login_required
def edit_combinesub(request,subject_id):
        subject=CombineSubjects.objects.get(id=subject_id)
        classes=Classes.objects.all()
        staff=CustomUser.objects.filter(user_type=2)
        return render(request, "admin_template/edit_subjects_template.html",{"combsubj":subject,"classes":classes,"staff":staff,"id":subject_id})
  
@login_required  
def edit_save_comb(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get('subject_id')
        name=request.POST.get("subject_name")
        staff_id=request.POST.get("tutor")
        
        try:
            subject=CombineSubjects.objects.get(id=subject_id)
            subject.name=name
            tutor=CustomUser.objects.get(id=staff_id)
            subject.tutor=tutor
            subject.save()
            messages.success(request,name+"  For  "+name+"   Successfully Updated")
            return HttpResponseRedirect(reverse("edit_combinesub",kwargs={"subject_id":subject_id}))
        except:
            messages.error(request,name+" Failed To Update")
            return HttpResponseRedirect(reverse("edit_combinesub",kwargs={"subject_id":subject_id}))
 
@login_required
def edit_subject_save(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get("subject_id")
        name=request.POST.get("subject_name")
        cat_name=request.POST.get('cat_name')
        classes_id=request.POST.get("classes")
        staff_id=request.POST.get("tutor")
        
        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.subject_name=name
            class_obj=Classes.objects.get(id=classes_id)
            subject.class_id=class_obj
            tutor=CustomUser.objects.get(id=staff_id)
            subject.tutor=tutor
            subject.save()
            messages.success(request,name+"  For  "+class_obj.name+"   Successfully Updated")
            return HttpResponseRedirect(reverse("edit_subjects",kwargs={"subject_id":subject_id}))
        except:
            messages.error(request,name+" Failed To Update")
            return HttpResponseRedirect(reverse("edit_subjects",kwargs={"subject_id":subject_id}))
        
        # # try:
        # subject=Subjects.objects.get(id=subject_id)
        # subject.subject_name=name
        # class_obj=Classes.objects.get(id=classes_id)
        # subject.class_id=class_obj
        # tutor=CustomUser.objects.get(id=staff_id)
        # subject.tutor=tutor
        # subject.save()
        
        # cls_catobj=ClassCategories.objects.get(class_id=class_obj, name=cat_name)
        # check_exist=SubjectsAllo.objects.filter(subject=subject,class_cat=cls_catobj)
        # if check_exist:
        #     SubjectsAllo.objects.filter(subject=subject,class_cat=cls_catobj).update(tutor=tutor)
        # else:
        #     SubjectsAllo.objects.create(subject=subject,class_cat=cls_catobj,tutor=tutor)
            
        # messages.success(request,name+"  For  "+class_obj.name+"   Successfully Updated")
        # return HttpResponseRedirect(reverse("edit_subjects",kwargs={"subject_id":subject_id}))
        # # except:
        # #     messages.error(request,name+" Failed To Update")
        # #     return HttpResponseRedirect(reverse("edit_subjects",kwargs={"subject_id":subject_id}))

@login_required
def view_subjects(request):
    subjects=Subjects.objects.all()
    return render(request,"admin_template/view_subjects.html",{"subjects":subjects})


@login_required
def add_students(request):
    form=AddStudentForm()
    return render(request, "admin_template/add_student_template.html",{"form":form})

@login_required
def add_students_save(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            student_address=form.cleaned_data["address"]
            gender=form.cleaned_data["gender"]
            session_year_id=form.cleaned_data["session_year_id"]
            classes_id=form.cleaned_data["classes"]
            class_category=form.cleaned_data["class_category"]
            religion=form.cleaned_data["religion"]
            origin_state=form.cleaned_data["origin_state"]
            dobs=form.cleaned_data["dob"]
            parent_name=form.cleaned_data["parent_name"]
            parent_phone=form.cleaned_data["parent_phone"]
            parent_email=form.cleaned_data["parent_email"]
            admission_class=classes_id

            profile_pic = request.FILES['profile_pic']
            fs=FileSystemStorage(location="/home/chrijpdc/public_html/media/")
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
            # profile_pic_url='/media/IDUKO.png'
            
            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                class_obj=Classes.objects.get(id=classes_id)
                class_cat=ClassCategories.objects.get(class_id=class_obj,name=class_category)
                user.students.class_id=class_obj
                user.students.class_category=class_cat
                user.students.religion=religion
                user.students.origin_state=origin_state
                user.students.dob=dobs
                user.students.address=student_address
                user.students.profile_pic=profile_pic_url
                user.students.gender=gender
                user.students.admission_class=admission_class
                user.students.admission_ses=session_year_id
                user.students.parent_name=parent_name
                user.students.parent_email=parent_email
                user.students.parent_phone=parent_phone
                session_year=SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id=session_year
                user.save()
                messages.success(request,"Student Successfully Added")
                return HttpResponseRedirect(reverse("add_students"))
            except:
                messages.error(request,"Failed To Save")
                return HttpResponseRedirect(reverse("add_students"))
        else:
            form=AddStudentForm(request.POST)
            return render(request, "admin_template/add_student_template.html",{"form":form})

@login_required
def manage_students(request):
    students = Students.objects.all()
    return render(request, "admin_template/manage_students_template.html",{"students":students})


@login_required
def edit_student(request,students_id):
    request.session['students_id']=students_id
    students = Students.objects.get(admin=students_id)
    form=EditStudentForm()
    form.fields['email'].initial=students.admin.email
    form.fields['first_name'].initial=students.admin.first_name
    form.fields['last_name'].initial=students.admin.last_name
    form.fields['classes'].initial=students.class_id
    form.fields['gender'].initial=students.gender
    form.fields['session_year_id'].initial=students.session_year_id.id
    form.fields['address'].initial=students.address

    form.fields['class_category'].initial=students.class_category
    form.fields['religion'].initial=students.religion
    form.fields['origin_state'].initial=students.origin_state
    form.fields['dob'].initial=students.dob
    form.fields['parent_name'].initial=students.parent_name
    form.fields['parent_phone'].initial=students.parent_phone
    form.fields['parent_email'].initial=students.parent_email
    return render (request, "admin_template/edit_student_template.html",{"form":form,"id":students_id,"username":students.admin.username,"first_name":students.admin.first_name,"last_name":students.admin.last_name})


@login_required
def edit_student_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id=request.session.get("students_id")
        if student_id == None:
            return HttpResponseRedirect(reverse("manage_students"))

        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            email=form.cleaned_data["email"]
            student_address=form.cleaned_data["address"]
            gender=form.cleaned_data["gender"]
            session_year_id=form.cleaned_data["session_year_id"]
            classes_id=form.cleaned_data["classes"]
            classes_id=form.cleaned_data["classes"]
            class_category=form.cleaned_data["class_category"]
            religion=form.cleaned_data["religion"]
            origin_state=form.cleaned_data["origin_state"]
            dobs=form.cleaned_data["dob"]
            parent_name=form.cleaned_data["parent_name"]
            parent_phone=form.cleaned_data["parent_phone"]
            parent_email=form.cleaned_data["parent_email"]
            password = form.cleaned_data["password"]
            
            if request.FILES.get('profile_pic',False):
                profile_pic = request.FILES['profile_pic']
                fs=FileSystemStorage(location="/home/chrijpdc/public_html/media/")
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None

            try: 
                user=CustomUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.email=email
                # If password is provided, update it
                if password:
                    user.set_password(password)
            
                user.save()
    
                student=Students.objects.get(admin=student_id)
                student.address = student_address
                student.gender = gender
                if profile_pic_url != None:
                    student.profile_pic = profile_pic_url
                session_year=SessionYearModel.objects.get(id=session_year_id)
                student.session_year_id=session_year
                classes=Classes.objects.get(id=classes_id)
                student.class_id = classes
    
                class_cat=ClassCategories.objects.get(class_id=classes,name=class_category)
                student.class_category=class_cat
                student.religion=religion
                student.origin_state=origin_state
                student.dob=dobs
                student.parent_name=parent_name
                student.parent_email=parent_email
                student.parent_phone=parent_phone
    
                student.save()
                del request.session['students_id']
    
                messages.success(request,"Student Successfully Updated")
                return HttpResponseRedirect("edit_student/"+student_id)
            except:
                messages.error(request,"Failed To Update Profile")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"students_id":student_id}))
        else:
            form=EditStudentForm(request.POST)
            students=Students.objects.get(admin=student_id)
            return render(request,"admin_template/edit_student_template.html",{"form":form,"id":student_id,"username":students.admin.username,"first_name":students.admin.first_name,"last_name":students.admin.last_name})


@login_required
def view_students(request):
    sessions=SessionYearModel.objects.all()
    classes=Classes.objects.all()
    return render(request,"admin_template/view_students.html",{"sessions":sessions,"classes":classes})


@csrf_exempt
def query_view_students(request):
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
        students=Students.objects.filter(admission_ses=the_session)
    else:
        students=Students.objects.filter(class_id=class_ids,admission_ses=session_id)

    if students!=None:
        list_data=[]
        for student in students:
            data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"gender":student.gender,"profile_pic":str(student.profile_pic),"dob":student.dob,"classes":student.class_id.name+" "+student.class_category.name,"parent_name":student.parent_name,"phone":student.parent_phone,"parent_email":student.parent_email}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    else:
        messages.Error(request,"No Records Found")

@login_required
def manage_session(request):
    return render(request, "admin_template/manage_session_template.html")

@login_required
def add_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("add_session_save"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")
        status=request.POST.get("status")
        try:
            sessionyear=SessionYearModel(session_start_year=session_start_year,session_end_year=session_end_year,status=status)
            sessionyear.save()
            messages.success(request,"Session Successfully Added")
            return HttpResponseRedirect(reverse("manage_session"))
            
        except:
            messages.error(request," Failed To Add Session")
            return HttpResponseRedirect(reverse("manage_session"))



@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)
        

@login_required
def student_feedback_message(request):
    feedback=FeedBackStudent.objects.all()
    return render(request,"admin_template/student_feedback_template.html",{"feedbacks":feedback})

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStudent.objects.get(id=feedback_id)
        feedback.Feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


@login_required
def staff_feedback_message(request):
    feedback=FeedBackStaff.objects.all()
    return render(request,"admin_template/staff_feedback_template.html",{"feedbacks":feedback})


@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStaff.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


@login_required
def student_exit_view(request):
    exits=StudentExitReport.objects.all()
    return render(request,"admin_template/student_exit_view.html",{"exits":exits})

@login_required
def student_exit_approve(request,leave_id):
    leave=StudentExitReport.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("student_exit_view"))

@login_required
def student_exit_decline(request,leave_id):
    leave=StudentExitReport.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("student_exit_view"))


@login_required
def staff_leave_view(request):
    leave=LeaveReport.objects.all()
    return render(request,"admin_template/staff_leave_view.html",{"leaves":leave})

@login_required
def staff_leave_approve(request,leave_id):
    leave=LeaveReport.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

@login_required
def staff_leave_decline(request,leave_id):
    leave=LeaveReport.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

@login_required
def admin_view_attendance(request):
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.objects.all()
    return render(request,"admin_template/admin_view_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_attendance_date(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)

@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)


@login_required
def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"admin_template/admin_profile.html",{"user":user})


@login_required
def edit_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")

        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()
            messages.success(request,"Profile Successfully Updated")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request,"Failed To Update")
            return HttpResponseRedirect(reverse("admin_profile"))

@login_required
def admin_send_notification_staff(request):
    staff=Staff.objects.all()
    return render(request,"admin_template/staff_notification.html",{"staff":staff})

@login_required
def admin_send_notification_student(request):
    students=Students.objects.all()
    return render(request,"admin_template/student_notification.html",{"students":students})


@csrf_exempt
def send_student_notification(request):
    ids=request.POST.get("id")
    message=request.POST.get("message")
    student=Students.objects.get(admin=ids)
    token=student.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Christ High School",
            "body":message,
        },
        "to":token
    }
    headers={"content-Type":"application/json","Authorization":"key=AAAAFrwMsNg:APA91bGvdzvKmI7lbsFxtNu---cxCMGAwyJOmVYNJHMjAR9B4mTX42ZEOJC-j7s81CeiS9POoB_YKGHHyOurxcMe00ITnf93b_XdeuuKldS7glTcBWYTIi8R64sQetC6WtvYY_ZIhUJO"}
    data=request.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationStudent(student_id=student,message=message,)
    notification.save()
    print(data.text)
    return HttpResponse("True")

    
@csrf_exempt
def send_staff_notification(request):
    ids=request.POST.get("id")
    message=request.POST.get("message")
    staff=Staff.objects.get(admin=ids)
    token=staff.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"Christ High School",
            "body":message,
        },
        "to":token
    }
    headers={"content-Type":"application/json","Authorization":"key=AAAAFrwMsNg:APA91bGvdzvKmI7lbsFxtNu---cxCMGAwyJOmVYNJHMjAR9B4mTX42ZEOJC-j7s81CeiS9POoB_YKGHHyOurxcMe00ITnf93b_XdeuuKldS7glTcBWYTIi8R64sQetC6WtvYY_ZIhUJO"}
    data=request.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationStaff(staff_id=staff,message=message,)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@login_required
def calender_activities(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_controls=SiteControls.objects.all()
    activate_sess=SessionYearModel.objects.get(status=1)
    active_t=Terms.objects.get(status=1)
    return render(request,"admin_template/calender_template.html",{"all_sessions":all_sessions,"activate_sess":activate_sess,"all_terms":all_terms,"active_t":active_t,"all_controls":all_controls})

@login_required
def activate_term(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        term_id=request.POST.get("activate_term_id")

    try:
        term_obj=Terms.objects.get(id=term_id)
        term_deactivate=Terms.objects.get(status=1)
        term_obj.status=1
        term_deactivate.status=0
        term_obj.save()
        term_deactivate.save()
        messages.success(request," "+term_obj.name+"   Successfully Activated")
        return HttpResponseRedirect(reverse("calender_activities"))
    except:
        messages.error(request," Failed To Activate")
        return HttpResponseRedirect(reverse("calender_activities"))

@login_required
def activate_session(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        session_id=request.POST.get("activate_session_id")
    try:
        session_obj=SessionYearModel.objects.get(id=session_id)
        session_deactivate=SessionYearModel.objects.get(status=1)
        session_obj.status=1
        session_deactivate.status=0
        session_obj.save()
        session_deactivate.save()

        messages.success(request," "+session_obj.name+"   Successfully Activated")
        return HttpResponseRedirect(reverse("calender_activities"))
    except:
        messages.error(request," Failed To Activate")
        return HttpResponseRedirect(reverse("calender_activities"))
        
@login_required
def site_controls(request):
    if request.method!="POST":
        return HttpResponseRedirect("<h2>Method Not Allowed</h2>")
    else:
        control_id = request.POST.get('control_name')
        control_obj = SiteControls.objects.get(id=control_id)
        # try:
        if control_obj.c_code == "LP":
            ethos_value = request.POST.get('ethos_value')
            # Attempt to save the ethos_value
            try:
                control_obj.count_value = ethos_value
                control_obj.save()
                print("Lesson Plan value saved successfully.")
            except Exception as e:
                print("Error saving Lesson Plan value:", e) 
        else:
            # Toggle control status (0 to 1 or 1 to 0)
            control_obj.status = 1 - control_obj.status
            control_obj.save()

        messages.success(request," "+control_obj.name+"   Successfully Updated")
        return HttpResponseRedirect(reverse("calender_activities"))
        # except:
        #     messages.error(request," Failed To Activate")
        #     return HttpResponseRedirect(reverse("calender_activities"))


def update_status(request):
    if request.method == "POST":
        term_id = request.POST.get("term_id")  # Ensure the name matches the template's field
        result_type = request.POST.get("result_type")
        session_year_id = request.POST.get("session_year_id")
        status = request.POST.get("status")  # 0 for unapproved, 1 for approved

        try:
            # Filter the records
            records = ClassAverage.objects.filter(
                term_id=term_id,
                result_type=result_type,
                session_year_id=session_year_id
            )

            # Update the status for the filtered records
            updated_count = records.update(status=status)

            # Success message
            messages.success(request, f"Status successfully updated for {updated_count} record(s).")
        except Exception as e:
            # Handle errors
            messages.error(request, f"An error occurred: {str(e)}")

        # Redirect back to the calendar activities page
        return redirect("calender_activities")  # Update with the correct URL name for calendar activities

    # Pass terms, result types, and session years to the template (if needed for GET requests)
    terms = Terms.objects.all()
    session_years = SessionYearModel.objects.all()

    return render(request, "update_status.html", {"terms": terms, "session_years": session_years})


#ACTION LINKS
def online_class_action(request):
    return render(request,"admin_template/online_class_action.html")

@login_required
def student_action(request):
    return render(request,"admin_template/student_action.html")

def library_action(request):
    return render(request,"admin_template/library_action.html")

@login_required
def class_action(request):
    return render(request,"admin_template/class_action.html")

@login_required
def subject_action(request):
    return render(request,"admin_template/subject_action.html")

@login_required
def sessional_promotion(request):
    return render(request,"admin_template/promotion_action.html")

@login_required
def promote_class_action(request):
    classes= ClassCategories.objects.all()
    return render(request,"admin_template/promote_class.html",{"classes":classes})

@csrf_exempt
def get_students_promote(request):
    class_id=request.POST.get('class_id')
    class_cat=ClassCategories.objects.get(id=class_id)

    students=Students.objects.filter(class_id=class_cat.class_id,class_category=class_cat.id)
    list_data=[]
    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name,"reg_id":student.admin.username,"class_name":class_cat.class_id.name+class_cat.name,"class_cat":class_cat.id}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@login_required
def promote_class(request):
    class_cat=request.POST.get("promotion_class")
    class_id= ClassCategories.objects.get(id=class_cat)
    new_class_id=int(class_id.class_id.id)+1
    new_class=ClassCategories.objects.get(class_id=new_class_id,name=class_id.name)

    try:
        Students.objects.filter(class_id=class_id.class_id.id,class_category=class_id.id).update(class_id=new_class.class_id,class_category=new_class.id)
        messages.success(request," "+class_id.class_id.name+"   Successfully Promoted")
        return HttpResponseRedirect(reverse("promote_class_action"))
    except:
        messages.error(request," Failed To Promote "+class_id.class_id.name)
        return HttpResponseRedirect(reverse("promote_class_action"))

@login_required
def promote_student_action(request):
    classes= ClassCategories.objects.all()
    return render(request,"admin_template/promote_student_template.html",{"classes":classes})

@csrf_exempt
def promote_student(request):
    reg_no=request.POST.get("reg_no")
    action_type=request.POST.get("action_type")
    class_cat=request.POST.get("class_cat")
    action_type=int(action_type)
    student=CustomUser.objects.get(username=reg_no)
    get_student=Students.objects.get(admin=student)
    current_class=get_student.class_id.id

    try:
        if action_type==0:     
            new_class_id=current_class-1
            class_cate=ClassCategories.objects.get(class_id=new_class_id,name=get_student.class_category.name)
        elif action_type==1:
            new_class_id=current_class+1
            class_cate=ClassCategories.objects.get(class_id=new_class_id,name=get_student.class_category.name)
            
        new_class=Classes.objects.get(id=new_class_id)
        get_student.class_id=new_class
        get_student.class_category=class_cate
        get_student.save()

        return HttpResponse("OK")
    except:
        return HttpResponse("Error")

    
    
@login_required
def remove_student_action(request):
    classes= ClassCategories.objects.all()
    return render(request,"admin_template/remove_student_template.html",{"classes":classes})

@csrf_exempt
def remove_student(request):
    reg_no=request.POST.get("reg_no")
    action_type=request.POST.get("action_type")
    action_type=int(action_type)
    student=CustomUser.objects.get(username=reg_no)
    get_student=Students.objects.get(admin=student)

    try:
        if action_type==1:     
            new_class_id=8
        elif action_type==2:
            new_class_id=9
        elif action_type==3:
            new_class_id=3
        
        new_class=Classes.objects.get(id=new_class_id)
        get_student.class_id=new_class
        get_student.save()

        return HttpResponse("OK")
    except:
        return HttpResponse("Error")
        


@login_required
def action_result(request):
    return render(request,"admin_template/action_result.html")

@login_required
def student_results(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_class=Classes.objects.all()
    if request.method!="POST":
        return render(request,"admin_template/student_results.html",{"sessions":all_sessions,"all_terms":all_terms,"all_class":all_class})
    else:
        session_year = int(request.POST.get("sess"))
        term = int(request.POST.get("term"))
        res_type = int(request.POST.get("result_type"))
        reg_no = request.POST.get("stdID")
        std_id = CustomUser.objects.get(username=reg_no)
        class_cat=Students.objects.get(admin=std_id)
        #student ethos
        re_type = res_type-1
        ethos_records = StudentEthosRecords.objects.filter(term=term, session_year=session_year, result_type=re_type, student_id=class_cat.id)
        for record in ethos_records:
            positive_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('leadership', 'neatness', 'room_represent_compet', 'room_represent_inspect', 'selfconfidence', 'team_spirit', 'return_lost_items', 'obidience_to_staff', 'obidience_to_rules', 'volunteerism', 'reporting_unacceptable_behavior', 'prayerfullness'))])
            negative_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('loitering', 'immoral_relation_conduct', 'poor_timing', 'negative_influence', 'noise_making', 'hostel_disobidience', 'bullying_fighting', 'negative_civil', 'gossip', 'avoiding_meals', 'carelessness_personal'))])
            record.total_positive_ethos = positive_ethos_sum
            record.total_negative_ethos = negative_ethos_sum
            record.total_ethos = positive_ethos_sum - negative_ethos_sum
        try:
            if res_type==2:
                avg_id=ClassAverage.objects.get(students_id=class_cat,term=term,session_year=session_year,result_type=res_type)
                psychomotor=Psycomotor.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
                affective=AffectiveDomain.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
                endterm_result=EndTerm.objects.filter(students_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term)
                endterms=[]
                for entry in endterm_result:
                    detres=EndTerm.objects.filter(subjects_id=entry.subjects_id,session_year=avg_id.session_year,term=avg_id.term)
                    da=detres.order_by('-total')[:1]
                    for da in da:
                        da=da
                    dat=detres.order_by('total')[:1]
                    for dat in dat:
                        dat=dat
        
                    r={"subject":entry.subjects_id.subject_name,"ca1":entry.ca1,"ca2":entry.ca2,"clss":entry.class_work,"pp":entry.project_practical,"first_total":entry.first_total,"second_total":entry.second_total,"endterm_exam":entry.endterm_exam,"total":entry.total,"highest":da.total,"lowest":dat.total,"grades":entry.grades,"effort":entry.effort}
                    endterms.append(r)
                return render(request,"admin_template/endterm_result_preview.html",{"ethos_records":ethos_records,"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"endterm":endterms,"sessions":all_sessions,"all_terms":all_terms,"all_class":all_class})
            
            else:
                avg_id=ClassAverage.objects.get(students_id=class_cat,term=term,session_year=session_year,result_type=res_type)
                psychomotor=Psycomotor.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
                affective=AffectiveDomain.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
                midterm_result=MidTerm.objects.filter(students_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term)
                return render(request,"admin_template/student_results.html",{"ethos_records":ethos_records,"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"midterm":midterm_result,"sessions":all_sessions,"all_terms":all_terms,"all_class":all_class})
    
        except:
            messages.error(request,"ERROR!....Result not available")
            return HttpResponseRedirect(reverse("student_results"))

    
@csrf_exempt
def admin_results(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_subj=Subjects.objects.all()
    if request.method!="POST":
        return render(request,"admin_template/view_results.html",{"sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj})
    else:
        result_type=int(request.POST.get('result_type'))
        subjects=int(request.POST.get('subject'))
        term=int(request.POST.get('term'))
        session=int(request.POST.get('session'))
        
        subject=Subjects.objects.get(id=subjects)
        current_session=SessionYearModel.objects.get(id=session)
        current_term=Terms.objects.get(id=term)
        
        if result_type==1:
            viewtype=1
            json_data = []
            check_exist = CombineSubjects.objects.filter(subject_main=subject).exists()
            if check_exist:
                students = Students.objects.filter(class_id=subject.class_id)
                
                for student in students:
                    student_data = {
                        "Student": student.admin.first_name + " " + student.admin.last_name,
                        "student_id":student.id,
                        "subject_id":subject.id
                    }
                    combinesubjects = CombineSubjects.objects.filter(subject_main=subject)
                    for combinesubject in combinesubjects:
                        try:
                            midterm = CombineMidTerm.objects.get(
                                students_id=student,
                                session_year=current_session,
                                term=current_term,
                                
                                subjects_id=combinesubject,
                            )
                            subject_data = {
                                f"{combinesubject.name}": linebreaksbr("Res. Test: " + str(midterm.resumption_text) + "\nAssignment: " + str(midterm.assignment) + "\nClass work: " + str(midterm.class_work) + "\nExam: " + str(midterm.midterm_exam) + "\nTotal: " + str(midterm.total_score) + "\nGrades: " + midterm.grades),
                            }
                            viewtype=2
                        except CombineMidTerm.DoesNotExist:
                            subject_data = {
                                f"{combinesubject.name}": "No Record Found",
                            }
                        student_data.update(subject_data)

                    json_data.append(student_data)
  
            get_results=MidTerm.objects.filter(subjects_id=subject,session_year=current_session,term=current_term)
            context={"subject":subject,"results":get_results,"json_data":json_data,"viewtype":viewtype,"restype":result_type,"sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj,"delterm":term,"delses":session}
            return render(request,"admin_template/view_results.html",context)

        elif result_type==2:
            check_exist = CombineSubjects.objects.filter(subject_main=subject).exists()
            viewtype=1
            json_data = []
            if check_exist:
                students = Students.objects.filter(class_id=subject.class_id)
                
                for student in students:
                    student_data = {
                        "Student": student.admin.first_name + " " + student.admin.last_name,
                        "student_id":student.id,
                        "subject_id":subject.id
                    }

                    combinesubjects = CombineSubjects.objects.filter(subject_main=subject)
                    for combinesubject in combinesubjects:
                        try:
                            enterm = CombineEndTerm.objects.get(
                                students_id=student,
                                session_year=current_session,
                                term=current_term,
                                subjects_id=combinesubject,
                            )
                            subject_data = {
                                f"{combinesubject.name}": linebreaksbr("First Half: " + str(enterm.first_total) + "\nAssignment: " + str(enterm.ca1) + "\nClass work: " + str(enterm.class_work) + "\nTest: " + str(enterm.ca2) + "\nProject/Practical: " + str(enterm.project_practical) + "\nExam: " + str(enterm.endterm_exam) + "\nTotal: " + str(enterm.total) + "\nGrades: " + enterm.grades),
                            }
                            viewtype=2
                        except CombineEndTerm.DoesNotExist:
                            subject_data = {
                                f"{combinesubject.name}": "No Record Found",
                            }
                        student_data.update(subject_data)

                    json_data.append(student_data)
                        
            get_results=EndTerm.objects.filter(subjects_id=subject,term=term,session_year=session)
            
            context={"subject":subject,"results":get_results,"json_data":json_data,"viewtype":viewtype,"restype":result_type,"sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj,"delterm":term,"delses":session}           
            return render(request,"admin_template/view_results.html",context)


def combmid_save(request):
    student_id=request.POST.get("student_id")
    subject_id=request.POST.get("subject_id")
    subjects=Subjects.objects.get(id=subject_id)
    combine_subjects=CombineSubjects.objects.filter(subject_main=subjects)
    
    session_year=SessionYearModel.objects.get(status=1)
    term=Terms.objects.get(status=1)
    
    # Retrieve the subject IDs that are combined under the CombineSubjects entry
    combined_subject_ids = [combine_subject.id for combine_subject in combine_subjects]
    
    # Query CombineMidTerm for all entries matching the student ID, combined subject IDs, session year, and term
    combine_midterm_entries = CombineMidTerm.objects.filter(students_id=student_id, subjects_id__in=combined_subject_ids, session_year=session_year, term=term)
    
    # Calculate the average of the scores for the corresponding entries
    num_entries = len(combine_midterm_entries)
    if num_entries > 0:
        total_resumption_text = sum(combine_midterm_entry.resumption_text for combine_midterm_entry in combine_midterm_entries)
        total_class_work = sum(combine_midterm_entry.class_work for combine_midterm_entry in combine_midterm_entries)
        total_assignment = sum(combine_midterm_entry.assignment for combine_midterm_entry in combine_midterm_entries)
        total_midterm_exam = sum(combine_midterm_entry.midterm_exam for combine_midterm_entry in combine_midterm_entries)
        total_total_score = sum(combine_midterm_entry.total_score for combine_midterm_entry in combine_midterm_entries)

        average_resumption_text = round(total_resumption_text / num_entries, 1)
        average_class_work = round(total_class_work / num_entries, 1)
        average_assignment = round(total_assignment / num_entries, 1)
        average_midterm_exam = round(total_midterm_exam / num_entries, 1)
        average_total_score = round(total_total_score / num_entries, 1)
        
    else:
        # Handle the case when there are no CombineMidTerm entries for the given criteria
        average_resumption_text = 0.0
        average_class_work = 0.0
        average_assignment = 0.0
        average_midterm_exam = 0.0
        average_total_score = 0.0
        
    if average_total_score >=25:
        grade='A'
        remark='Excellent'
    elif average_total_score >=20:
        grade='B'
        remark='Very Good'
    elif average_total_score >=15:
        grade='C'
        remark='Good'
    elif average_total_score >=10:
        grade='P'
        remark='Pass'
    else:
        grade='F'
        remark='Fail'

    # Check if the MidTerm entry exists for the given criteria
    midterm_entry_exists = MidTerm.objects.filter(students_id=student_id, subjects_id=subjects, session_year=session_year, term=term).exists()

    if midterm_entry_exists:
        # Retrieve the existing MidTerm entry
        midterm_entry = MidTerm.objects.get(students_id=student_id, subjects_id=subjects, session_year=session_year, term=term)
        
        # Update the fields of the MidTerm entry with the calculated averages
        midterm_entry.resumption_text = average_resumption_text
        midterm_entry.class_work = average_class_work
        midterm_entry.assignment = average_assignment
        midterm_entry.midterm_exam = average_midterm_exam
        midterm_entry.total_score = average_total_score
        midterm_entry.grades = grade
        midterm_entry.remark = remark

        # Save the updated MidTerm entry
        midterm_entry.save()
        messages.success(request,"Result for " + midterm_entry.students_id.admin.first_name + " Approved Successfully")
        return HttpResponseRedirect(reverse("admin_results"))
    else:
        student_id=Students.objects.get(id=student_id)
        # Create a new MidTerm entry
        midterm_entry = MidTerm.objects.create(students_id=student_id, 
                                               subjects_id=subjects, 
                                               session_year=session_year, 
                                               term=term, 
                                               resumption_text = average_resumption_text,
                                               class_work = average_class_work, 
                                               assignment = average_assignment,
                                               midterm_exam = average_midterm_exam,
                                               total_score = average_total_score,
                                               grades = grade,
                                               remark = remark)
        messages.success(request,"Result for " + midterm_entry.students_id.admin.first_name + " Approved Successfully")
        return HttpResponseRedirect(reverse("admin_results"))

    
        
def combend_save(request):
    student_id=request.POST.get("student_id")
    subject_id=request.POST.get("subject_id")
    subjects=Subjects.objects.get(id=subject_id)
    combine_subjects=CombineSubjects.objects.filter(subject_main=subjects)
    
    session_year=SessionYearModel.objects.get(status=1)
    term=Terms.objects.get(status=1)
    
    # Retrieve the subject IDs that are combined under the CombineSubjects entry
    combined_subject_ids = [combine_subject.id for combine_subject in combine_subjects]
    
    # Query CombineMidTerm for all entries matching the student ID, combined subject IDs, session year, and term
    combine_enterm_entries = CombineEndTerm.objects.filter(students_id=student_id, subjects_id__in=combined_subject_ids, session_year=session_year, term=term)
    
    # Calculate the average of the scores for the corresponding entries
    num_entries = len(combine_enterm_entries)
    if num_entries > 0:
        total_ca1 = sum(combine_enterm_entry.ca1 for combine_enterm_entry in combine_enterm_entries)
        total_ca2 = sum(combine_enterm_entry.ca2 for combine_enterm_entry in combine_enterm_entries)
        total_project_practical = sum(combine_enterm_entry.project_practical for combine_enterm_entry in combine_enterm_entries)
        total_class_work = sum(combine_enterm_entry.class_work for combine_enterm_entry in combine_enterm_entries)
        total_sec_total = sum(combine_enterm_entry.sec_total for combine_enterm_entry in combine_enterm_entries)
        total_first_total = sum(combine_enterm_entry.first_total for combine_enterm_entry in combine_enterm_entries)
        total_second_total = sum(combine_enterm_entry.second_total for combine_enterm_entry in combine_enterm_entries)
        total_endterm_exam = sum(combine_enterm_entry.endterm_exam for combine_enterm_entry in combine_enterm_entries)
        total_total = sum(combine_enterm_entry.total for combine_enterm_entry in combine_enterm_entries)
        
        
        average_ca1 = round(total_ca1 / num_entries, 1)
        average_ca2 = round(total_ca2 / num_entries, 1)
        average_project_practical = round(total_project_practical / num_entries, 1)
        average_class_work = round(total_class_work / num_entries, 1)
        average_sec_total = round(total_sec_total / num_entries, 1)
        average_first_total = round(total_first_total / num_entries, 1)
        average_second_total = round(total_second_total / num_entries, 1)
        average_endterm_exam = round(total_endterm_exam / num_entries, 1)
        average_total = round(total_total / num_entries, 1)
        
    else:
        # Handle the case when there are no CombineEndTerm entries for the given criteria
        average_ca1 = 0.0
        average_ca2 = 0.0
        average_project_practical = 0.0
        average_class_work = 0.0
        average_sec_total = 0.0
        average_first_total = 0.0
        average_second_total = 0.0
        average_endterm_exam = 0.0
        average_total = 0.0
        
    if average_total >=80:
        grade='A'
        remark='Excellent'
    elif average_total >=70:
        grade='B'
        remark='Very Good'
    elif average_total >=60:
        grade='C'
        remark='Good'
    elif average_total >=50:
        grade='P'
        remark='Pass'
    else:
        grade='F'
        remark='Fail'

    # Check if the EndTerm entry exists for the given criteria
    endterm_entry_exists = EndTerm.objects.filter(students_id=student_id, subjects_id=subjects, session_year=session_year, term=term).exists()

    if endterm_entry_exists:
        # Retrieve the existing EndTerm entry
        endterm_entry = EndTerm.objects.get(students_id=student_id, subjects_id=subjects, session_year=session_year, term=term)
        
        # Update the fields of the MidTerm entry with the calculated averages
        endterm_entry.ca1 = average_ca1
        endterm_entry.ca2 = average_ca2
        endterm_entry.class_work = average_class_work
        endterm_entry.first_total = average_first_total
        endterm_entry.sec_total = average_sec_total
        endterm_entry.second_total = average_second_total
        endterm_entry.project_practical = average_project_practical
        endterm_entry.endterm_exam = average_endterm_exam
        endterm_entry.total = average_total
        endterm_entry.grades = grade
        endterm_entry.effort = remark

        # Save the updated EndTerm entry
        endterm_entry.save()
        messages.success(request,"Result Approved Successfully" + " " + endterm_entry.students_id.admin.first_name)
        return HttpResponseRedirect(reverse("admin_results"))
    else:
        student_id=Students.objects.get(id=student_id)
        # Create a new EndTerm entry
        endterm_entry = EndTerm.objects.create(students_id=student_id, 
                                                subjects_id=subjects, 
                                                session_year=session_year, 
                                                term=term,
                                                ca1 = average_ca1,
                                                ca2 = average_ca2,
                                                class_work = average_class_work,
                                                first_total = average_first_total,
                                                sec_total = average_sec_total,
                                                second_total = average_second_total,
                                                project_practical = average_project_practical,
                                                endterm_exam = average_endterm_exam,
                                                total = average_total,
                                                grades = grade,
                                                effort = remark)
        messages.success(request,"Result Approved Successfully" + " " + endterm_entry.students_id.admin.first_name)
        return HttpResponseRedirect(reverse("admin_results"))




def midterm_grade(average_score, class_id):
    if class_id >= 4:
        if average_score >= 13:
            return 'A'
        elif average_score >= 10:
            return 'B'
        elif average_score >= 8:
            return 'C'
        elif average_score >= 6:
            return 'P'
        else:
            return 'F'
        
    else:
        if average_score >= 25:
            return 'A'
        elif average_score >= 20:
            return 'B'
        elif average_score >= 15:
            return 'C'
        elif average_score >= 10:
            return 'P'
        else:
            return 'F'

def endterm_grade(average_score, class_id):
    if average_score >=80:
        return 'A'
    elif average_score >=70:
        return 'B'
    elif average_score >=60:
        return 'C'
    elif average_score >=50:
        return 'P'
    else:
        return 'F'
    
def ordinal_suffix(number):
    if 10 <= number % 100 < 20:
        return 'th'
    else:
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        return suffixes.get(number % 10, 'th') 
 
def broadsheet_analysis(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_cat=ClassCategories.objects.all().order_by('class_id__name')
    if request.method!="POST":
        return render(request,"admin_template/broadsheet_template.html",{"all_sessions":all_sessions,"all_terms":all_terms,"all_cat":all_cat})
    else:
        # Post data
        result_type=int(request.POST.get('result_type'))
        clas_cat=int(request.POST.get('classid'))
        term=int(request.POST.get('term'))
        sess_year=int(request.POST.get('sess_year'))
        
        # Retrieve students
        class_cat = ClassCategories.objects.get(id=clas_cat)
        re_type = result_type-1
        #student ethos
        ethos_records = StudentEthosRecords.objects.filter(term=term, session_year=sess_year, result_type=re_type, student_id__class_category=clas_cat)
        for record in ethos_records:
            positive_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('leadership', 'neatness', 'room_represent_compet', 'room_represent_inspect', 'selfconfidence', 'team_spirit', 'return_lost_items', 'obidience_to_staff', 'obidience_to_rules', 'volunteerism', 'reporting_unacceptable_behavior', 'prayerfullness'))])
            negative_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('loitering', 'immoral_relation_conduct', 'poor_timing', 'negative_influence', 'noise_making', 'hostel_disobidience', 'bullying_fighting', 'negative_civil', 'gossip', 'avoiding_meals', 'carelessness_personal'))])
            record.total_positive_ethos = positive_ethos_sum
            record.total_negative_ethos = negative_ethos_sum
            record.total_ethos = positive_ethos_sum - negative_ethos_sum
            
        #staff attestation
        attestations = EntryAttestation.objects.filter(term=term, session_year=sess_year, result_type=re_type, subjects__class_id=class_cat.class_id)
        
        
        
        students = Students.objects.filter(class_category=class_cat, class_id=class_cat.class_id)
        
        c_sess=SessionYearModel.objects.get(status=1)

        r_class = class_cat.class_id.id+(sess_year - c_sess.id)
        
        subjects = Subjects.objects.filter(class_id=r_class)
        subject_names = [subject.outline for subject in subjects]  # Extract subject names

        subject_grade_counts = {subject_name: {'A': 0, 'B': 0, 'C': 0, 'P': 0, 'F': 0} for subject_name in subject_names}
        subject_termly = {subject_name: {'curterm': 0, 'pevterm': 0} for subject_name in subject_names}
        termly_compare= {student:{'currentterm':0,'prevterm':0} for student in students}
        if result_type==1:
            # Prepare JSON data
            json_data = []
            for student in students:
                # Retrieve midterms for the student
                midterms = MidTerm.objects.filter(students_id=student,session_year=sess_year,term=term)
                
                # Calculate the average of total scores
                total_scores = [midterm.total_score for midterm in midterms]
                average_score = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00

                # Determine grade based on average score
                grade = midterm_grade(average_score, student.class_id.id)
                
                # Format JSON data for each student
                student_data = {
                    ".:.:.": None,
                    "Student": student.admin.first_name+" "+student.admin.last_name,
                    "Avg:.": average_score,
                    "Grade": grade,
                }

                for subject in subjects:
                    try:
                        midterm = midterms.get(subjects_id=subject.id)
                        subject_data = {
                            f"{midterm.subjects_id.outline}": midterm.total_score,
                        }  
                        # Increment the grade count for the subject
                        grade = midterm.grades  # Assuming all scores for a subject have the same grade
                        subject_grade_counts[midterm.subjects_id.outline][grade] += 1
                        
                        # subject total score comparism
                        if term == 1:
                            subject_termly[midterm.subjects_id.outline]['curterm'] += round(midterm.total_score,2)
                        else:
                            subject_termly[midterm.subjects_id.outline]['curterm'] += round(midterm.total_score,2)
                            pterm = term-1
                            try:
                                mids = MidTerm.objects.filter(students_id=student,session_year=sess_year,term=pterm)
                                mid = mids.get(subjects_id=subject.id)
                                subject_termly[mid.subjects_id.outline]['pevterm'] += round(mid.total_score,2)
                            except:
                                None
                    except:
                        subject_data = {
                            f"{subject.outline}": " -"
                        }
                    student_data.update(subject_data)

                json_data.append(student_data)
                
                if term == 1:
                    terms = 3
                    sess_years=sess_year - 1
                    # Retrieve midterms for the student
                    midterms = MidTerm.objects.filter(students_id=student,session_year=sess_years,term=terms)
                    
                    # Calculate the average of total scores
                    total_scores = [midterm.total_score for midterm in midterms]
                    prev_average = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00
                    
                    termly_compare[student]['currentterm']=average_score
                    termly_compare[student]['prevterm']=prev_average
                else:
                    terms = term - 1
                    # Retrieve midterms for the student
                    midterms = MidTerm.objects.filter(students_id=student,session_year=sess_year,term=terms)
                    
                    # Calculate the average of total scores
                    total_scores = [midterm.total_score for midterm in midterms]
                    prev_average = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00
                    
                    termly_compare[student]['currentterm']=average_score
                    termly_compare[student]['prevterm']=prev_average
      
            # Sort student_data by average_score in ascending order
            json_data.sort(key=lambda x: x['Avg:.'], reverse=True)
            
            # Add ordinal position for each student in the JSON data
            for index, student in enumerate(json_data):
                position = index + 1
                suffix = ordinal_suffix(position)
                student['.:.:.'] = f"{position}{suffix}"
                
                
            theses = all_sessions.get(id=sess_year)
            theterm = all_terms.get(id=term)
            theclass = Classes.objects.get(id=r_class)
            
            # Count grade occurrences
            grade_counts = {'A': 0, 'B': 0, 'C': 0, 'P': 0, 'F': 0}
            for student in json_data:
                grade = student['Grade']
                grade_counts[grade] += 1
                
                
            #ethos records
            
            context = {"json_data": json_data,
                    "all_sessions":all_sessions,
                    "all_terms":all_terms,
                    "all_cat":all_cat,
                    "theses":theses,
                    "theterm":theterm,
                    "theclass":theclass,
                    "subject_grade_counts":subject_grade_counts,
                    'grade_counts': grade_counts,
                    "termly_compare":termly_compare,
                    "subject_termly":subject_termly,
                    "thehalf":"First Half",
                    "ethos_records":ethos_records,
                    "attestations":attestations,
                    "re_type":re_type}
            return render(request, 'admin_template/broadsheet_template.html', context) 
        
        elif result_type==2:
            # Prepare JSON data
            json_data = []
            cumul_records = []
            for student in students:
                # Retrieve midterms for the student
                all_endterms = EndTerm.objects.filter(students_id=student,session_year=sess_year)
                endterms = all_endterms.filter(term=term)
                
                # Calculate the average of total scores
                total_scores = [endterm.total for endterm in endterms]
                average_score = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00

                # Determine grade based on average score
                grade = endterm_grade(average_score, student.class_id.id)
                
                # Format JSON data for each student
                student_data = {
                    ".:.:.": None,
                    "Student": student.admin.first_name+" "+student.admin.last_name,
                    "Avg:.": average_score,
                    "Grade": grade,
                }
                
                                #Cummulative Average starts
                
                # Calculate the average of total scores
                total_scores = [endterm.total for endterm in all_endterms]
                Cummaverage_score = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00

                # Determine grade based on average score
                grade = endterm_grade(Cummaverage_score, student.class_id.id)

                
                def determine_grade(Cummaverage_score):
                    if Cummaverage_score >= 80:
                        return 'A'
                    elif Cummaverage_score >= 70:
                        return 'B'
                    elif Cummaverage_score >= 60:
                        return 'C'
                    elif Cummaverage_score >= 50:
                        return 'P'
                    else:
                        return 'F'


                cumul_data = {
                    "Student": student.admin.first_name + " " + student.admin.last_name,
                    "Cum Avg": Cummaverage_score,
                    "Cum Grade": grade,
                }

                 # Handling different terms
                if term == 3:  # For term 3, consider cumulative average of all terms

                    for subject in subjects:
                        try:
                            # Retrieve end terms for each subject for terms 1, 2, and 3
                            endterm1 = all_endterms.get(subjects_id=subject.id, term=1)
                            endterm2 = all_endterms.get(subjects_id=subject.id, term=2)
                            endterm3 = all_endterms.get(subjects_id=subject.id, term=3)

                            # Calculate average of three terms for each subject
                            average_score = (endterm1.total + endterm2.total + endterm3.total) / 3
                            subject_data = {
                                f"{endterm1.subjects_id.outline}": round(average_score, 2),
                            }
                        except EndTerm.DoesNotExist:
                            subject_data = {
                                f"{subject.outline}": " -"
                            }
                        cumul_data.update(subject_data)

                elif term == 2:  # For term 2, calculate average of end of term totals for terms 1 and 2
                    # Calculate the average of total scores
                    filtered_endterms = all_endterms.filter(term__in=[1, 2])
                    total_scores = [endterm.total for endterm in filtered_endterms]
                    Cummaverage_score = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00

                    
                    cumul_data["Cum Avg"] = Cummaverage_score
                    cumul_data["Cum Grade"] = determine_grade(Cummaverage_score)

                    for subject in subjects:
                        try:
                            # Retrieve end terms for each subject for terms 1 and 2
                            endterm1 = all_endterms.get(subjects_id=subject.id, term=1)
                            endterm2 = all_endterms.get(subjects_id=subject.id, term=2)

                            # Calculate average of two terms for each subject
                            average_score = (endterm1.total + endterm2.total) / 2
                            subject_data = {
                                f"{endterm1.subjects_id.outline}": round(average_score, 2),
                            }
                        except EndTerm.DoesNotExist:
                            subject_data = {
                                f"{subject.outline}": " -"
                            }
                        cumul_data.update(subject_data)

                elif term == 1:  # For term 1, calculate the average of end of term totals for term 1

                    None

                cumul_records.append(cumul_data)
                # Cummulative average stops
                

                for subject in subjects:
                    try:
                        endterm = endterms.get(subjects_id=subject.id)
                        subject_data = {
                            f"{endterm.subjects_id.outline}": endterm.total,
                        }  
                        # Increment the grade count for the subject
                        grade = endterm.grades  # Assuming all scores for a subject have the same grade
                        subject_grade_counts[endterm.subjects_id.outline][grade] += 1
                        
                        # subject total score comparism
                        if term == 1:
                            subject_termly[endterm.subjects_id.outline]['curterm'] += round(endterm.total,2)
                        else:
                            subject_termly[endterm.subjects_id.outline]['curterm'] += round(endterm.total,2)
                            pterm = term-1
                            try:
                                ends = EndTerm.objects.filter(students_id=student,session_year=sess_year,term=pterm)
                                end = ends.get(subjects_id=subject.id)
                                subject_termly[end.subjects_id.outline]['pevterm'] += round(end.total,2)
                            except:
                                None
                    except:
                        subject_data = {
                            f"{subject.outline}": " -"
                        }
                    student_data.update(subject_data)

                json_data.append(student_data)
                


            
                if term == 1:
                    terms = 3
                    sess_years=sess_year - 1
                    # Retrieve endterms for the student
                    endterms = EndTerm.objects.filter(students_id=student,session_year=sess_years,term=terms)
                    
                    # Calculate the average of total scores
                    total_scores = [endterm.total for endterm in endterms]
                    prev_average = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00
                    
                    termly_compare[student]['currentterm']=average_score
                    termly_compare[student]['prevterm']=prev_average
                else:
                    terms = term - 1
                    # Retrieve midterms for the student
                    endterms = EndTerm.objects.filter(students_id=student,session_year=sess_year,term=terms)
                    
                    # Calculate the average of total scores
                    total_scores = [endterm.total for endterm in endterms]
                    prev_average = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00
                    
                    termly_compare[student]['currentterm']=average_score
                    termly_compare[student]['prevterm']=prev_average
            
            # Sort student_data by average_score in ascending order
            json_data.sort(key=lambda x: x['Avg:.'], reverse=True)
            
            cumul_records.sort(key=lambda x: x['Cum Avg'], reverse=True)
            
            # Add ordinal position for each student in the JSON data
            for index, student in enumerate(json_data):
                position = index + 1
                suffix = ordinal_suffix(position)
                student['.:.:.'] = f"{position}{suffix}"
                
                
            # Count grade occurrences
            grade_counts = {'A': 0, 'B': 0, 'C': 0, 'P': 0, 'F': 0}
            for student in json_data:
                grade = student['Grade']
                grade_counts[grade] += 1
            theses = all_sessions.get(id=sess_year)
            theterm = all_terms.get(id=term)
            theclass = Classes.objects.get(id=r_class)
            
            
            context = {"json_data": json_data,
                    "cumul_records": cumul_records,
                    "all_sessions":all_sessions,
                    "all_terms":all_terms,
                    "all_cat":all_cat,
                    "theses":theses,
                    "theterm":theterm,
                    "theclass":theclass,
                    "subject_grade_counts":subject_grade_counts,
                    'grade_counts': grade_counts,
                    "termly_compare":termly_compare,
                    "subject_termly":subject_termly,
                    "thehalf":"End of Term",
                    "ethos_records":ethos_records,
                    "attestations":attestations,
                    "re_type":re_type}
            return render(request, 'admin_template/broadsheet_template.html', context) 

@login_required
def old_results(request):
    if request.method!="POST":
        sessions=SessionYearModel.objects.all()
        old_results=OldResults.objects.all()
        classess=Classes.objects.all()
        return render(request,"admin_template/old_results.html",{"sessions":sessions,"old_results":old_results,"classess":classess})
    else:
        sess = int(request.POST.get("session_id"))
        term = int(request.POST.get("term"))
        res_type = request.POST.get("res_type")
        reg = request.POST.get("reg")
        classid = int(request.POST.get("classid"))
        res_file = request.FILES['res_file']
        fs=FileSystemStorage(location="/home/chrijpdc/public_html/media/old_results/")
        filename=fs.save(res_file.name,res_file)
        res_file_url=fs.url("old_results/"+filename)

        admin_id=CustomUser.objects.get(username=reg)
        student_id=Students.objects.get(admin_id=admin_id)
        term=Terms.objects.get(id=term)
        sess=SessionYearModel.objects.get(id=sess)
        classid=Classes.objects.get(id=classid)
        try:
            check_exist=OldResults.objects.filter(students=student_id,term=term,session_year=sess,result_type=res_type,classes=classid)
            if check_exist:
                messages.error(request," Record already exist, please review details and try again.")
                return HttpResponseRedirect(reverse("old_results"))
            else:
                OldResults.objects.create(students=student_id,term=term,session_year=sess,result_type=res_type,result_file=res_file_url,classes=classid)
                messages.success(request,"Record added Succcessfully")
                return HttpResponseRedirect(reverse("old_results"))
        except:
            messages.error(request," Failed to add, please review details anf try again.")
            return HttpResponseRedirect(reverse("old_results"))



def manage_hostels(request):
    if request.method!="POST":
        hostels=Hostel.objects.all()
        return render(request,"admin_template/hostels.html",{"hostels":hostels})
    else:
        type = request.POST.get('cate')
        ids = request.POST.get('ID')
        name = request.POST.get("name")
        capacity = request.POST.get("capacity")
        rooms = request.POST.get("rooms")
        p1 = request.POST.get("p1")
        p2 = request.POST.get("p2")
        prefect = request.POST.get("prefect")

        try:
            check_exist=Hostel.objects.filter(id=ids)
            hp1=CustomUser.objects.get(username=p1)
            hpre=CustomUser.objects.get(username=prefect)
            hp=Students.objects.get(admin=hpre)
            if check_exist:
                check_exist=Hostel.objects.get(id=ids)
                check_exist.sex=type
                check_exist.name=name
                check_exist.capacity=capacity
                check_exist.room_count=rooms
                check_exist.hparent1=hp1
                check_exist.hparent2=p2
                check_exist.hprefect=hp
                check_exist.save()
                messages.success(request,"Hostel Details Successfully Updated")
                return HttpResponseRedirect(reverse("manage_hostels"))
            else:
                Hostel.objects.create(name=name,room_count=rooms,Sex=type,capacity=capacity,hparent1=hp1,hparent2=p2,hprefect=hp)            
                messages.success(request,"Hostel Successfully Added")
                return HttpResponseRedirect(reverse("manage_hostels"))
        except:
            messages.error(request,"Failed To Update/Add Hostel")
            return HttpResponseRedirect(reverse("manage_hostels"))

def manage_rooms(request):
    if request.method!="POST":
        hostels=Hostel.objects.all()
        rooms=Rooms.objects.all()
        return render(request,"admin_template/rooms.html",{"rooms":rooms,"hostels":hostels})
    else:
        hostel = int(request.POST.get('hostel'))
        roomid = request.POST.get("roomid")
        roomname = request.POST.get("name")
        roomcap = request.POST.get("capacity")
        roomhead = request.POST.get("roomhead")

        try:
            check_exist = Rooms.objects.filter(id=roomid)
            if check_exist:
                check_exist = Rooms.objects.get(id=roomid)
                check_exist.name=roomname
                check_exist.capacity=roomcap
                check_exist.hostels=Hostel.objects.get(id=hostel)
                headid=CustomUser.objects.get(username=roomhead)
                check_exist.roomhead=Students.objects.get(admin=headid)
                check_exist.save()
                messages.success(request,"Room Details Successfully Updated")
                return HttpResponseRedirect(reverse("manage_rooms"))
            else:
                hostel=Hostel.objects.get(id=hostel)
                headid=CustomUser.objects.get(username=roomhead)
                rhead=Students.objects.get(admin=headid)
                Rooms.objects.create(name=roomname,roomhead=rhead,hostels=hostel,capacity=roomcap)
                messages.success(request,"Room Successfully Added")
                return HttpResponseRedirect(reverse("manage_rooms"))


        except:
            messages.error(request,"Failed To Update/Add Room")
            return HttpResponseRedirect(reverse("manage_rooms"))

def hostel_analytics(request):
    # Retrieve data for cards
    male_hostel = Hostel.objects.filter(Sex='Male').first()
    female_hostel = Hostel.objects.filter(Sex='Female').first()

    # Retrieve data for accordion sections
    rooms_data = Rooms.objects.all()
    # Order reports_data based on the parsed rdate
    reports_data = Logbook.objects.all()
    reports_data = sorted(reports_data, key=lambda x: datetime.strptime(x.rdate, '%Y-%m-%d'))

    context = {
        'male_hostel': male_hostel,
        'female_hostel': female_hostel,
        'rooms_data': rooms_data,
        'reports_data': reports_data,
    }

    return render(request, 'admin_template/hostel_dashboard.html', context)
        
def old_cumm(request):
    if request.method!="POST":
        sessions=SessionYearModel.objects.all()
        old_results=OldCummulative.objects.all()
        return render(request,"admin_template/old_cummu.html",{"sessions":sessions,"old_results":old_results})
    else:
        sess = int(request.POST.get("session_id"))
        reg = request.POST.get("reg")
        res_file = request.FILES['cumm_file']
        fs=FileSystemStorage(location="/home/chrijpdc/public_html/media/old_cumm/")
        filename=fs.save(res_file.name,res_file)
        res_file_url=fs.url("old_cumm/"+filename)

        student_id=Students.objects.get(admin_id__username=reg)
        sess=SessionYearModel.objects.get(id=sess)
        try:
            OldCummulative.objects.create(students=student_id,session_year=sess,cummulative_file=res_file_url)
            messages.success(request,"Record added Succcessfully")
            return HttpResponseRedirect(reverse("old_cumm"))
        except:
            messages.error(request," Failed to add, please review details and try again.")
            return HttpResponseRedirect(reverse("old_cumm"))
            
            
            
def cbtentry(request):
    student = Students.objects.filter(class_id = 6)
    subjects = Subjects.objects.filter(class_id = 6)
    if request.method=="POST":
        try:
            with transaction.atomic():
                # Get form data
                student_id = request.POST.get('student')
                cbtdate = request.POST.get('cbtdate')
                subj1 = request.POST.get('subj1')
                score1 = int(request.POST.get('score1'))
                subj2 = request.POST.get('subj2')
                score2 = int(request.POST.get('score2'))
                subj3 = request.POST.get('subj3')
                score3 = int(request.POST.get('score3'))
                subj4 = request.POST.get('subj4')
                score4 = int(request.POST.get('score4'))

                total_score = math.ceil(sum([score1, score2, score3, score4]) * 2.2222222222)

                # Save data to the database
                cbt_result = CBTresult(
                    student_id=student.get(id=student_id),
                    subject1=subjects.get(id=subj1),
                    subject2=subjects.get(id=subj2),
                    subject3=subjects.get(id=subj3),
                    subject4=subjects.get(id=subj4),
                    sub1=score1,
                    sub2=score2,
                    sub3=score3,
                    sub4=score4,
                    Total=total_score,  # Update this based on your logic
                    entrydate = cbtdate
                )
                cbt_result.save()

                messages.success(request, 'CBT result added successfully.')
        except Exception as e:
            messages.error(request, f'Error: {e}')

        return redirect('cbtentry') 
    else:
        
        return render(request, "admin_template/cbtentry.html",{"subjects":subjects,"student":student})


def domainviews(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_classes=Classes.objects.all()
    if request.method!="POST":
        return render(request,"admin_template/admin_domains.html",{"sessions":all_sessions,"all_terms":all_terms,"all_classes":all_classes})
    else:
        result_type=int(request.POST.get('result_type'))
        c_id=int(request.POST.get('c_id'))
        term=int(request.POST.get('term'))
        session=int(request.POST.get('session'))
        
        student_obj = Students.objects.filter(class_id=c_id).first()
        

        pdomain = Psycomotor.objects.filter(student_id__class_id=student_obj.class_id, term=term, session_year=session, result_type=result_type)
        
        adomain = AffectiveDomain.objects.filter(student_id__class_id=student_obj.class_id, term=term, session_year=session, result_type=result_type)

            
        context={"pdomain":pdomain,"adomain":adomain,"sessions":all_sessions,"all_terms":all_terms,"all_classes":all_classes}           
        return render(request,"admin_template/admin_domains.html",context)



def add_material(request):
    if request.method == "POST":
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Material added successfully"}, status=201)
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = StudyMaterialForm()

    subjects = Subjects.objects.all()
    return render(request, 'admin_template/add_material.html', {'form': form, 'subjects': subjects})

def materials_list(request):
    materials = StudyMaterial.objects.all().order_by('-id')
    return render(request, 'admin_template/materials_list.html', {'materials': materials})

def update_material(request, material_id):
    if request.method == "POST":
        material = get_object_or_404(StudyMaterial, id=material_id)
        title = request.POST.get("title")
        status = request.POST.get("status") == "true"  # Convert to boolean
        
        if title:
            material.title = title
        material.status = status
        material.save()
        
        return JsonResponse({"message": "Material updated successfully"}, status=200)

def delete_material(request, material_id):
    if request.method == "POST":
        material = get_object_or_404(StudyMaterial, id=material_id)
        material.delete()
        return JsonResponse({"message": "Material deleted successfully"}, status=200)


def exam_files_view(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    classes = Classes.objects.all()
    exam_files = ExamFile.objects.all()
    
    context = {
        'subjects': subjects,
        'session_years': session_years,
        'classes': classes,
        'exam_files': exam_files,
    }
    return render(request, 'admin_template/exam_files.html', context)

@csrf_exempt
def add_exam_file(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject')
        session_year_id = request.POST.get('session_year')
        class_id = request.POST.get('class_name')
        exam_pdf = request.FILES.get('exam_pdf')

        subject = Subjects.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)
        class_name = Classes.objects.get(id=class_id)

        exam_file = ExamFile.objects.create(
            subject=subject,
            session_year=session_year,
            class_name=class_name,
            exam_pdf=exam_pdf
        )
        return JsonResponse({'message': 'Exam file added successfully!', 'id': exam_file.id})

@csrf_exempt
def update_exam_status(request, file_id):
    if request.method == "POST":
        exam_file = get_object_or_404(ExamFile, id=file_id)
        data = json.loads(request.body)
        exam_file.status = data.get("status")
        exam_file.save()
        return JsonResponse({'message': 'Status updated successfully'})

@csrf_exempt
def delete_exam_file(request, file_id):
    if request.method == "POST":
        exam_file = get_object_or_404(ExamFile, id=file_id)
        exam_file.delete()
        return JsonResponse({'message': 'Exam file deleted successfully'})

    
# --------------CBT--------------------

# View to display admin dashboard
def admin_cbt(request):
    quizzes = Quiz.objects.all()
    schedules = QuizSchedule.objects.all()
    return render(request, 'admin_template/quizes/admin_cbt.html', {
        'quizzes': quizzes,
        'schedules': schedules,
    })

# View to display details of a specific quiz
def admin_view_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    objective_questions = ObjectiveQuestion.objects.filter(quiz=quiz)
    theory_questions = TheoryQuestion.objects.filter(quiz=quiz)
    return render(request, 'admin_template/quizes/admin_view_quiz.html', {
        'quiz': quiz,
        'objective_questions': objective_questions,
        'theory_questions': theory_questions,
    })

# View to delete a quiz
def admin_delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    messages.success(request, "Quiz deleted successfully.")
    return redirect('admin_cbt')

# View to delete a schedule
def admin_delete_schedule(request, schedule_id):
    schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    schedule.delete()
    messages.success(request, "Schedule deleted successfully.")
    return redirect('admin_cbt')

# View to delete an objective question
def admin_delete_objective_question(request, question_id):
    question = get_object_or_404(ObjectiveQuestion, id=question_id)
    question.delete()
    messages.success(request, "Objective question deleted successfully.")
    return redirect('admin_view_quiz', quiz_id=question.quiz.id)

# View to delete a theory question
def admin_delete_theory_question(request, question_id):
    question = get_object_or_404(TheoryQuestion, id=question_id)
    question.delete()
    messages.success(request, "Theory question deleted successfully.")
    return redirect('admin_view_quiz', quiz_id=question.quiz.id)

    