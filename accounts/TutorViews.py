
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse

from accounts.models import AffectiveDomain, Attendance, AttendanceReport, ClassAverage, ClassCategories, Classes, CombineEndTerm, CombineMidTerm, CombineSubjects, CustomUser, GncResponse, EndTerm, EntryAttestation, FeedBackStaff, LeaveReport, LessionPlan, MidTerm, NotificationStaff, OldCummulative, Psycomotor, SessionYearModel, Staff, Students, SiteControls, Subjects, SubjectStream, Terms
from hostel.models import StudentEthosRecords
from django.shortcuts import get_object_or_404, render, redirect, render

from accounts.models import AffectiveDomain, Attendance, AttendanceReport, ClassAverage, ClassCategories, Classes, CustomUser, EndTerm, FeedBackStaff, LeaveReport, LessionPlan, MidTerm, NotificationStaff, Psycomotor, SessionYearModel, Staff, Students, Subjects, Terms
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core import serializers

from django.template.defaultfilters import linebreaksbr
from django.db.models import Q, Sum
import os
from accounts.forms import EntryAttestationForm, QuestionForm
from onlinecbt.forms import QuizForm, QuizScheduleForm
from onlinecbt.models import ObjectiveOption, ObjectiveQuestion, Quiz, QuizResult, QuizSchedule, TheoryQuestion

from onlinecbt.models import Quiz, Question, Answer, QUIZ_CHOICES
from django.views import View



@login_required
def tutors_home(request):
    # <--start-->For Fetch All Student Under Staff
    subjects=Subjects.objects.filter(tutor_id=request.user.id)
    class_id_list=[]
    for subject in subjects:
        classes=Classes.objects.get(id=subject.class_id.id)
        class_id_list.append(classes.id)

    final_class=[]
    #remove duplicate class ID
    for class_id in class_id_list:
        if class_id not in final_class:
            final_class.append(class_id)

    student_count=Students.objects.filter(class_id__in=final_class).count()
    # <--end-->For Fetch All Student Under Staff

    #For Fetch All attendance Count
    attendance_count=Attendance.objects.filter(subject_id__in=subjects).count()

    #For Fetch All approved Leave
    staff=Staff.objects.get(admin=request.user.id)
    leave_count=LeaveReport.objects.filter(staff_id=staff.id,leave_status=1).count()

    #subject Count
    subject_count=subjects.count()

    # Fetch Attendance Data by Subject
    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance_count1=Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    
    student_attendance=Students.objects.filter(class_id__in=final_class)
    student_list=[]
    student_list_attendance_present=[]
    student_list_attendance_absent=[]
    for student in student_attendance:
        attendance_present_count=AttendanceReport.objects.filter(status=True,student_id=student.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(status=False,student_id=student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    return render(request,"tutors_template/tutors_home.html",{"student_count":student_count,"attendance_count":attendance_count,"leave_count":leave_count,"subject_count":subject_count,"subject_list":subject_list,"attendance_list":attendance_list,"student_list":student_list,"present_list":student_list_attendance_present,"absent_list":student_list_attendance_absent})

@login_required
def subject_students(request):
    form_classes=ClassCategories.objects.filter(form_tutor=request.user.id)
    form_subjects=Subjects.objects.filter(tutor=request.user.id)
    return render(request,"tutors_template/subject_students_template.html",{"form_classes":form_classes,"form_subjects":form_subjects})


@csrf_exempt
def get_tutor_students(request):
    subject_id=request.POST.get("subject")
    class_ids=request.POST.get("classid") 

    if subject_id=='all':
        students=Students.objects.filter(class_id=class_ids)
    else:
        subject=Subjects.objects.get(id=subject_id)
        students=Students.objects.filter(class_id=subject.class_id)

    list_data=[]
    for student in students:
        data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"gender":student.gender,"profile_pic":str(student.profile_pic)}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@login_required
def asses_formclass(request):
    form_class=ClassCategories.objects.get(form_tutor=request.user.id)
    return render(request,"tutors_template/asses_formclass.html",{"form_class":form_class})

@login_required
def tutors_subjects(request):
    tutor_subjects=Subjects.objects.filter(tutor=request.user.id)
    return render(request,"tutors_template/tutors_subjects_template.html",{"tutor_subjects":tutor_subjects})

@login_required
def tutors_profile(request):
    return render(request,"tutors_template/tutors_profile_template.html")


@login_required
def take_attendance(request):
    subjects=Subjects.objects.filter(tutor=request.user.id)
    session_years=SessionYearModel.objects.all()
    return render(request,"tutors_template/take_attendance_template.html",{"subjects":subjects,"session_years":session_years})

@csrf_exempt
def get_students(request):
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.objects.get(id=session_year)
    students=Students.objects.filter(class_id=subject.class_id,session_year_id=session_model)
    list_data=[]
    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name,"reg_id":student.admin.username}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def save_attendance_date(request):
    student_ids=request.POST.get("student_ids")
    subject_id=request.POST.get("subject_id")
    attendance_date=request.POST.get("attendance_date")
    session_year_id=request.POST.get("session_year_id")

    subject_model=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.objects.get(id=session_year_id)
    json_student=json.loads(student_ids)
    
    try:
        attendance=Attendance(subject_id=subject_model,attendance_date=attendance_date,session_year_id=session_model)
        attendance.save()

        for stud in json_student:
            student=Students.objects.get(admin=stud['id'])
            attendance_report=AttendanceReport(student_id=student,attendance_id=attendance,status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")

@login_required
def student_attendance(request):
    subjects=Subjects.objects.filter(tutor=request.user.id)
    session_year_id=SessionYearModel.objects.all()
    return render(request,"tutors_template/student_attendance_template.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def get_attendance_date(request):
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
def get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def update_attendance_date(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    json_student=json.loads(student_ids)
    
    try:
        for stud in json_student:
            student=Students.objects.get(admin=stud['id'])
            attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
            attendance_report.status=stud['status']
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")

@login_required
def staff_leave(request):
    staff_obj=Staff.objects.get(admin=request.user.id)
    leave_data=LeaveReport.objects.filter(staff_id=staff_obj)
    return render(request,"tutors_template/staff_leave_template.html",{"leave_data":leave_data})


@login_required
def staff_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_reason")

        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReport(staff_id=staff_obj,leave_messagee=leave_msg,leave_date=leave_date,leave_status=0)
            leave_report.save()
             
            messages.success(request,"Application Successfully Submitted")
            return HttpResponseRedirect(reverse("staff_leave"))
        except:
            messages.error(request,"Failed Submit Application")
            return HttpResponseRedirect(reverse("staff_leave"))


@login_required
def staff_feedback(request):
    staff_id=Staff.objects.get(admin=request.user.id)
    feedback_data=FeedBackStaff.objects.filter(staff_id=staff_id)
    return render(request,"tutors_template/staff_feedback_template.html",{"feedback_data":feedback_data})


@login_required
def staff_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaff(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
             
            messages.success(request,"Feedback Successfully Sent")
            return HttpResponseRedirect(reverse("staff_feedback"))
        except:
            messages.error(request,"Failed To Send Feedback")
            return HttpResponseRedirect(reverse("staff_feedback"))
            
            
@login_required
def staff_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    tutor=Staff.objects.get(admin=user)
    return render(request,"tutors_template/staff_profile.html",{"user":user,"tutor":tutor})


@login_required
def staff_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_profile"))
    else:
        address=request.POST.get("address")
        password=request.POST.get("password")

        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            if password!=None and password!="":
                customuser.set_password(password)
                customuser.save()
                staff=Staff.objects.get(admin=customuser.id)
                staff.address=address
                staff.save()
                messages.success(request,"Profile Successfully Updated")
                return HttpResponseRedirect(reverse("login"))
            else:
                staff=Staff.objects.get(admin=customuser.id)
                staff.address=address
                staff.save()
                messages.success(request,"Profile Successfully Updated")
                return HttpResponseRedirect(reverse("staff_profile"))

        except:
            messages.error(request,"Failed To Update")
            return HttpResponseRedirect(reverse("staff_profile"))


@csrf_exempt
def staff_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        staff=Staff.objects.get(admin=request.user.id)
        staff.fcm_token=token
        staff.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@login_required
def staff_all_notification(request):
    staff=Staff.objects.get(admin=request.user.id)
    notification=NotificationStaff.objects.filter(staff_id=staff.id)
    return render(request,"tutors_template/all_notifcation.html",{"notifications":notification})


@login_required
def result_action(request):
    return render(request,"tutors_template/result_action.html")


@login_required
def result_action_midterm(request):
    return render(request,"tutors_template/result_action_midterm.html")

@login_required
def result_action_endterm(request):
    return render(request,"tutors_template/result_action_endterm.html")


@login_required
def tutorview_midterm_result(request):
    current_session=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    subjects=Subjects.objects.filter(tutor=request.user.id)
    combsub = CombineSubjects.objects.filter(tutor=request.user.id)
    combsub = combsub.exclude(subject_main__in=subjects)
   
    if request.method!="POST":
        return render(request,"tutors_template/view_midterm_results.html",{"current_session":current_session,"subjects":subjects,"current_term":current_term,"combsub":combsub})
    else:
        subject_id = request.POST.get("subject")
        subject = Subjects.objects.get(id=subject_id)
        # Check initial values
        form = EntryAttestationForm()
        term_initial = form.fields['term'].initial
        session_year_initial = form.fields['session_year'].initial
        result_type_initial = form.fields['result_type'].initial
        existing_entry = EntryAttestation.objects.filter(term=term_initial, session_year=session_year_initial,result_type=result_type_initial, subjects=subject).exists()
        atestation = 0
        if existing_entry:
            atestation = 1
        else:
            atestation = 2
        
        form.fields['subjects'].initial = subject.id

        check_exist = CombineSubjects.objects.filter(subject_main=subject).exists()
        if check_exist:
            students = Students.objects.filter(class_id=subject.class_id)

            json_data = []
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
                    except CombineMidTerm.DoesNotExist:
                        subject_data = {
                            f"{combinesubject.name}": "No Record Found",
                        }
                    student_data.update(subject_data)

                json_data.append(student_data)
            midterm_result=MidTerm.objects.filter(session_year=current_session,term=current_term,subjects_id=subject)
            return render(request,"tutors_template/view_midterm_results.html",{"viewtype":2,"results":midterm_result, "json_data": json_data,"current_session":current_session,"subjects":subjects,"current_term":current_term,'form': form,"atestation":atestation})
        else:
            midterm_result=MidTerm.objects.filter(session_year=current_session,term=current_term,subjects_id=subject)
            return render(request,"tutors_template/view_midterm_results.html",{"viewtype":1,"results":midterm_result,"current_session":current_session,"subjects":subjects,"current_term":current_term, 'form': form,"atestation":atestation})


def combmidterm_save(request):
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
        return HttpResponseRedirect(reverse("tutorview_midterm_result"))
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
        return HttpResponseRedirect(reverse("tutorview_midterm_result"))

    
            


@csrf_exempt
def get_midterm_result(request):
    subject_id=request.POST.get("subject")

    subject=Subjects.objects.get(id=subject_id)
    current_session=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    students=Students.objects.filter(class_id=subject.class_id,session_year_id=current_session)
    list_data=[]
    for student in students:
        
        midterm_result=MidTerm.objects.get(session_year=current_session,term=current_term,students_id=student)
        data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"resumption_test":midterm_result.resumption_text,"class_work":midterm_result.class_work,"assignment":midterm_result.assignment,"midterm_exam":midterm_result.midterm_exam,"total_score":midterm_result.total_score,"grades":midterm_result.grades,"remark":midterm_result.remark,"restype":1,"score_id":midterm_result.id}
        list_data.append(data_small)
        
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def get_endterm_result(request):
    subject_id=request.POST.get("subject")
    subject=Subjects.objects.get(id=subject_id)
    current_session=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    
    list_data=[]
    get_results=EndTerm.objects.filter(subjects_id=subject,term=current_term,session_year=current_session)
    for get_result in get_results:
        data_small={"id":get_result.students_id.admin.id,"reg_id":get_result.students_id.admin.username,"name":get_result.students_id.admin.first_name+" "+get_result.students_id.admin.last_name,"asstest":get_result.ca2,"project":get_result.project_practical,"class_work":get_result.class_work,"assignment":get_result.ca1,"exam":get_result.endterm_exam,"total_score":get_result.total,"first_tot":get_result.first_total,"grades":get_result.grades,"remark":get_result.effort,"restype":2, "score_id":endterm_result.id}
        list_data.append(data_small)
       
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)


@login_required
def tutorview_endterm_result(request):
    current_session=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    subjects=Subjects.objects.filter(tutor=request.user.id)
    combsub = CombineSubjects.objects.filter(tutor=request.user.id)
    combsub = combsub.exclude(subject_main__in=subjects)
    if request.method!="POST":
        return render(request,"tutors_template/view_endterm_results.html",{"current_session":current_session,"subjects":subjects,"current_term":current_term,"combsub":combsub})
    else:
        subject_id=request.POST.get("subject")
        subject=Subjects.objects.get(id=subject_id)
        check_exist = CombineSubjects.objects.filter(subject_main=subject).exists()
        form = EntryAttestationForm()
        # Check initial values
        term_initial = form.fields['term'].initial
        session_year_initial = form.fields['session_year'].initial
        result_type_initial = form.fields['result_type'].initial
        existing_entry = EntryAttestation.objects.filter(term=term_initial, session_year=session_year_initial,result_type=result_type_initial, subjects=subject).exists()
        atestation = 0
        if existing_entry:
            atestation = 1
        else:
            atestation = 2
        
        form.fields['subjects'].initial = subject.id
        if check_exist:
            students = Students.objects.filter(class_id=subject.class_id)

            json_data = []
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
                    except CombineEndTerm.DoesNotExist:
                        subject_data = {
                            f"{combinesubject.name}": "No Record Found",
                        }
                    student_data.update(subject_data)

                json_data.append(student_data)
            endterm_result=EndTerm.objects.filter(session_year=current_session,term=current_term,subjects_id=subject)
            return render(request,"tutors_template/view_endterm_results.html",{"viewtype":2,"results":endterm_result, "json_data":json_data,"current_session":current_session,"subjects":subjects,"current_term":current_term,'form': form,"atestation":atestation})
        else:
            endterm_result=EndTerm.objects.filter(session_year=current_session,term=current_term,subjects_id=subject)
            return render(request,"tutors_template/view_endterm_results.html",{"viewtype":1,"results":endterm_result,"current_session":current_session,"subjects":subjects,"current_term":current_term,'form': form,"atestation":atestation})


def combendterm_save(request):
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
        return HttpResponseRedirect(reverse("tutorview_endterm_result"))
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
        return HttpResponseRedirect(reverse("tutorview_endterm_result"))


@login_required
def form_class(request):
    form_class=ClassCategories.objects.filter(form_tutor=request.user.id)
    subject_class=Subjects.objects.filter(tutor=request.user.id)
    return render(request,"tutors_template/form_class_template.html",{"form_class":form_class,"subject_class":subject_class})

@login_required
def tutor_add_midterm_result(request):
    subjects=Subjects.objects.filter(tutor=request.user.id)
    session_year=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    combsub=CombineSubjects.objects.filter(tutor=request.user.id)
    site_control = SiteControls.objects.filter(c_code='RT').first()
    return render(request,"tutors_template/tutor_add_midterm_result.html",{"combsub":combsub,"subjects":subjects,"session_years":session_year,"current_term":current_term, "site_control":site_control})


@login_required
def tutor_add_endterm_result(request):
    subjects=Subjects.objects.filter(tutor=request.user.id)
    session_year=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    combsub=CombineSubjects.objects.filter(tutor=request.user.id)
    site_control = SiteControls.objects.filter(c_code='RT').first()
    return render(request,"tutors_template/tutor_add_endterm_result.html",{"combsub":combsub,"subjects":subjects,"session_years":session_year,"current_term":current_term, "site_control":site_control})

@csrf_exempt
def result_get_students(request):
    subject_id=request.POST.get('subject')
    subtype=int(request.POST.get('subtype'))
    
    if subtype==1:

        subject=Subjects.objects.get(id=subject_id)
        students=Students.objects.filter(class_id=subject.class_id).order_by('admin__first_name')
        list_data=[]
        for student in students:
            data_small={"id":student.admin.id,"reg":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"reg_id":student.admin.username,"class_ids":subject.class_id_id}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    
    else:
        subject=CombineSubjects.objects.get(id=subject_id)
        students=Students.objects.filter(class_id=subject.subject_main.class_id).order_by('admin__first_name')
        list_data=[]
        for student in students:
            data_small={"id":student.admin.id,"reg":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"reg_id":student.admin.username,"class_ids":subject.subject_main.class_id_id}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)


@login_required            
def delete_score(request,restype,score_id):
    try:
        if restype==1:
            dels=MidTerm.objects.get(id=score_id)
            dels.delete()
            
            messages.info(request,"Entry Deleted Successfully, Check List Below TO Confirm")
            return HttpResponseRedirect(reverse("tutorview_midterm_result"))
        elif restype==2:
            dels=EndTerm.objects.get(id=score_id)
            dels.delete()
            
            messages.success(request,"Entry Deleted Successfully, Check TO Confirm")
            return HttpResponseRedirect(reverse("tutorview_endterm_result"))
        elif restype==3:
            dels=AffectiveDomain.objects.get(id=score_id)
            dels.delete()
            
            messages.success(request,"Entry Deleted Successfully, Check TO Confirm")
            return HttpResponseRedirect(reverse("AdminViews:domainview"))
        elif restype==4:
            dels=Psycomotor.objects.get(id=score_id)
            dels.delete()
            
            messages.success(request,"Entry Deleted Successfully, Check TO Confirm")
            return HttpResponseRedirect(reverse("AdminViews:domainview"))
        else:
            messages.success(request,"Entry Deleted Successfully, Check TO Confirm")
            return HttpResponseRedirect(reverse("tutorview_endterm_result"))
        
    except:
        messages.error(request,"Failed To Delete Entry, Please Check and Try Again")
        return HttpResponseRedirect(reverse("tutorview_midterm_result"))
  

@login_required
def save_midterm_result(request):
    if request.method!='POST':
        return HttpResponse(reverse,"tutor_add_midterm_result")



    student_admin_id=request.POST.get('student_list')
    resumption_test=request.POST.get('resumption_test')
    class_work=request.POST.get('class_work')
    assignment_score=request.POST.get('assignment')
    midterm_exams=request.POST.get('midterm_exam')
    subject_id=request.POST.get('subject')
    class_id =int(request.POST.get('class_id'))

    student_obj=Students.objects.get(admin=student_admin_id)
    subject_obj=Subjects.objects.get(id=subject_id)
    term_obj=Terms.objects.get(status=1)
    session_id=SessionYearModel.objects.get(status=1)

    if class_id >= 4:
        total_score=int(resumption_test)+float(class_work)+int(assignment_score)+int(midterm_exams)
        average_score=total_score/2
        if average_score >=13:
            grade='A'
            remark='Excellent'
        elif average_score >=10:
            grade='B'
            remark='Very Good'
        elif average_score >=8:
            grade='C'
            remark='Good'
        elif average_score >=6:
            grade='P'
            remark='Pass'
        else:
            grade='F'
            remark='Fail'
    elif class_id <= 3:
        average_score=int(resumption_test)+float(class_work)+int(assignment_score)+int(midterm_exams)
        if average_score >=25:
            grade='A'
            remark='Excellent'
        elif average_score >=20:
            grade='B'
            remark='Very Good'
        elif average_score >=15:
            grade='C'
            remark='Good'
        elif average_score >=10:
            grade='P'
            remark='Pass'
        else:
            grade='F'
            remark='Fail'

    # try:
    check_exist=MidTerm.objects.filter(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id).exists()
    if check_exist:
        result=MidTerm.objects.get(subjects_id=subject_obj,students_id=student_obj)
        result.resumption_text=resumption_test
        result.class_work=class_work
        result.assignment=assignment_score
        result.midterm_exam=midterm_exams
        result.total_score=average_score
        result.grades=grade
        result.remark=remark
        result.save()
        messages.success(request,"Successfully Updated Result")
        return HttpResponseRedirect(reverse("tutor_add_midterm_result"))

    else:

        student_admin_id=request.POST.get('student_list')
        resumption_test=request.POST.get('resumption_test')
        class_work=request.POST.get('class_work')
        assignment_score=request.POST.get('assignment')
        midterm_exams=request.POST.get('midterm_exam')
        subject_id=request.POST.get('subject')
        class_id =int(request.POST.get('class_id'))
        entrytype = request.POST.get('entrytype')
        
        if entrytype=='1':
            student_obj=Students.objects.get(admin=student_admin_id)
            subject_obj=Subjects.objects.get(id=subject_id)
            term_obj=Terms.objects.get(status=1)
            session_id=SessionYearModel.objects.get(status=1)
        
            if class_id >= 4:
                total_score=float(resumption_test)+float(class_work)+float(assignment_score)+float(midterm_exams)
                average_score=total_score/2
                average_score=round(average_score,2)
                if average_score >=12.5:
                    grade='A'
                    remark='Excellent'
                elif average_score >=9.5:
                    grade='B'
                    remark='Very Good'
                elif average_score >=7.5:
                    grade='C'
                    remark='Good'
                elif average_score >=5.5:
                    grade='P'
                    remark='Pass'
                else:
                    grade='F'
                    remark='Fail'
            elif class_id <= 3:
                average_score=float(resumption_test)+float(class_work)+float(assignment_score)+float(midterm_exams)
                average_score=round(average_score,2)
                if average_score >=24.5:
                    grade='A'
                    remark='Excellent'
                elif average_score >=19.5:
                    grade='B'
                    remark='Very Good'
                elif average_score >=14.5:
                    grade='C'
                    remark='Good'
                elif average_score >=9.5:
                    grade='P'
                    remark='Pass'
                else:
                    grade='F'
                    remark='Fail'
        
            try:
                check_exist=MidTerm.objects.filter(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id).exists()
                if check_exist:
                    result=MidTerm.objects.get(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id)
                    result.resumption_text=resumption_test
                    result.class_work=class_work
                    result.assignment=assignment_score
                    result.midterm_exam=midterm_exams
                    result.total_score=average_score
                    result.grades=grade
                    result.remark=remark
                    result.save()
                    messages.success(request,"Successfully Updated Result")
                    return HttpResponseRedirect(reverse("tutor_add_midterm_result"))
                else:
                    result=MidTerm(students_id=student_obj,subjects_id=subject_obj,resumption_text=resumption_test,class_work=class_work,assignment=assignment_score,midterm_exam=midterm_exams,total_score=average_score,grades=grade,remark=remark,term=term_obj,session_year=session_id)
                    result.save()
                    messages.success(request,"Successfully Added Result")
                    return HttpResponseRedirect(reverse("tutor_add_midterm_result"))
            except:
                messages.error(request,"Failed To Add Result")
                return HttpResponseRedirect(reverse("tutor_add_midterm_result"))
                
        elif entrytype=='2':
            subject_id=request.POST.get('subjectcomb')
            student_obj=Students.objects.get(admin=student_admin_id)
            subject_obj=CombineSubjects.objects.get(id=subject_id)
            term_obj=Terms.objects.get(status=1)
            session_id=SessionYearModel.objects.get(status=1)

            if class_id >= 4:
                total_score=float(resumption_test)+float(class_work)+float(assignment_score)+float(midterm_exams)
                average_score=total_score/2
                if average_score >=13:
                    grade='A'
                    remark='Excellent'
                elif average_score >=10:
                    grade='B'
                    remark='Very Good'
                elif average_score >=8:
                    grade='C'
                    remark='Good'
                elif average_score >=6:
                    grade='P'
                    remark='Pass'
                else:
                    grade='F'
                    remark='Fail'
            elif class_id <= 3:
                average_score=float(resumption_test)+float(class_work)+float(assignment_score)+float(midterm_exams)
                if average_score >=25:
                    grade='A'
                    remark='Excellent'
                elif average_score >=20:
                    grade='B'
                    remark='Very Good'
                elif average_score >=15:
                    grade='C'
                    remark='Good'
                elif average_score >=10:
                    grade='P'
                    remark='Pass'
                else:
                    grade='F'
                    remark='Fail'

            try:
                check_exist=CombineMidTerm.objects.filter(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id).exists()
                if check_exist:
                    result=CombineMidTerm.objects.get(subjects_id=subject_obj,students_id=student_obj,term=term_obj,session_year=session_id)
                    result.resumption_text=resumption_test
                    result.class_work=class_work
                    result.assignment=assignment_score
                    result.midterm_exam=midterm_exams
                    result.total_score=average_score
                    result.grades=grade
                    result.remark=remark
                    result.save()
                    messages.success(request,"Successfully Updated Result")
                    return HttpResponseRedirect(reverse("tutor_add_midterm_result"))
                else:
                    result=CombineMidTerm(students_id=student_obj,subjects_id=subject_obj,resumption_text=resumption_test,class_work=class_work,assignment=assignment_score,midterm_exam=midterm_exams,total_score=average_score,grades=grade,remark=remark,term=term_obj,session_year=session_id)
                    result.save()
                    messages.success(request,"Successfully Added Result")
                    return HttpResponseRedirect(reverse("tutor_add_midterm_result"))
        
            except:
                messages.error(request,"Failed Add Result")
                return HttpResponseRedirect(reverse("tutor_add_midterm_result"))

@login_required
def save_endterm_result(request):
    if request.method!='POST':
        return HttpResponse(reverse,"tutor_add_endterm_result")
    else:
        student_admin_id=request.POST.get('student_list')
        assignment=request.POST.get('ca1')
        test=request.POST.get('ca2')
        project=request.POST.get('project')
        classwork=request.POST.get('classwork')
        exams=request.POST.get('exam')
        subject_id=request.POST.get('subject')
        entrytype = request.POST.get('entrytype')
    
        student_obj=Students.objects.get(admin=student_admin_id)
        term_obj=Terms.objects.get(status=1)
        session_id=SessionYearModel.objects.get(status=1)
        class_id=student_obj.class_id.id
        
        if entrytype=='1':
            subject_obj=Subjects.objects.get(id=subject_id)
            sec_total=float(assignment)+float(test)+float(project)+float(classwork)
        
            if class_id >= 4:
                second_total=sec_total/2
                try:
                    first_half=MidTerm.objects.get(session_year=session_id,term=term_obj,subjects_id=subject_obj,students_id=student_obj)
                    first_total=first_half.total_score
                    total_score=second_total+first_total+float(exams)
                    total_score=round(total_score,2)
                    if total_score >=79.5:
                        grade='A'
                        remark='Excellent'
                    elif total_score >=69.5:
                        grade='B'
                        remark='Very Good'
                    elif total_score >=59.5:
                        grade='C'
                        remark='Good'
                    elif total_score >=49.5:
                        grade='P'
                        remark='Pass'
                    else:
                        grade='F'
                        remark='Fail'
                except:
                    messages.error(request,"First Half Does Not Exist")
                    return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
                        
            elif class_id <= 3:
                second_total=sec_total
                try:
                    first_half=MidTerm.objects.get(session_year=session_id,term=term_obj,subjects_id=subject_obj,students_id=student_obj)
                    first_total=first_half.total_score
                    total_score=second_total+first_total+float(exams)
                    total_score=round(total_score,2)
                    if total_score >=79.5:
                        grade='A'
                        remark='Excellent'
                    elif total_score >=69.5:
                        grade='B'
                        remark='Very Good'
                    elif total_score >=59.5:
                        grade='C'
                        remark='Good'
                    elif total_score >=49.5:
                        grade='P'
                        remark='Pass'
                    else:
                        grade='F'
                        remark='Fail'
                except:
                    messages.error(request,"First Half Does Not Exist")
                    return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
        
            
            try:
                check_exist=EndTerm.objects.filter(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id).exists()
                if check_exist:
                    result=EndTerm.objects.get(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id)
                    result.ca1=assignment
                    result.ca2=test
                    result.project_practical=project
                    result.class_work=classwork
                    result.sec_total=sec_total
                    result.first_total=first_total
                    result.second_total=second_total
                    result.endterm_exam=exams
                    result.total=total_score     
                    result.grades=grade
                    result.effort=remark
                    result.save()
                    messages.success(request,"Successfully Updated Result")
                    return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
                else:
                    result=EndTerm(students_id=student_obj,subjects_id=subject_obj,term=term_obj,session_year=session_id,ca1=assignment,ca2=test,second_total=second_total,first_total=first_total,sec_total=sec_total,class_work=classwork,project_practical=project,endterm_exam=exams,total=total_score,grades=grade,effort=remark,)
                    result.save()
                    messages.success(request,"Successfully Added Result")
                    return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
            except:
                messages.error(request,"Failed Add Result")
                return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
                
        elif entrytype=='2':
            
            subject_id=request.POST.get('subjectcomb')
            subject_obj=CombineSubjects.objects.get(id=subject_id)
            
            sec_total=float(assignment)+float(test)+float(project)+float(classwork)
    
            if class_id >= 4:
                second_total=sec_total/2
                first_half=CombineMidTerm.objects.get(session_year=session_id,term=term_obj,subjects_id=subject_obj,students_id=student_obj)
                first_total=first_half.total_score
                total_score=second_total+first_total+float(exams)
                if total_score >=80:
                    grade='A'
                    remark='Excellent'
                elif total_score >=70:
                    grade='B'
                    remark='Very Good'
                elif total_score >=60:
                    grade='C'
                    remark='Good'
                elif total_score >=50:
                    grade='P'
                    remark='Pass'
                else:
                    grade='F'
                    remark='Fail'
            elif class_id <= 3:
                second_total=sec_total
                first_half=CombineMidTerm.objects.get(session_year=session_id,term=term_obj,subjects_id=subject_obj,students_id=student_obj)
                first_total=first_half.total_score
                total_score=second_total+first_total+float(exams)
                if total_score >=80:
                    grade='A'
                    remark='Excellent'
                elif total_score >=70:
                    grade='B'
                    remark='Very Good'
                elif total_score >=60:
                    grade='C'
                    remark='Good'
                elif total_score >=50:
                    grade='P'
                    remark='Pass'
                else:
                    grade='F'
                    remark='Fail'
    
            
            try:
                check_exist=CombineEndTerm.objects.filter(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id).exists()
                if check_exist:
                    result=CombineEndTerm.objects.get(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id,session_year=session_id)
                    result.ca1=assignment
                    result.ca2=test
                    result.project_practical=project
                    result.class_work=classwork
                    result.sec_total=sec_total
                    result.first_total=first_total
                    result.second_total=second_total
                    result.endterm_exam=exams
                    result.total=total_score     
                    result.grades=grade
                    result.effort=remark
                    result.save()
                    messages.success(request,"Successfully Updated Result")
                    return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
                else:
                    result=CombineEndTerm(students_id=student_obj,subjects_id=subject_obj,term=term_obj,session_year=session_id,ca1=assignment,ca2=test,second_total=second_total,first_total=first_total,sec_total=sec_total,class_work=classwork,project_practical=project,endterm_exam=exams,total=total_score,grades=grade,effort=remark,)
                    result.save()
                    messages.success(request,"Successfully Added Result")
                    return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
            except:
                messages.error(request,"Failed Add Result")
                return HttpResponseRedirect(reverse("tutor_add_endterm_result"))
        

@login_required
def manage_midterm_result(request):
    subjects=Subjects.objects.filter(tutor=request.user.id)
    session_year=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    return render(request,"tutors_template/manage_midterm_result.html",{"subjects":subjects,"session_years":session_year,"current_term":current_term})

@login_required
def manage_endterm_result(request):
    subjects=Subjects.objects.filter(tutor=request.user.id)
    session_year=SessionYearModel.objects.get(status=1)
    current_term=Terms.objects.get(status=1)
    return render(request,"tutors_template/manage_endterm_result.html",{"subjects":subjects,"session_years":session_year,"current_term":current_term})


@csrf_exempt
def get_midterm_result(request):
    subject_id=request.POST.get("subject")

    subject=Subjects.objects.get(id=subject_id)
    students=Students.objects.filter(class_id=subject.class_id)
    session_id=SessionYearModel.objects.get(status=1)
    term_id=Terms.objects.get(status=1)
    list_data=[]
    for student in students:
        try:
            midterm_result=MidTerm.objects.get(students_id=student,session_year=session_id,term=term_id,subjects_id=subject)
            data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name,"reg_id":student.admin.username,"resumption_test":midterm_result.resumption_text,"class_work":midterm_result.class_work,"assignment":midterm_result.assignment,"midterm_exam":midterm_result.midterm_exam,"total_score":midterm_result.total_score,"grades":midterm_result.grades,"remark":midterm_result.remark}
            list_data.append(data_small)
        except MidTerm.DoesNotExist:
            midterm_result=None
    
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)


@csrf_exempt
def manage_save_midterm_result(request):
    username=request.POST.get('username')
    subject_id=request.POST.get('subject')
    session=request.POST.get('session_year')
    terms=request.POST.get('term')
    resumption_test=request.POST.get('resumption_test')
    class_work=request.POST.get('class_work')
    assignment_score=request.POST.get('assignment_score')
    midterm_exams=request.POST.get('midterm_exams')

    student_ids=CustomUser.objects.get(username=username)
    student_obj=Students.objects.get(admin=student_ids)

    term_obj=Terms.objects.get(id=terms)
    session_id=SessionYearModel.objects.get(id=session)
    subject_obj=Subjects.objects.get(id=subject_id)


    total_score=float(resumption_test)+float(class_work)+float(assignment_score)+float(midterm_exams)
    average_score=total_score/2
    if average_score >=13:
        grade='A'
        remark='Excellent'
    elif average_score >=10:
        grade='B'
        remark='Very Good'
    elif average_score >=8:
        grade='C'
        remark='Good'
    elif average_score >=6:
        grade='P'
        remark='Pass'
    else:
        grade='F'
        remark='Fail'

    try:
        result=MidTerm.objects.get(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id)
        result.resumption_text=resumption_test
        result.class_work=class_work
        result.assignment=assignment_score
        result.midterm_exam=midterm_exams
        result.total_score=total_score
        result.average_score=average_score
        result.grades=grade
        result.remark=remark
        result.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("NO")


@csrf_exempt
def manage_save_endterm_result(request):
    username=request.POST.get('username')
    subject_id=request.POST.get('subject')
    session=request.POST.get('session_year')
    terms=request.POST.get('term')
    resumption_test=request.POST.get('resumption_test')
    class_work=request.POST.get('class_work')
    assignment_score=request.POST.get('assignment_score')
    midterm_exams=request.POST.get('midterm_exams')

    student_ids=CustomUser.objects.get(username=username)
    student_obj=Students.objects.get(admin=student_ids)

    term_obj=Terms.objects.get(id=terms)
    session_id=SessionYearModel.objects.get(id=session)
    subject_obj=Subjects.objects.get(id=subject_id)


    total_score=int(resumption_test)+int(class_work)+int(assignment_score)+int(midterm_exams)
    average_score=total_score/2
    if average_score >=13:
        grade='A'
        remark='Excellent'
    elif average_score >=10:
        grade='B'
        remark='Very Good'
    elif average_score >=8:
        grade='C'
        remark='Good'
    elif average_score >=6:
        grade='P'
        remark='Pass'
    else:
        grade='F'
        remark='Fail'

    try:
        result=MidTerm.objects.get(subjects_id=subject_obj,students_id=student_obj,term=term_obj.id)
        result.resumption_text=resumption_test
        result.class_work=class_work
        result.assignment=assignment_score
        result.midterm_exam=midterm_exams
        result.total_score=total_score
        result.average_score=average_score
        result.grades=grade
        result.remark=remark
        result.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("NO")




@csrf_exempt
def save_add_endterm_result(request):
    username=request.POST.get('username')
    subject_id=request.POST.get('subject')
    session=request.POST.get('session_year')
    terms=request.POST.get('term')
    assignment=request.POST.get('ca1')
    test=request.POST.get('ca2')
    project=request.POST.get('project')
    classwork=request.POST.get('classwork')
    exam=request.POST.get('exam')

    student_ids=CustomUser.objects.get(username=username)
    student_obj=Students.objects.get(admin=student_ids)

    term=Terms.objects.get(id=terms)
    session_year=SessionYearModel.objects.get(id=session)
    subject_obj=Subjects.objects.get(id=subject_id)



    total_score=int(ca1)+int(ca2)+int(exam)
    if total_score >=70:
        grade='A'
        effort=5
    elif total_score >=50:
        grade='B'
        effort=4
    elif total_score >=40:
        grade='B=C'
        effort=4
    else:
        grade='F'
        effort=0
               
    try:
        check_exist=EndTerm.objects.filter(subjects_id=subject_obj,students_id=student_obj.id,term=term,session_year=session_year).exists()
        if check_exist:
            result=EndTerm.objects.get(subjects_id=subject_obj,students_id=student_obj,term=term,session_year=session_year)
            result.ca1=ca1
            result.ca2=ca2
            result.endterm_exam=exam
            result.total=total_score     
            result.grades=grade
            result.effort=effort
            result.save()
            return HttpResponse("OK")
        else:
            result=EndTerm(students_id=student_obj,subjects_id=subject_obj,term=term,session_year=session_year,ca1=ca1,ca2=ca2,endterm_exam=exam,total=total_score,grades=grade,effort=effort)
            result.save()
            return HttpResponse("OK")
    except:
        messages.error(request,"Failed Add Result")
        return HttpResponse("NO")


@login_required
def manage_form_class(request, class_id):
    return render(request,"tutors_template/manage_form_class.html",{"class_id":class_id})
 
 
@login_required    
def tutors_assesment(request, class_id):
    form_students=Students.objects.filter(class_category=class_id)
    term=Terms.objects.get(status=1)
    session_year=SessionYearModel.objects.get(status=1)
    return render(request,"tutors_template/tutor_assesment_template.html",{"form_students":form_students})

@login_required
def class_student(request,std_id):
    term=Terms.objects.get(status=1)
    session_year=SessionYearModel.objects.get(status=1)
    class_cat=Students.objects.get(id=std_id)
    # try:
    avg_id=ClassAverage.objects.filter(students_id=std_id,term=term,session_year=session_year,result_type=2)
    #student ethos
    
    if avg_id:
        avg_id=ClassAverage.objects.get(students_id=class_cat,term=term,session_year=session_year,result_type=2)
        re_type = avg_id.result_type-1
        ethos_records = StudentEthosRecords.objects.filter(term=avg_id.term, session_year=avg_id.session_year, result_type=re_type, student_id=avg_id.students_id)
        for record in ethos_records:
            positive_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('leadership', 'neatness', 'room_represent_compet', 'room_represent_inspect', 'selfconfidence', 'team_spirit', 'return_lost_items', 'obidience_to_staff', 'obidience_to_rules', 'volunteerism', 'reporting_unacceptable_behavior', 'prayerfullness'))])
            negative_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('loitering', 'immoral_relation_conduct', 'poor_timing', 'negative_influence', 'noise_making', 'hostel_disobidience', 'bullying_fighting', 'negative_civil', 'gossip', 'avoiding_meals', 'carelessness_personal'))])
            record.total_positive_ethos = positive_ethos_sum
            record.total_negative_ethos = negative_ethos_sum
            record.total_ethos = positive_ethos_sum - negative_ethos_sum
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
        return render(request,"tutors_template/endterm_result_preview.html",{"ethos_records":ethos_records,"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"endterm":endterms})
        
    
    else:
        avg_id=ClassAverage.objects.get(students_id=std_id,term=term,session_year=session_year,result_type=1)
        #student ethos
        re_type = avg_id.result_type-1
        ethos_records = StudentEthosRecords.objects.filter(term=avg_id.term, session_year=avg_id.session_year, result_type=re_type, student_id=avg_id.students_id)
        for record in ethos_records:
            positive_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('leadership', 'neatness', 'room_represent_compet', 'room_represent_inspect', 'selfconfidence', 'team_spirit', 'return_lost_items', 'obidience_to_staff', 'obidience_to_rules', 'volunteerism', 'reporting_unacceptable_behavior', 'prayerfullness'))])
            negative_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('loitering', 'immoral_relation_conduct', 'poor_timing', 'negative_influence', 'noise_making', 'hostel_disobidience', 'bullying_fighting', 'negative_civil', 'gossip', 'avoiding_meals', 'carelessness_personal'))])
            record.total_positive_ethos = positive_ethos_sum
            record.total_negative_ethos = negative_ethos_sum
            record.total_ethos = positive_ethos_sum - negative_ethos_sum
        psychomotor=Psycomotor.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
        affective=AffectiveDomain.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
        midterm_result=MidTerm.objects.filter(students_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term)
        return render(request,"tutors_template/midterm_result_preview.html",{"ethos_records":ethos_records,"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"midterm":midterm_result})

    # except:
    #     messages.error(request,"ERROR!....Result not yet approved")
    #     return HttpResponseRedirect(reverse("tutors_assesment",kwargs={"class_id":class_cat.class_category.id}))

@login_required
def tutor_assess_student(request,students_id):
    stud=CustomUser.objects.get(id=students_id)
    student=Students.objects.get(admin=stud)
    term=Terms.objects.get(status=1)
    sessionyear=SessionYearModel.objects.get(status=1)
    mid=MidTerm.objects.filter(session_year=sessionyear, term=term, students_id=student)
    endterm=EndTerm.objects.filter(session_year=sessionyear, term=term, students_id=student)
    return render(request, "tutors_template/tutor_assess_student.html",{"student":stud,"mid":mid,"enterm":endterm})
    
@login_required
def save_assessment (request):
    student_id=request.POST.get("student_id")
    result_type=int(request.POST.get('result_type'))
    # Psychomotor
    handwriting=request.POST.get("handwirting")
    verbal=request.POST.get("verbal")
    sport=request.POST.get("sport")
    knitting=request.POST.get("knitting")

    # Affective
    punctuality=request.POST.get("punctuality")
    neatness=request.POST.get("neatness")
    initiative=request.POST.get("initiative")
    leadership=request.POST.get("leadership")
    health=request.POST.get("health")
    attentiveness=request.POST.get("attentiveness")
    coop=request.POST.get("cooperation")
    perseverance=request.POST.get("perseverance")
    helping=request.POST.get("helping")
    emotional=request.POST.get("emotional")
    
    # comments
    tcomment = request.POST.get("tcomment")
    pcomment = request.POST.get("pcomment")

    student_obj=Students.objects.get(admin=student_id)
    term=Terms.objects.get(status=1)
    session_year=SessionYearModel.objects.get(status=1)

    if result_type==1:

        if student_obj.class_id.id <= 3:

        if student_obj.class_id <= 3:
            totals=MidTerm.objects.filter(students_id=student_obj,term=term,session_year=session_year)
            subjects=totals.count()
            subject_sum=0
            for total in totals:
                subject_sum=subject_sum+total.total_score

            subject_total=subjects*30
            average=subject_sum/subject_total*100

        elif student_obj.class_id >=4:


            totals=MidTerm.objects.filter(students_id=student_obj,term=term,session_year=session_year)
            subjects=totals.count()
            subject_sum=0
            for total in totals:
                subject_sum=subject_sum+total.total_score

            subject_total=subjects*15
            average=subject_sum/subject_total*100

        elif student_obj.class_id.id >=4:

            totals=MidTerm.objects.filter(students_id=student_obj,term=term,session_year=session_year)
            subjects=totals.count()
            subject_sum=0
            for total in totals:
                subject_sum=subject_sum+total.total_score

            subject_total=subjects*15
            averages=subject_sum/subject_total*100
            average=round(averages,2)

       
    elif result_type==2:

        totals=EndTerm.objects.filter(students_id=student_obj,term=term,session_year=session_year)
        subjects=totals.count()
        subject_sum=0
        for total in totals:
            subject_sum=subject_sum+total.total

        subject_total=subjects*100

        averages=subject_sum/subject_total*100
        average=round(averages,2)
        
    try:
        checks=ClassAverage.objects.filter(students_id=student_obj,term=term,session_year=session_year,result_type=result_type).exists()
        if checks:
            class_average=ClassAverage.objects.get(students_id=student_obj,term=term,session_year=session_year,result_type=result_type)
            class_average.t_comment=tcomment
            class_average.p_comment=pcomment
            class_average.avg_percent=average
            class_average.save()
        else:
            class_average=ClassAverage(student_class=student_obj.class_id,students_id=student_obj,term=term,session_year=session_year,result_type=result_type,avg_percent=average,t_comment=tcomment,p_comment=pcomment)
            class_average.save()
    except:
        messages.error(request,"Ensure all first half scores are correctly entered and complet")
        return HttpResponseRedirect(reverse("tutor_assess_student",kwargs={"students_id":student_id}))

    try:
        check_exist=Psycomotor.objects.filter(student_id=student_obj,term=term,session_year=session_year,result_type=result_type).exists()
        if check_exist:
            check_exist=AffectiveDomain.objects.filter(student_id=student_obj,term=term,session_year=session_year,result_type=result_type).exists()
            if check_exist:
                result_psychomotor=Psycomotor.objects.get(student_id=student_obj,term=term,session_year=session_year,result_type=result_type)
                result_psychomotor.handwriting=handwriting
                result_psychomotor.verbal=verbal
                result_psychomotor.sport=sport
                result_psychomotor.knitting=knitting 
                result_psychomotor.result_type=result_type    
        
                result_affective=AffectiveDomain.objects.get(student_id=student_obj,term=term,session_year=session_year,result_type=result_type)
                result_affective.punctuality=punctuality
                result_affective.neatness=neatness
                result_affective.initiative=initiative
                result_affective.leadership=leadership
                result_affective.health=health
                result_affective.attentiveness=attentiveness
                result_affective.perseverance=perseverance
                result_affective.co_others=coop
                result_affective.helping=helping
                result_affective.emotional=emotional
                result_affective.result_type=result_type
        
                result_psychomotor.save()
                result_affective.save()
        
                messages.success(request,"Assessment Successfully Updated")
                return HttpResponseRedirect(reverse("tutor_assess_student",kwargs={"students_id":student_id}))
            
        else:
            result_psychomotor=Psycomotor(student_id=student_obj,term=term,session_year=session_year,result_type=result_type,handwriting=handwriting,verbal=verbal,sport=sport,knitting=knitting)
            result_affective=AffectiveDomain(student_id=student_obj,term=term,session_year=session_year,result_type=result_type,punctuality=punctuality,neatness=neatness,initiative=initiative,leadership=leadership,health=health,attentiveness=attentiveness,perseverance=perseverance,helping=helping,emotional=emotional,co_others=coop)
            result_psychomotor.save()
            result_affective.save()
            messages.success(request,"Successfully Assessed")
            return HttpResponseRedirect(reverse("tutor_assess_student",kwargs={"students_id":student_id}))
    except:
        messages.error(request,"Failed to Assess Student, try again or contact ICT support")

        average=subject_sum/subject_total*100
        
    # try:
    checks=ClassAverage.objects.filter(students_id=student_obj,term=term,session_year=session_year,result_type=result_type).exists()
    if checks:
        class_average=ClassAverage.objects.get(students_id=student_obj,term=term,session_year=session_year,result_type=result_type)
        class_average.avg_percent=average
        class_average.save()
    else:
        class_average=ClassAverage(student_class=student_obj.class_id,students_id=student_obj,term=term,session_year=session_year,result_type=result_type,avg_percent=average)
        class_average.save()
    # except:
    #     messages.error(request,"Ensure all first half scores are correctly entered and complet")
    #     return HttpResponseRedirect(reverse("tutor_assess_student",kwargs={"students_id":student_id}))


    check_exist=Psycomotor.objects.filter(student_id=student_obj,term=term,session_year=session_year).exists()
    if check_exist:
        result_psychomotor=Psycomotor.objects.get(student_id=student_obj,term=term,session_year=session_year)
        result_psychomotor.handwriting=handwriting
        result_psychomotor.verbal=verbal
        result_psychomotor.sport=sport
        result_psychomotor.knitting=knitting 
        result_psychomotor.result_type=result_type    

        result_affective=AffectiveDomain.objects.get(student_id=student_obj,term=term,session_year=session_year)
        result_affective.punctuality=punctuality
        result_affective.neatness=neatness
        result_affective.initiative=initiative
        result_affective.leadership=leadership
        result_affective.health=health
        result_affective.attentiveness=attentiveness
        result_affective.perseverance=perseverance
        result_affective.helping=helping
        result_affective.emotional=emotional
        result_affective.result_type=result_type

        result_psychomotor.save()
        result_affective.save()

        messages.success(request,"Assessment Successfully Updated")

        return HttpResponseRedirect(reverse("tutor_assess_student",kwargs={"students_id":student_id}))
@login_required
def form_students(request, class_id):
    form_students=Students.objects.filter(class_category=class_id)
    return render(request,"tutors_template/view_form_student.html",{"form_students":form_students})


@login_required
@csrf_exempt
def class_results(request, class_id):
    all_sessions=SessionYearModel.objects.filter(status=1)
    all_terms=Terms.objects.all()
    clas_id=ClassCategories.objects.get(id=class_id)
    all_subj=Subjects.objects.filter(class_id=clas_id.class_id)
    if request.method!="POST":
        return render(request,"tutors_template/get_class_result.html",{"all_sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj,"class_id":class_id})
    else:
        result_type=int(request.POST.get('result_type'))
        subjects=int(request.POST.get('subject'))
        term=int(request.POST.get('term'))
        session=int(request.POST.get('session'))
        
        subject=Subjects.objects.get(id=subjects)
        current_session=SessionYearModel.objects.get(id=session)
        current_term=Terms.objects.get(id=term)
        
        list_data=[]
        if result_type==1:
            get_results=MidTerm.objects.filter(subjects_id=subject,session_year=current_session,term=current_term)
            
            for get_result in get_results:
                clas_cat = get_result.students_id.class_category.id
                if clas_cat==clas_id.id:
                    data_small={"ids":get_result.id,"id":get_result.students_id.admin.id,"reg_id":get_result.students_id.admin.username,"name":get_result.students_id.admin.first_name+" "+get_result.students_id.admin.last_name,"resumption_test":get_result.resumption_text,"class_work":get_result.class_work,"assignment":get_result.assignment,"midterm_exam":get_result.midterm_exam,"total_score":get_result.total_score,"grades":get_result.grades,"remark":get_result.remark}
                    list_data.append(data_small)
                # else:
                #     return render(request,"tutors_template/get_class_result.html",{"sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj,"class_id":class_id})

        elif result_type==2:
    
            get_results=EndTerm.objects.filter(subjects_id=subject,term=term,session_year=session)
            
            for get_result in get_results:
                data_small={"id":get_result.students_id.admin.id,"reg_id":get_result.students_id.admin.username,"name":get_result.students_id.admin.first_name+" "+get_result.students_id.admin.last_name,"asstest":get_result.ca2,"project":get_result.project_practical,"class_work":get_result.class_work,"assignment":get_result.ca1,"exam":get_result.endterm_exam,"total_score":get_result.total,"first_tot":get_result.first_total,"grades":get_result.grades,"remark":get_result.effort}
                list_data.append(data_small)
           
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
   
    
@login_required
def submit_plan(request):
    current_term=Terms.objects.get(status=1)
    tutor_subjects=Subjects.objects.filter(tutor=request.user.id)
    current_sessions=SessionYearModel.objects.get(status=1)
    combine_subjects = CombineSubjects.objects.filter(tutor=request.user.id)
    site_control = SiteControls.objects.filter(c_code='LP').first()
    les_count = site_control.count_value
    less_plan=range(les_count, 15 + 1)
    if request.method!="POST":
        leplans = LessionPlan.objects.filter(Q(subjects__tutor=request.user.id) | Q(subjects__in=combine_subjects.values('subject_main')))

        return render(request,"tutors_template/submit_plat_template.html",{"subjects":tutor_subjects, "current_term":current_term,"leplans":leplans, "c_subjects":combine_subjects, "less_plan":less_plan})
    else:
        week=request.POST.get('weeks')
        subject=int(request.POST.get('subject'))
        all_subjects=Subjects.objects.all()
        subject=all_subjects.get(id=subject)
        notes=request.POST.get('notes')
        
        plan_file = request.FILES['plan_file']
        fs=FileSystemStorage(location="/home/chrijpdc/public_html/media/lession_plan/")
        filename=fs.save(plan_file.name,plan_file)
        plan_file_url=fs.url("lession_plan/"+filename)

        try:
            LessionPlan.objects.create(weeks=week,session_year=current_sessions,notes=notes,term=current_term,subjects=subject,plan_file=plan_file_url)

def submit_plan(request):
    current_term=Terms.objects.get(status=1)
    tutor_subjects=Subjects.objects.filter(tutor=request.user.id)
    if request.method!="POST":
        leplans=LessionPlan.objects.all()
        return render(request,"tutors_template/submit_plat_template.html",{"subjects":tutor_subjects, "current_term":current_term,"leplans":leplans})
    else:
        week=request.POST.get('weeks')
        subject=int(request.POST.get('subject'))
        subject=tutor_subjects.get(id=subject)
        
        plan_file = request.FILES['plan_file']
        fs=FileSystemStorage()
        filename=fs.save(plan_file.name,plan_file)
        plan_file_url=fs.url(filename)

        try:
            LessionPlan.objects.create(weeks=week,term=current_term,subjects=subject,plan_file=plan_file_url)

            messages.success(request,"Lession Plan Submitted Successfully, Check List Below TO Confirm")
            return HttpResponseRedirect(reverse("submit_plan"))
        except:
            messages.error(request,"Failed To Submit Lession Plan, Please Check and Try Again")
            return HttpResponseRedirect(reverse("submit_plan"))


@login_required            
def delete_plan(request,item_id):
    try:
        dels=LessionPlan.objects.get(id=item_id)
        dels.delete()
        
        messages.info(request,"Entry Deleted Successfully, Check List Below TO Confirm")
        return HttpResponseRedirect(reverse("submit_plan"))
    except:
        messages.error(request,"Failed To Delete Entry, Please Check and Try Again")
        return HttpResponseRedirect(reverse("submit_plan"))


@login_required        
def delete_mid(request,item_id):
    try:
        dels=MidTerm.objects.get(id=item_id)
        dels.delete()
        
        messages.info(request,"Entry Deleted Successfully, Check List Below TO Confirm")
        return HttpResponseRedirect(reverse("class_results"))
    except:
        messages.error(request,"Failed To Delete Entry, Please Check and Try Again")
        return HttpResponseRedirect(reverse("class_results"))


@login_required      
def delete_end(request,item_id):
    try:
        dels=EndTerm.objects.get(id=item_id)
        dels.delete()
        
        messages.info(request,"Entry Deleted Successfully, Check List Below TO Confirm")
        return HttpResponseRedirect(reverse("submit_plan"))
    except:
        messages.error(request,"Failed To Delete Entry, Please Check and Try Again")
        return HttpResponseRedirect(reverse("submit_plan"))
        


def gandc (request):
    students= Students.objects.filter(class_id__in=[3,4,5]).order_by('class_id__name')
    old_results=OldCummulative.objects.all().order_by('created_at')
    subjstreaming = SubjectStream.objects.all().order_by('created_at')
    # Process subj_choice field
    for obj in subjstreaming:
        subj_choice = obj.subj_choice.strip("[]'").split("', '")
        obj.subj_choice = subj_choice
        
    # Calculate GncResponse totals for each student
    studentss = students.filter(class_id=3)
    student_totals = []
    
    for student in studentss:
        total_humanity = GncResponse.objects.filter(student=student, question__field_type='Humanities').aggregate(total=Sum('answer_choice'))['total'] or 0
        total_science = GncResponse.objects.filter(student=student, question__field_type='Science').aggregate(total=Sum('answer_choice'))['total'] or 0
        total_business = GncResponse.objects.filter(student=student, question__field_type='Business').aggregate(total=Sum('answer_choice'))['total'] or 0
        total_technology = GncResponse.objects.filter(student=student, question__field_type='Technology').aggregate(total=Sum('answer_choice'))['total'] or 0
    
        totals = {
            'student': student,
            'total_humanity': total_humanity,
            'percent_humanity': round((total_humanity / 245) * 100),
            'total_science': total_science,
            'percent_science': round((total_science / 95) * 100),
            'total_business': total_business,
            'percent_business': round((total_business / 95) * 100),
            'total_technology': total_technology,
            'percent_technology': round((total_technology / 65) * 100),
        }
        
        student_totals.append(totals)
        
    if request.method!="POST":
        form = QuestionForm()
        return render(request,"tutors_template/g_and_c.html",{"students":students,"old_results":old_results,"subjstreaming":subjstreaming, 'student_totals': student_totals, 'form': form})
    else:
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gandc')
        # student=int(request.POST.get('student'))
        # student = Students.objects.get(id=student)
        
        # session_year = SessionYearModel.objects.get(status=1)
        # results= EndTerm.objects.filter(students_id=student)
        # subjects = Subjects.objects.all()
        # subject = subjects.filter(class_id=1)
        # json_data = []
        # for subj in subject:
        #     student_data = {
        #         "subject_id":subj.subject_name
        #     }
            
        #     if student.class_id.id == 3:
        #         # 1st class result
        #         first_session = session_year.id - 2
        #         year_ones = results.filter(session_year=first_session, subjects_id=subj)
        #         # Calculate the average of total scores
        #         total_scores = [year_one.total for year_one in year_ones]
        #         average_score = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00
                
                
        #         #2nd class result
        #         general_outline = str(subj.outline)[:3]
        #         subject_second_year = subjects.get(outline__startswith=general_outline, class_id=2)
        #         second_session = session_year.id - 1
        #         year_twos = results.filter(session_year=second_session, subjects_id=subject_second_year)
        #         # Calculate the average of total scores
        #         total_scores = [year_two.total for year_two in year_twos]
        #         average_score = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00
                
                
        #         # 3rd class result
        #         subject_third_year = subjects.get(outline__startswith=general_outline, class_id=3)
        #         second_session = session_year.id - 1
        #         year_threes = results.filter(session_year=session_year, subjects_id=subject_third_year)
        #         # Calculate the average of total scores
        #         total_scores = [year_three.total for year_three in year_threes]
        #         average_score = round(sum(total_scores) / len(total_scores), 2) if len(total_scores) > 0 else 0.00
                
        #     elif student.class_id.id == 4:
        #         # 1st class result
        #         first_session = session_year.id - 3
        #         year_one = results.filter(session_year=first_session, subjects_id=subj)
                
        #         #2dn class result
        #         second_session = session_year.id - 2
        #         year_two = results.filter(session_yeare=second_session, subjects_id=subj)
                
        #         # 3rd class result
        #         third_session = session_year.id - 1
        #         year_three = results.filter(session_year=third_session, subjects_id=subj)
            
        #     elif student.class_id.id == 5:
        #         # 1st class result
        #         first_session = session_year.id - 4
        #         year_one = results.filter(session_year=first_session, subjects_id=subj)
                
        #         #2dn class result
        #         second_session = session_year.id - 3
        #         year_two = results.filter(session_year=second_session, subjects_id=subj)
                
        #         # 3rd class result
        #         third_session = session_year.id - 2
        #         year_three = results.filter(session_year=third_session, subjects_id=subj)
                

        #     json_data.append(student_data)
        # return render(request,"tutors_template/g_and_c.html",{"students":students,"json_data":json_data})

@login_required
def tutorattestation(request):
    if request.method == 'POST':
        form = EntryAttestationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or homepage if referer not found
    else:
        return redirect(request.META.get('HTTP_REFERER', '/'))

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
 
         
@login_required
def formbroadsheet(request):
    all_sessions=SessionYearModel.objects.filter(status=1)
    all_terms=Terms.objects.all()
    
    if request.method =="POST":
        # Post data
        result_type=int(request.POST.get('result_type'))
        clas_cat=int(request.POST.get('class_name'))
        term=int(request.POST.get('term'))
        sess_year=int(request.POST.get('session'))
        
        # Retrieve students
        class_cat = ClassCategories.objects.get(id=clas_cat)
        all_subj=Subjects.objects.filter(class_id=class_cat.class_id)
        re_type = result_type-1
        #student ethos
        ethos_records = StudentEthosRecords.objects.filter(term=term, session_year=sess_year, result_type=re_type, student_id__class_category=class_cat)
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
                    "all_subj":all_subj,
                    "class_id":class_cat,
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
            return render(request, 'tutors_template/get_class_result.html', context)
        
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
                    "all_subj":all_subj,
                    "class_id":class_cat,
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
            return render(request, 'tutors_template/get_class_result.html', context) 
    else:
        return redirect(request.META.get('HTTP_REFERER', '/'))
        
        
   
#<---------------|CBT|------------------->
# View to display the page with the accordions for Quiz and Quiz Schedule
def quiz_management(request):
    # Filter subjects where the current user is the tutor
    subjects_taught = Subjects.objects.filter(
        Q(tutor=request.user) | 
        Q(id__in=CombineSubjects.objects.filter(tutor=request.user).values('subject_main'))
    ).distinct()

    # Filter quizzes by the subjects taught by the current user and order by creation date
    quizzes = Quiz.objects.filter(subject__in=subjects_taught).order_by('-created_at')

    # Filter quiz schedules by quizzes related to the subjects taught by the current user and order by start_time
    schedules = QuizSchedule.objects.filter(quiz__subject__in=subjects_taught).order_by('-start_time')


    quiz_form = QuizForm(tutor=request.user)
    schedule_form = QuizScheduleForm(tutor=request.user)

    context = {
        'quiz_form': quiz_form,
        'schedule_form': schedule_form,
        'quizzes': quizzes,
        'schedules': schedules,
    }
    return render(request, 'tutors_template/quizes/add_quiz.html', context)


def add_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Quiz added successfully!'})
        else:
            # Return the errors to display on the frontend
            return JsonResponse({'status': 'error', 'errors': form.errors})

    return redirect('tutor_quiz_management')


# View to handle adding a quiz schedule
def add_quiz_schedule(request):
    if request.method == 'POST':
        form = QuizScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Schedule added successfully!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    return redirect('tutor_quiz_management')


# View to handle editing a quiz (only title and description)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    return redirect('tutor_quiz_management')


# View to delete a quiz schedule (only if pending or ongoing)
def delete_quiz_schedule(request, schedule_id):
    schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    if schedule.status in ['pending', 'ongoing']:
        schedule.delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Cannot delete a completed schedule'})

# View to handle editing a quiz schedule (only date, time, and status)
def edit_quiz_schedule(request, schedule_id):
    schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    if request.method == 'POST':
        form = QuizScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
            




# View to display quiz details with buttons to manage questions
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    objective_questions = quiz.objective_questions.all()  # Fetch associated questions

    context = {
        'quiz': quiz,
        'objective_questions': objective_questions,
    }
    return render(request, 'tutors_template/quizes/quiz_detail.html', context)

# View to handle adding objective questions
def add_objective_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        question_texts = request.POST.getlist('question[]')
        diagrams = request.FILES.getlist('diagram[]')

        # Use an atomic transaction
        with transaction.atomic():
            # Loop through each question
            for i in range(len(question_texts)):
                question_text = question_texts[i].strip()
                diagram = diagrams[i] if i < len(diagrams) else None  # Get the diagram if it exists for this question

                # Ensure the question text is not empty
                if question_text:
                    # Save the question to the database
                    objective_question = ObjectiveQuestion(quiz=quiz, question=question_text, diagram=diagram)
                    objective_question.save()

                    # Collect the options for this specific question
                    options = []
                    for j in range(5):  # We have 5 options: A, B, C, D, E
                        option_text = request.POST.getlist(f'option_text_{i}[]', [''])[j].strip()  # Get each option
                        if option_text:  # Make sure the option text is not empty
                            is_correct = request.POST.get(f'correct_option[{i}]', '') == 'ABCDE'[j]  # Check if this option is correct
                            options.append({
                                'text': option_text,
                                'value': 'ABCDE'[j],
                                'is_correct': is_correct
                            })

                    # Save each option in the database
                    for option in options:
                        ObjectiveOption.objects.create(
                            question=objective_question,
                            option_text=option['text'],
                            option_value=option['value'],
                            is_correct=option['is_correct']
                        )

        # Redirect after saving
        messages.success(request, "All questions saved successfully!")
        return redirect('tutor_question_view', quiz_id=quiz.id)

    # GET request: Show the form to add questions
    return render(request, 'tutors_template/quizes/add_objective.html', {'quiz': quiz})


#View to handle adding theory questions
def add_theory_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        question_numbers = request.POST.getlist('question_number[]')
        question_texts = request.POST.getlist('question[]')
        diagrams = request.FILES.getlist('diagram[]')
        answer_summaries = request.POST.getlist('answer_summary[]')

        for i in range(len(question_texts)):
            question_number = question_numbers[i].strip()
            question_text = question_texts[i].strip()
            diagram = diagrams[i] if i < len(diagrams) else None  # Ensure diagram exists if uploaded
            answer_summary = answer_summaries[i].strip()

            # Ensure the question text is not empty
            if question_text:
                # Save each theory question to the database
                TheoryQuestion.objects.create(
                    quiz=quiz,
                    question_number=question_number,
                    question=question_text,
                    diagram=diagram,
                    answer_summary=answer_summary
                )

        messages.success(request, "Theory questions added successfully!")
        return redirect('tutor_question_view', quiz_id=quiz.id)

    return render(request, 'tutors_template/quizes/add_theory.html', {'quiz': quiz})


# View to display the submitted theory questions
def question_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    theory_questions = quiz.theory_questions.all()
    questions = quiz.objective_questions.all()

    return render(request, 'tutors_template/quizes/question_view.html', {'quiz': quiz, 'questions': questions, 'theory_questions': theory_questions})




def schedule_students(request, schedule_id):
    # Get the quiz schedule based on the provided ID
    schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    # Get all results related to the schedule
    results = QuizResult.objects.filter(schedule=schedule)  # Fetch QuizResults for the given schedule

    # Extract students from results
    students = [result.student for result in results]

    context = {
        'schedule': schedule,
        'results': results,
        'students': students,
    }
    return render(request, 'tutors_template/quizes/schedule_students.html', context)

def result_details(request, schedule_id, student_id):
    schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    quiz = schedule.quiz
    
    # Fetch student answers for the quiz schedule
    student_answers = schedule.student_answers.filter(student=student_id)
    
    # Prepare objective question data
    objective_questions_data = []
    for question in quiz.objective_questions.all():
        options = question.options.all()
        selected_option = None
        is_correct = False

        # Check if there is an answer for this question
        if question in [answer.objective_question for answer in student_answers]:
            student_answer = student_answers.get(objective_question=question)
            selected_option = student_answer.selected_option.id if student_answer.selected_option else None
            is_correct = student_answer.is_correct

        objective_questions_data.append({
            'question_text': question.question,
            'diagram': question.diagram.url if question.diagram else None,
            'options': [
                {'id': option.id, 'text': option.option_text, 'value': option.option_value, 'is_correct': option.is_correct}
                for option in options
            ],
            'selected_option': selected_option,
            'is_correct': is_correct,
        })

    # Prepare theory question data
    theory_questions_data = []
    for theory_question in quiz.theory_questions.all():
        # Check if there is an answer for this theory question
        student_answer = student_answers.filter(theory_question=theory_question).first()
        
        theory_questions_data.append({
            'question_number': theory_question.question_number,
            'question_text': theory_question.question,
            'diagram': theory_question.diagram.url if theory_question.diagram else None,
            'theory_answer': student_answer.theory_answer if student_answer else "No answer provided",
            'answer_summary': theory_question.answer_summary or "No summary provided"
        })

    result = get_object_or_404(QuizResult, student=student_id, schedule=schedule)
    # Combine data into context
    context = {
        'quiz_title': quiz.title,
        'objective_questions': objective_questions_data,
        'theory_questions': theory_questions_data,
        'result':result
    }

    return render(request, 'tutors_template/quizes/student_cbt_result.html', context)


def tutor_cbt(request):
    form_subjects=Subjects.objects.filter(tutor=request.user.id)
    return render(request,"tutors_template/cbtest.html",{"form_subjects":form_subjects})



class AddQuizView(View):
    model = Quiz
    template_name = 'tutors_template/addquiz.html'
    def get(self, request):
        form_subjects=Subjects.objects.filter(tutor=request.user.id)
        quizes = []
        for subject in form_subjects:
            quiz = Quiz.objects.filter(subject=subject.id)
            quizes.extend(quiz)
        return render(request, self.template_name,{"QUIZ_CHOICES":QUIZ_CHOICES,"subjects":form_subjects, 'obj':quizes})

    def post(self, request):
        subject_id = request.POST.get('subject')
        name = request.POST.get('name')
        topic = request.POST.get('topic')
        number_of_questions = int(request.POST.get('number_of_questions'))
        time = int(request.POST.get('time'))
        required_score_to_pass = int(request.POST.get('required_score_to_pass'))
        quiz_type = request.POST.get('quiz_type')
        subject = Subjects.objects.get(pk=subject_id)

        quiz = Quiz.objects.create(
            subject=subject,
            name=name,
            topic=topic,
            number_of_questions=number_of_questions,
            time=time,
            required_score_to_pass=required_score_to_pass,
            quiz_type=quiz_type
        )
        messages.success(request,"Successfully Added")
        return HttpResponseRedirect(reverse("addquiz"))



def add_questions(request, quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    if request.method == 'POST':
        for i in range(quiz.number_of_questions):
            question_text = request.POST.get('question_{}'.format(i))
            correct_answer_text = request.POST.get('correct_answer_{}'.format(i))
            answer1_text = request.POST.get('answer_{}_1'.format(i))
            answer2_text = request.POST.get('answer_{}_2'.format(i))
            answer3_text = request.POST.get('answer_{}_3'.format(i))
            print(question_text)
            print(correct_answer_text)

            question = Question.objects.create(quiz=quiz, text=question_text)
            Answer.objects.create(question=question, text=correct_answer_text, correct=True)
            Answer.objects.create(question=question, text=answer1_text)
            Answer.objects.create(question=question, text=answer2_text)
            Answer.objects.create(question=question, text=answer3_text)

        return HttpResponse('Questions added to {}'.format(quiz.name))
    else:
        question_count = range(quiz.number_of_questions)

        questions = []
        for q in quiz.get_questions():
            answers = []
            for a in q.get_answers():
                answers.append(a.text)
            questions.append({str(q): answers})
        return render(request, 'tutors_template/add_questions.html', {'quiz': quiz, 'question_count': question_count,'questions':questions})
    # quiz = Quiz.objects.get(pk=quiz_id)
    # if request.method == 'POST':
    #     for i in range(1, quiz.number_of_questions + 1):
    #         text = request.POST.get(f'text_{i}')
    #         correct_answer_text = request.POST.get(f'correct_answer_{i}')
    #         wrong_answer_texts = [
    #             request.POST.get(f'wrong_answer_{j}_{i}')
    #             for j in range(1, 4)
    #         ]
    #         question = Question.objects.create(text=text, quiz=quiz)
    #         answers = [
    #             Answer(text=correct_answer_text, correct=True, question=question),
    #             Answer(text=wrong_answer_texts[0], correct=False, question=question),
    #             Answer(text=wrong_answer_texts[1], correct=False, question=question),
    #             Answer(text=wrong_answer_texts[2], correct=False, question=question),
    #         ]
    #         Answer.objects.bulk_create(answers)
    #     return redirect('quiz_detail', quiz_id=quiz.id)
    # else:
    #     no_question = range(quiz.number_of_questions)
    #     return render(request, 'tutors_template/add_questions.html', {'quiz': quiz,'no_question':no_question})


def edit_question(request, question_id):
    question = Question.objects.get(pk=question_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        question.text = text
        question.save()
        answers = question.get_answers()
        for answer in answers:
            answer_text = request.POST.get(f'answer_{answer.id}')
            is_correct = request.POST.get(f'correct_{answer.id}') == 'on'
            answer.text = answer_text
            answer.correct = is_correct
            answer.save()
        return redirect('quiz_detail', quiz_id=question.quiz.id)
    else:
        answers = question.get_answers()
        return render(request, 'edit_question.html', {'question': question, 'answers': answers})

class AddQuestionView(View):
    template_name = 'quizes/add_question.html'

    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(pk=quiz_id)
        return render(request, self.template_name, {'quiz': quiz})

    def post(self, request, quiz_id):
        quiz = Quiz.objects.get(pk=quiz_id)
        question_text = request.POST.get('question_text')
        question = Question.objects.create(
            text=question_text,
            quiz=quiz
        )
        for i in range(4):
            answer_text = request.POST.get(f'answer_{i}')
            is_correct = request.POST.get(f'answer_{i}_correct')
            if is_correct == 'on':
                is_correct = True
            else:
                is_correct = False
            answer = Answer.objects.create(
                text=answer_text,
                correct=is_correct,
                question=question
            )
        return redirect('quiz_detail', pk=quiz.pk)


