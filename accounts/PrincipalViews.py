import json
from django.contrib import messages
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from accounts.models import Attendance, AttendanceReport, Classes, ClassCategories, CombineEndTerm, CombineMidTerm, CombineSubjects, CustomUser, FeedBackStaff, EntryAttestation, FeedBackStudent, LeaveReport, LessionPlan, SessionYearModel, Staff, StudentApplication, StudentExitReport, Students, Subjects, Terms,SubjectsAllo, EndTerm, MidTerm,ClassAverage,AffectiveDomain,Psycomotor
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Sum
from django.template.defaultfilters import linebreaksbr
from hostel.models import Hostel, Rooms, Logbook, Allocations, StudentEthosRecords
from datetime import datetime

from publicsite.models import JobApp

@login_required
def principal_home(request):
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


    return render(request,"principal_template/principal_home.html",{"student_count":student_count,"staff_count":staff_count,"subject_count":subject_count,"class_count":class_count,"class_name_list":class_name_list,"subject_count_list":subject_count_list,"student_count_list_in_class":student_count_list_in_class,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"staff_name_list":staff_name_list,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student})

@login_required
def principal_view_subjects(request):
    subjects=Subjects.objects.all()
    subj = {subject: {'plan_count':0} for subject in subjects}
    for subje in subjects:
        ses = SessionYearModel.objects.get(status=1)
        term = Terms.objects.get(status=1)
        subj[subje]['plan_count'] = LessionPlan.objects.filter(subjects=subje,session_year=ses,term=term).count()
    return render(request,"principal_template/view_subjects.html",{"subjects":subj})

@csrf_exempt
def principal_view_students(request):
    
    if request.method!="POST":
        sessions=SessionYearModel.objects.all()
        classes=Classes.objects.all()
        return render(request,"principal_template/principal_view_students.html",{"sessions":sessions,"classes":classes})
    else:
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
                data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"gender":student.gender,"profile_pic":str(student.profile_pic),"dob":student.dob,"classes":student.class_id.name+" "+student.class_category.name,"parent_name":student.parent_name,"phone":student.parent_phone,"parent_email":student.parent_email}
                list_data.append(data_small)
            return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
        else:
            messages.Error(request,"No Records Found")

@login_required
def principal_view_staff(request):
    staffs=Staff.objects.filter(status=1)
    return render(request,"principal_template/view_all_staff.html",{"staffs":staffs})

@login_required
def principal_result_action(request):
    classes=Classes.objects.all()
    return render(request,"principal_template/principal_result_action.html",{"classes":classes})


@csrf_exempt
def principal_get_result(request):
    class_ids=request.POST.get("classid")
    if class_ids=='0':
        students=Students.objects.all()
    else:
        students=Students.objects.filter(class_id=class_ids)

    if students!=None:
        list_data=[]
        for student in students:
            data_small={"id":student.admin.id,"reg_id":student.admin.username,"name":student.admin.first_name+" "+student.admin.last_name,"profile_pic":str(student.profile_pic),"class_name":student.class_id.name}
            list_data.append(data_small)
            messages.success(request,"Success")
        return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)
    else:
        messages.Error(request,"No Records Found")

@login_required
def principal_leave(request):
    leave=LeaveReport.objects.all()
    return render(request,"principal_template/principal_leave_template.html",{"leaves":leave})

@login_required
def leave_approve(request,leave_id):
    leave=LeaveReport.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("principal_leave"))

@login_required
def leave_decline(request,leave_id):
    leave=LeaveReport.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("principal_leave"))


@login_required
def principal_feedback(request):
    feedback=FeedBackStaff.objects.all()    
    return render(request,"principal_template/principal_feedback_template.html",{"feedbacks":feedback})

@login_required
def principal_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("principal_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaff(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
             
            messages.success(request,"Feedback Successfully Sent")
            return HttpResponseRedirect(reverse("principal_feedback"))
        except:
            messages.error(request,"Failed To Send Feedback")
            return HttpResponseRedirect(reverse("principal_feedback"))

@login_required
def student_feedbacks(request):
    feedback=FeedBackStudent.objects.all()
    return render(request,"principal_template/student_feedback.html",{"feedbacks":feedback})

@login_required
def principal_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request,"principal_template/principal_profile.html",{"user":user})

@login_required
def edit_principal_profile(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("principal_profile"))
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
            return HttpResponseRedirect(reverse("principal_profile"))
        except:
            messages.error(request,"Failed To Update")
            return HttpResponseRedirect(reverse("principal_profile"))

@login_required
def student_applications(request):
    job=StudentApplication.objects.all()
    return render(request,"principal_template/student_applications.html",{'job':job})

@login_required
def job_applications(request):
    jobs=JobApp.objects.all()
    return render(request,"principal_template/job_applications.html",{"jobs":jobs})
    
@login_required
def lession_plan(request, subject_id):
    ses=SessionYearModel.objects.get(status=1)
    les_plan = LessionPlan.objects.filter(subjects=subject_id,session_year=ses)
    return render(request,"principal_template/lession_plans.html",{"les_plan":les_plan})




@login_required
def management_result(request):
    return render(request,"principal_template/action_result.html")

@login_required
def management_studentresults(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_class=Classes.objects.all()
    if request.method!="POST":
        return render(request,"principal_template/student_results.html",{"sessions":all_sessions,"all_terms":all_terms,"all_class":all_class})
    else:
        session_year = int(request.POST.get("sess"))
        term = int(request.POST.get("term"))
        res_type = int(request.POST.get("result_type"))
        reg_no = request.POST.get("stdID")
        std_id = CustomUser.objects.get(username=reg_no)
        class_cat=Students.objects.get(admin=std_id)
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
                return render(request,"principal_template/endterm_result_preview.html",{"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"endterm":endterms,"sessions":all_sessions,"all_terms":all_terms,"all_class":all_class})
            
            else:
                avg_id=ClassAverage.objects.get(students_id=class_cat,term=term,session_year=session_year,result_type=res_type)
                psychomotor=Psycomotor.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
                affective=AffectiveDomain.objects.get(student_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term,result_type=avg_id.result_type)
                midterm_result=MidTerm.objects.filter(students_id=avg_id.students_id,session_year=avg_id.session_year,term=avg_id.term)
                return render(request,"admin_template/student_results.html",{"avg_id":avg_id,"psycomotor":psychomotor,"affective":affective,"midterm":midterm_result,"sessions":all_sessions,"all_terms":all_terms,"all_class":all_class})
    
        except:
            messages.error(request,"ERROR!....Result not available")
            return HttpResponseRedirect(reverse("management_studentresults"))


@csrf_exempt
def management_subjectresults(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_subj=Subjects.objects.all()
    if request.method!="POST":
        return render(request,"principal_template/view_results.html",{"sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj})
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
            context={"subject":subject,"results":get_results,"json_data":json_data,"viewtype":viewtype,"restype":result_type,"sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj}
            return render(request,"principal_template/view_results.html",context)

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
            
            context={"subject":subject,"results":get_results,"json_data":json_data,"viewtype":viewtype,"restype":result_type,"sessions":all_sessions,"all_terms":all_terms,"all_subj":all_subj}           
            return render(request,"principal_template/view_results.html",context)

   

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
 
def thebroadsheet_analysis(request):
    all_sessions=SessionYearModel.objects.all()
    all_terms=Terms.objects.all()
    all_cat=ClassCategories.objects.all().order_by('class_id__name')
    if request.method!="POST":
        return render(request,"principal_template/broadsheet_template.html",{"all_sessions":all_sessions,"all_terms":all_terms,"all_cat":all_cat})
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
            return render(request, 'principal_template/broadsheet_template.html', context) 
        
        elif result_type==2:
            # Prepare JSON data
            json_data = []
            for student in students:
                # Retrieve midterms for the student
                endterms = EndTerm.objects.filter(students_id=student,session_year=sess_year,term=term)
                
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
            return render(request, 'principal_template/broadsheet_template.html', context) 
    
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

    return render(request, 'principal_template/hostel_dashboard.html', context)
    
    
    
