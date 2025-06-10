
import json
from django.contrib import messages
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from accounts.models import AffectiveDomain, Attendance, AttendanceReport, ClassAverage, ClassCategories, Classes, CustomUser, EndTerm, FeedBackStudent, GncQuestion, GncResponse, MidTerm, NotificationStudent, OldCummulative, OldResults, Psycomotor, SessionYearModel, StudentAccount, StudentExitReport, Students, StudyMaterial, SubjectStream, Subjects, Terms
from hostel.models import StudentEthosRecords
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import datetime
from accounts.forms import GncResponseForm
from django.forms import modelformset_factory
from django.db import IntegrityError
from onlinecbt.models import ObjectiveQuestion, Quiz, QuizResult, QuizSchedule, StudentAnswer, StudentProgress, TheoryQuestion

from paystackpayments import forms
from paystackpayments.models import Payment

#vid 20
@login_required
def students_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    subjects=Subjects.objects.filter(class_category=student_obj.class_category, class_id=student_obj.class_id).count()
    term=Terms.objects.get(status=1)
    session_year=SessionYearModel.objects.get(status=1)

    subject_name=[]
    data_present=[]
    data_absent=[]
    subjects_data=Subjects.objects.filter(class_id=student_obj.class_id)
    for subject in subjects_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        atd_report=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=student_obj.id)
        attendance_present_count=atd_report.filter(status=True,).count()
        attendance_absent_count=atd_report.filter(status=False,).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    return render(request,"students_template/home_template.html",{"term":term,"session_year":session_year,"student_obj":student_obj,"total_attendance":attendance_present+attendance_absent,"attendance_present":attendance_present,"attendance_absent":attendance_absent,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent})

@login_required
def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    classes=Classes.objects.get(id=student.class_id.id)
    subjects=Subjects.objects.filter(class_id=classes)
    return render(request,"students_template/student_view_attendance.html",{"subjects":subjects})

@login_required
def student_subjects(request):
    student=Students.objects.get(admin=request.user.id)
    student_subjects=Subjects.objects.filter(class_id=student.class_id)
    return render(request,"students_template/student_subjects.html",{"student_subjects":student_subjects})

@login_required
def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")

    start_date_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_date_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subjects.objects.get(id=subject_id)
    user_object=CustomUser.objects.get(id=request.user.id)
    stud_obj=Students.objects.get(admin=user_object)

    attendance=Attendance.objects.filter(attendance_date__range=(start_date_parse,end_date_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)

    return render(request,"students_template/student_attendance_data.html",{"attendance_reports":attendance_reports})
    
@login_required
def student_leave(request):
    student_obj=Students.objects.get(admin=request.user.id)
    leave_data=StudentExitReport.objects.filter(student_id=student_obj)
    return render(request,"students_template/student_leave_template.html",{"leave_data":leave_data})

@login_required
def student_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_reason")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            leave_report=StudentExitReport(student_id=student_obj,leave_messagee=leave_msg,leave_date=leave_date,leave_status=0)
            leave_report.save()
             
            messages.success(request,"Application Successfully Submitted")
            return HttpResponseRedirect(reverse("student_leave"))
        except:
            messages.error(request,"Failed Submit Application")
            return HttpResponseRedirect(reverse("student_leave"))


@login_required
def student_feedback(request):
    student_id=Students.objects.get(admin=request.user.id)
    feedback_data=FeedBackStudent.objects.filter(student_id=student_id)
    return render(request,"students_template/student_feedback_template.html",{"feedback_data":feedback_data})

@login_required
def student_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStudent(student_id=student_obj,feedback=feedback_msg,Feedback_reply="")
            feedback.save()
             
            messages.success(request,"Feedback Successfully Sent")
            return HttpResponseRedirect(reverse("student_feedback"))
        except:
            messages.error(request,"Failed To Send Feedback")
            return HttpResponseRedirect(reverse("student_feedback"))

@login_required
def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    return render(request,"students_template/student_profile.html",{"user":user,"student":student})

@login_required
def student_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        address=request.POST.get("address")
        password=request.POST.get("password")

        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            if password!=None and password!="":
                customuser.set_password(password)
                customuser.save()
                student=Students.objects.get(admin=customuser.id)
                student.address=address
                student.save()
                messages.success(request,"Profile Successfully Updated")
                return HttpResponseRedirect(reverse("login"))
            else:
                student=Students.objects.get(admin=customuser.id)
                student.address=address
                student.save()
                messages.success(request,"Profile Successfully Updated")
                return HttpResponseRedirect(reverse("student_profile"))

        except:
            messages.error(request,"Failed To Update")
            return HttpResponseRedirect(reverse("student_profile"))

@login_required
def my_result_action(request,):
    return render(request,"students_template/my_result_action.html")
   
@login_required    
def my_results(request,res_type):
    
    student_id=Students.objects.get(admin=request.user.id)
    valid_ses_obj=ClassAverage.objects.filter(students_id=student_id, status=1)
    session_years=SessionYearModel.objects.all()
    old_res=OldResults.objects.filter(students=student_id)

    if res_type=="endterm":
        theader="End of Term Results"
        valid_old=[]
        for session in session_years:
            checks = old_res.filter(session_year=session,result_type=2)
            if checks:
                valid_old.append(checks)
        valid_ses=[]
        for session in session_years:
            checks=valid_ses_obj.filter(session_year=session,result_type=2)
            if checks:
                valid_ses.append(checks )

        return render(request,"students_template/student_my_results.html",{"valid_old":valid_old,"valid_ses":valid_ses,"theader":theader})

    elif res_type=="midterm":
        theader="Mid-Term Results"
        valid_old=[]
        for session in session_years:
            checks = old_res.filter(session_year=session,result_type=1)
            if checks:
                valid_old.append(checks)
        valid_ses=[]
        for session in session_years:
            checks=valid_ses_obj.filter(session_year=session,result_type=1)
            if checks:
                valid_ses.append(checks )
        
        return render(request,"students_template/student_my_results.html",{"valid_old":valid_old,"valid_ses":valid_ses,"theader":theader})

    else:
        return render(request,"students_template/my_result_action.html")



@login_required
def result_preview(request,res_id):
    avg_id=ClassAverage.objects.get(id=res_id)
    psychomotor=Psycomotor.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
    affective=AffectiveDomain.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)

    #student ethos
    re_type = avg_id.result_type-1
    ethos_records = StudentEthosRecords.objects.filter(term=avg_id.term, session_year=avg_id.session_year, result_type=re_type, student_id=avg_id.students_id)
    for record in ethos_records:
        positive_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('leadership', 'neatness', 'room_represent_compet', 'room_represent_inspect', 'selfconfidence', 'team_spirit', 'return_lost_items', 'obidience_to_staff', 'obidience_to_rules', 'volunteerism', 'reporting_unacceptable_behavior', 'prayerfullness'))])
        negative_ethos_sum = sum([getattr(record, field.name) for field in record._meta.fields if field.name.startswith(('loitering', 'immoral_relation_conduct', 'poor_timing', 'negative_influence', 'noise_making', 'hostel_disobidience', 'bullying_fighting', 'negative_civil', 'gossip', 'avoiding_meals', 'carelessness_personal'))])
        record.total_positive_ethos = positive_ethos_sum
        record.total_negative_ethos = negative_ethos_sum
        record.total_ethos = positive_ethos_sum - negative_ethos_sum
    if avg_id.result_type == 1:
        midterm_result=MidTerm.objects.filter(students_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term)
        return render(request,"students_template/midterm_result_preview.html",{"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"midterm":midterm_result,"ethos_records":ethos_records})

    elif avg_id.result_type == 2:
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
        return render(request,"students_template/endterm_result_preview.html",{"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"endterm":endterms,"ethos_records":ethos_records})
    else:
        return HttpResponseRedirect(reverse("my_results"))



@csrf_exempt
def student_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        student=Students.objects.get(admin=request.user.id)
        student.fcm_token=token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@login_required
def student_all_notification(request):
    student=Students.objects.get(admin=request.user.id)
    notification=NotificationStudent.objects.filter(student_id=student.id)
    
    return render(request,"students_template/student_notifcations.html",{"notifications":notification})

@login_required
def online_classes(request):
    return render(request,"students_template/online_class.html")

@login_required
def e_library(request):
    classs=Classes.objects.all()
    subject=Subjects.objects.all()

    return render(request,"students_template/e_library.html",{"classes":classs,"subjects":subject})

@login_required
def student_faq(request):
    return render(request,"students_template/student_faq.html")


@login_required
def tuition_preview(request):
    try:
        acc = StudentAccount.objects.get(students=request.user.id)
        students=Students.objects.get(admin=request.user.id)
        pay_history=Payment.objects.filter(reg_no=students.admin.username)
        payment_form=forms.PaymentForm()
        payment_form.fields['fullName'].initial=students.admin.first_name
        payment_form.fields['reg_no'].initial=students.admin.username
        payment_form.fields['email'].initial=students.admin.email

        return render(request,"students_template/tuition_template.html",{"acc":acc,'payment_form':payment_form,"pay_history":pay_history})
    except:
        messages.error(request,"No payment records found, if you consider this an error please contact the school admin.")
        return render(request,"students_template/tuition_template.html")

@login_required
def inter_records(request):
    student=Students.objects.get(admin=request.user.id)
    questions = GncQuestion.objects.all().order_by('form_type')
    GncResponseFormSet = modelformset_factory(GncResponse, form=GncResponseForm, extra=len(questions))
    
    form_types = [chr(i) for i in range(ord('A'), ord('J') + 1)]

    if request.method!="POST":
        initial_data = [{'question': question.id, 'form_type': question.form_type} for question in questions]
        formset = GncResponseFormSet(queryset=GncResponse.objects.none(), initial=initial_data)

        try:
            pdffile = OldCummulative.objects.get(students__admin=request.user)
            streamexist = SubjectStream.objects.filter(students__admin=request.user).count()
            return render(request,"students_template/inter_records.html",{"pdffile":pdffile,"streamexist":streamexist,'formset': formset,  'questions': questions, 'form_types':form_types})
        except:
            streamexist = SubjectStream.objects.filter(students__admin=request.user).count()
            return render(request,"students_template/inter_records.html",{"streamexist":streamexist,'formset': formset,  'questions': questions, 'form_types':form_types})
    else:
        subj_choice = request.POST.getlist('subj_coice')
        choice = request.POST.get('choice')
        career1 = request.POST.get('career1')
        career2 = request.POST.get('career2')
        career3 = request.POST.get('career3')
        reason1 = request.POST.get('reason1')
        passsubj1 = request.POST.get('passsubj1')
        passsubj2 = request.POST.get('passsubj2')
        passsubj3 = request.POST.get('passsubj3')
        passsubj4 = request.POST.get('passsubj4')
        passsubj5 = request.POST.get('passsubj5')
        passsubj6 = request.POST.get('passsubj6')
        failsubj1 = request.POST.get('failsubj1')
        failsubj2 = request.POST.get('failsubj2')
        failsubj3 = request.POST.get('failsubj3')
        failsubj4 = request.POST.get('failsubj4')
        failsubj5 = request.POST.get('failsubj5')
        failsubj6 = request.POST.get('failsubj6')
        pcareer = request.POST.get('pcareer')
        preason = request.POST.get('preason')
        pname = request.POST.get('pname')
        email = request.POST.get('email')
        parentcode = request.POST.get('parentcode')

        admin_user = request.user
        student = Students.objects.get(admin=admin_user)
        # Create a new Student object
        student = SubjectStream.objects.create(
            students=student,
            choice=choice,
            subj_choice=subj_choice,
            career1=career1,
            career2=career2,
            career3=career3,
            reason1=reason1,
            passsubj1=passsubj1,
            passsubj2=passsubj2,
            passsubj3=passsubj3,
            passsubj4=passsubj4,
            passsubj5=passsubj5,
            passsubj6=passsubj6,
            failsubj1=failsubj1,
            failsubj2=failsubj2,
            failsubj3=failsubj3,
            failsubj4=failsubj4,
            failsubj5=failsubj5,
            failsubj6=failsubj6,
            pcareer=pcareer,
            preason=preason,
            pname=pname,
            email=email,
            parentcode=parentcode
        )
        messages.success(request,"Subject Streaming Form Successfully Subitted")
        return HttpResponseRedirect(reverse("inter_records"))

@login_required
def saveinterests(request):
    student=Students.objects.get(admin=request.user.id)
    questions = GncQuestion.objects.all()
    GncResponseFormSet = modelformset_factory(GncResponse, form=GncResponseForm, extra=len(questions))
    
    if request.method == 'POST':
        formset = GncResponseFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.student = student
                instance.answer_text = GncQuestion.OPTIONS[int(instance.answer_choice)]
                try:
                    instance.save()
                    messages.success(request,"Inventory Successfully Saved")
                except IntegrityError:
                    messages.error(request, "Inventory Failed to Save: Entry already exists")
            return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or homepage if referer not found
    else:
        messages.error(request,"Inventory Failed to Saved")
        return redirect(request.META.get('HTTP_REFERER', '/'))

def student_assignments(request):
    student = Students.objects.get(admin=request.user.id)
    assignments = StudyMaterial.objects.filter(material_type="assignment", status=True, subject__class_id=student.class_id)
    return render(request, 'students_template/student_assignments.html', {'materials': assignments})

def student_notes(request):
    student = Students.objects.get(admin=request.user.id)
    notes = StudyMaterial.objects.filter(material_type="note", status=True, subject__class_id=student.class_id)
    return render(request, 'students_template/student_notes.html', {'materials': notes})

def student_textbooks(request):
    student = Students.objects.get(admin=request.user.id)
    textbooks = StudyMaterial.objects.filter(material_type="textbook", status=True, subject__class_id=student.class_id)
    return render(request, 'students_template/student_textbooks.html', {'materials': textbooks})

def view_textbook(request, material_id):
    textbook = get_object_or_404(StudyMaterial, id=material_id, material_type="textbook")
    return render(request, 'students_template/view_textbook.html', {'textbook': textbook})
        
        
#-----------------CBT--------------------------#
def cbt_view(request):
    # Get the current logged-in user
    user = request.user
    
    # Get the student associated with this user (assuming there is one)
    try:
        student = Students.objects.get(admin=user)
    except Students.DoesNotExist:
        student = None
    
    if student:
        # Get the class category of the student
        student_class = student.class_id
        
        # Filter QuizSchedule where the subject's class category matches the student's class category
        schedules = QuizSchedule.objects.filter(
            quiz__subject__class_id=student_class,
            status__in=['ongoing', 'result']
        )
        print(schedules)
    else:
        schedules = []

    # Render the template and pass the filtered schedules
    return render(request, "students_template/quizes/cbt_subjects.html", {"schedules": schedules})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def quiz_view(request, schedule_id):
    student = request.user
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)

    # Fetch or create student progress
    progress, created = StudentProgress.objects.get_or_create(student=student, schedule=quiz_schedule)

    # Check if the quiz has already been submitted
    result = QuizResult.objects.filter(student=student, schedule=quiz_schedule).first()
    if result:
        return redirect('cbt_theory', schedule_id=schedule_id)

    # Check if current time is before the quiz start time
    current_time = timezone.now()
    start_time = quiz_schedule.start_time

    # If current time is earlier than start time, display countdown to start time
    if current_time < start_time:
        time_until_start = (start_time - current_time).total_seconds()  # Calculate time in seconds
        return render(request, 'students_template/quizes/quiz_countdown.html', {
            'schedule': quiz_schedule,
            'time_until_start': time_until_start
        })

     # Quiz has started, proceed with loading the questions
    objective_questions = ObjectiveQuestion.objects.filter(quiz=quiz_schedule.quiz).order_by('id')

    # Get answered questions
    answered_questions = StudentAnswer.objects.filter(student=student, schedule=quiz_schedule)

    # Annotate objective questions with selected options
    for question in objective_questions:
        selected_answer = answered_questions.filter(objective_question=question).first()
        question.selected_option = selected_answer.selected_option if selected_answer else None


    
    # Calculate remaining time based on the quiz duration
    elapsed_time = (current_time - start_time).total_seconds()
    duration_in_seconds = quiz_schedule.duration * 60 
    time_remaining = max(0, duration_in_seconds - elapsed_time)

    # Redirect to submission if time has already elapsed
    if time_remaining <= 0:
        return redirect('submit_quiz', schedule_id=schedule_id)

    return render(request, 'students_template/quizes/quiz_ongoing.html', {
        'schedule': quiz_schedule,
        'objective_questions': objective_questions,
        'progress': progress,
        'time_remaining': time_remaining,  # Send remaining time in seconds
    })
    
def save_answer(request, schedule_id):
    student = request.user
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    question_id = request.POST.get('question_id')
    
    try:
        with transaction.atomic():
            # Save answer based on question type
            question = get_object_or_404(ObjectiveQuestion, id=question_id)
            selected_option_id = request.POST.get('selected_option')
            selected_option = question.options.get(id=selected_option_id)

            # Save the student's answer
            student_answer, created = StudentAnswer.objects.update_or_create(
                student=student, 
                schedule=quiz_schedule, 
                objective_question=question,
                defaults={
                    'selected_option': selected_option, 
                    'is_correct': selected_option.is_correct, 
                    'is_submitted': True, 
                    'submitted_at': timezone.now()
                }
            )

            # Update or create StudentProgress entry
            current_question_number = question.id  # Get current question number from POST data
            student_progress, _ = StudentProgress.objects.update_or_create(
                student=student, 
                schedule=quiz_schedule,
                defaults={
                    'current_question_number': current_question_number,  # Update current question number
                    'time_remaining': timezone.timedelta(seconds=60 * 15)  # Assuming 15 minutes time remaining; adjust as needed
                }
            )

            return JsonResponse({'status': 'success', 'message': 'Answer saved successfully'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def theory_view(request, schedule_id):
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    student = request.user

    # Check if the quiz schedule time has expired
    current_time = timezone.now()
    start_time = quiz_schedule.start_time
    # Calculate remaining time based on the quiz duration
    elapsed_time = (current_time - start_time).total_seconds()
    duration_in_seconds = quiz_schedule.duration * 60 
    time_remaining = max(0, duration_in_seconds - elapsed_time)
    
    # If time has expired, redirect to result page
    if time_remaining <= 0:
        return redirect('quiz_complete', schedule_id=schedule_id)

    # Check if all answers for the student are submitted
    theory_questions = TheoryQuestion.objects.filter(quiz=quiz_schedule.quiz).first()
    student_answers = StudentAnswer.objects.filter(student=student, schedule=quiz_schedule, theory_question=theory_questions)
    
    # Get all theory questions for the quiz
    theory_questions = TheoryQuestion.objects.filter(quiz=quiz_schedule.quiz)

    # Get all student answers for the theory questions in the current schedule
    student_answers = StudentAnswer.objects.filter(student=student, schedule=quiz_schedule, theory_question__in=theory_questions)

    # If there are no answers yet, allow the student to proceed
    if not student_answers.exists():
        pass  # Proceed with the quiz

    else:
        # Check if there are any unanswered theory questions
        if student_answers.filter(is_submitted=False).exists() or student_answers.count() < theory_questions.count():
            pass  # Proceed with the quiz, as not all answers are submitted
        else:
            # All answers are submitted
            return redirect('quiz_complete', schedule_id=schedule_id)

    if request.method == 'POST':
        if 'submit' in request.POST:
            try:
                # Mark quiz as submitted for all answers of this student for the given schedule
                StudentAnswer.objects.filter(student=student, schedule=quiz_schedule).update(
                    is_submitted=True, submitted_at=timezone.now()
                )
                return JsonResponse({'status': 'success', 'message': 'Quiz submitted!'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

        theory_question_id = request.POST.get('theory_question_id')
        theory_answer = request.POST.get('theory_answer')
        student = request.user

        try:
            with transaction.atomic():
                # Get the theory question
                theory_question = get_object_or_404(TheoryQuestion, id=theory_question_id)

                # Create or update the StudentAnswer instance
                student_answer, created = StudentAnswer.objects.update_or_create(
                    student=student,
                    schedule=quiz_schedule,
                    theory_question=theory_question,
                    defaults={
                        'theory_answer': theory_answer,
                        'is_submitted': True,
                        'submitted_at': timezone.now()
                    }
                )

                return JsonResponse({'status': 'success', 'message': 'Answer saved successfully.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    theory_questions = TheoryQuestion.objects.filter(quiz=quiz_schedule.quiz).order_by('question_number')
    
    return render(request, 'students_template/quizes/theory_questions.html', {
        'schedule': quiz_schedule,
        'theory_questions': theory_questions,
        'time_remaining': time_remaining
    })


def submit_quiz(request, schedule_id):
    student = request.user
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)

    try:
        # Check if there's a theory question for the quiz related to the schedule
        has_theory = TheoryQuestion.objects.filter(quiz=quiz_schedule.quiz).exists()
        # Calculate or retrieve the result
        result, created = QuizResult.objects.get_or_create(student=student, schedule=quiz_schedule)
        result.calculate_score()  # Calculate and save the score

        # Determine the response code based on the presence of theory questions
        code = 'theory' if has_theory else 'complete'
                
        return JsonResponse({'status': 'success', 'message': 'Answer saved successfully', 'code': code})

    except Exception as e:
        # Log the error if needed, e.g., using Django's logging framework
        print(f"Error saving result: {e}")
        return JsonResponse({'status': 'failure', 'message': e, 'code': 'errory'})
    
def handle_timeout(request, schedule_id):
    # Called via AJAX if the quiz time runs out
    return submit_quiz(request, schedule_id)

def quiz_complete(request, schedule_id):
    student = request.user
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)

    return render(request, 'students_template/quizes/cbt_complete.html', {'quiz_schedule': quiz_schedule})



def quiz_result_view(request, schedule_id):
    schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    quiz = schedule.quiz
    
    # Fetch student answers for the quiz schedule
    student_answers = schedule.student_answers.filter(student=request.user)
    
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

    result = get_object_or_404(QuizResult, student=request.user, schedule=schedule)
    # Combine data into context
    context = {
        'quiz_title': quiz.title,
        'objective_questions': objective_questions_data,
        'theory_questions': theory_questions_data,
        'result':result
    }

    return render(request, 'students_template/quizes/quiz_result.html', context)
        
