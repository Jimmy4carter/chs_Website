"""chs_Website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from os import name
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from accounts import  ManagementViews, AdminsecViews, PrincipalViews, TuckshopViews, TutorViews, StudentViews, views, AdminViews

from accounts import  ManagementViews, AdminsecViews, PrincipalViews, TutorViews, StudentViews, views, AdminViews

import accounts
from publicsite import PublicViews
from hostel import HostelViews
from chs_Website import settings

urlpatterns = [
    #public URLs
    path('',PublicViews.ShowHomePage,name="index"),
    path('about_us',PublicViews.about_us,name="about_us"),
    path('our_programs',PublicViews.our_programs,name="our_programs"),
    path('school_facilities',PublicViews.school_facilities,name="school_facilities"),
    path('our_gallery',PublicViews.our_gallery,name="our_gallery"),
    path('our_team',PublicViews.our_team,name="our_team"),
    path('our_events',PublicViews.our_events,name="our_events"),
    path('contact_us',PublicViews.contact_us,name="contact_us"),
    path('apply_action',PublicViews.apply_action,name="apply_action"),
    path('apply_job',PublicViews.apply_job,name="apply_job"),
    path('apply',PublicViews.apply,name="apply"),
    path('apply_success',PublicViews.apply_success,name="apply_success"),
    path('application_notice',PublicViews.application_notice,name="application_notice"),
    path('faqs',PublicViews.faqs,name="faqs"),
    path('jambcbt',PublicViews.jambcbt,name="jambcbt"),

    #generic URLs
    path('demo',views.ShowDemoPage,name=""),
    path('accounts/',include('django.contrib.auth.urls')),
    path('login',views.ShowLoginPage,name="login"),
    path('get_user_details',views.GetUserDetails,name="get_user_details"),
    path('logout_user',views.logout_user,name="logout"),
    path('doLogin',views.doLogin,name="doLogin"),
    path('new_subcriber',views.new_subcriber,name="new_subcriber"),


    #Admin URLs
    path('admin/', admin.site.urls),
    path('admin_home',AdminViews.admin_home,name="admin_home"),

    path('cbtentry',AdminViews.cbtentry,name="cbtentry"),

    path('class_result',AdminViews.viewclass_result,name="class_result"),


    #staff Actions
    path('staff_action',AdminViews.staff_action,name="staff_action"),
    path('add_staff',AdminViews.add_staff,name="add_staff"),
    path('add_staff_save',AdminViews.add_staff_save,name="add_staff_save"),
    path('manage_staff',AdminViews.manage_staff,name="manage_staff"),
    path('edit_staff/<str:staff_id>',AdminViews.edit_staff,name="edit_staff"),
    path('edit_staff_save',AdminViews.edit_staff_save,name="edit_staff_save"),
    path('view_staffs',AdminViews.view_staffs,name="view_staffs"),

    #Classes Actions
    path('add_classes',AdminViews.add_classes,name="add_classes"),
    path('add_class_save',AdminViews.add_class_save,name="add_class_save"),
    path('manage_classes',AdminViews.manage_classes,name="manage_classes"),
    path('edit_class/<str:class_id>',AdminViews.edit_class,name="edit_class"),
    path('edit_class_save',AdminViews.edit_class_save,name="edit_class_save"),
    path('view_classes',AdminViews.view_classes,name="view_classes"),

    #Subjects Actions
    path('add_subjects',AdminViews.add_subjects,name="add_subjects"),
    path('add_combinesubject',AdminViews.add_combinesubject,name="add_combinesubject"),
    path('add_subject_save',AdminViews.add_subject_save,name="add_subject_save"),
    path('manage_subjects',AdminViews.manage_subjects,name="manage_subjects"),
    path('edit_combinesub/<str:subject_id>',AdminViews.edit_combinesub,name="edit_combinesub"),
    path('edit_subjects/<str:subject_id>',AdminViews.edit_subjects,name="edit_subjects"),
    path('edit_save_comb',AdminViews.edit_save_comb,name="edit_save_comb"),
    path('edit_subject_save',AdminViews.edit_subject_save,name="edit_subject_save"),
    path('view_subjects',AdminViews.view_subjects,name="view_subjects"),

    #Student Actions
    path('add_students',AdminViews.add_students,name="add_students"),
    path('add_students_save',AdminViews.add_students_save,name="add_students_save"),
    path('manage_students',AdminViews.manage_students,name="manage_students"),
    path('edit_student/<str:students_id>',AdminViews.edit_student,name="edit_student"),
    path('edit_student_save',AdminViews.edit_student_save,name="edit_student_save"),
    path('view_students',AdminViews.view_students,name="view_students"),
    path('query_view_students',AdminViews.query_view_students,name="query_view_students"),

    #Session Actions
    path('manage_session',AdminViews.manage_session,name="manage_session"),
    path('add_session_save',AdminViews.add_session_save,name="add_session_save"),
    path('check_email_exist',AdminViews.check_email_exist,name="check_email_exist"),
    path('check_username_exist',AdminViews.check_username_exist,name="check_username_exist"),
    path('check_username_exis',HostelViews.check_username_exis,name="check_username_exis"),

    #Feedback Actions
    path('student_feedback_message',AdminViews.student_feedback_message,name="student_feedback_message"),
    path('student_feedback_message_replied',AdminViews.student_feedback_message_replied,name="student_feedback_message_replied"),
    path('staff_feedback_message',AdminViews.staff_feedback_message,name="staff_feedback_message"),
    path('staff_feedback_message_replied',AdminViews.staff_feedback_message_replied,name="staff_feedback_message_replied"),

    #Leave/Exit Actions
    path('student_exit_view',AdminViews.student_exit_view,name="student_exit_view"),
    path('student_exit_approve/<str:leave_id>',AdminViews.student_exit_approve,name="student_exit_approve"),
    path('student_exit_decline/<str:leave_id>',AdminViews.student_exit_decline,name="student_exit_decline"),
    path('staff_leave_view',AdminViews.staff_leave_view,name="staff_leave_view"),
    path('staff_leave_approve/<str:leave_id>',AdminViews.staff_leave_approve,name="staff_leave_approve"),
    path('staff_leave_decline/<str:leave_id>',AdminViews.staff_leave_decline,name="staff_leave_decline"),

    #Attendance Actions
    path('admin_view_attendance',AdminViews.admin_view_attendance,name="admin_view_attendance"),
    path('admin_get_attendance_date',AdminViews.admin_get_attendance_date,name="admin_get_attendance_date"),
    path('admin_get_attendance_student',AdminViews.admin_get_attendance_student,name="admin_get_attendance_student"),

    #Profle Actions
    path('admin_profile',AdminViews.admin_profile,name="admin_profile"),
    path('edit_profile_save',AdminViews.edit_profile_save,name="edit_profile_save"),

    #Notification Actions
    path('admin_send_notification_staff',AdminViews.admin_send_notification_staff,name="admin_send_notification_staff"),
    path('admin_send_notification_student',AdminViews.admin_send_notification_student,name="admin_send_notification_student"),
    path('send_student_notification',AdminViews.send_student_notification,name="send_student_notification"),
    path('send_staff_notification',AdminViews.send_staff_notification,name="send_staff_notification"),

    #calener Actions
    path('calender_activities',AdminViews.calender_activities,name="calender_activities"),
    path('activate_term',AdminViews.activate_term,name="activate_term"),
    path('activate_session',AdminViews.activate_session,name="activate_session"),
    path('site_controls',AdminViews.site_controls,name="site_controls"),
    path("update_status/", AdminViews.update_status, name="update_status"),
    

    #actions
    path('subject_action',AdminViews.subject_action,name="subject_action"),
    path('class_action',AdminViews.class_action,name="class_action"),
    path('library_action',AdminViews.library_action,name="library_action"),
    path('student_action',AdminViews.student_action,name="student_action"),
    path('online_class_action',AdminViews.online_class_action,name="online_class_action"),
    path('sessional_promotion',AdminViews.sessional_promotion,name="sessional_promotion"),
    
    path('promote_class_action',AdminViews.promote_class_action,name="promote_class_action"),
    path('get_students_promote',AdminViews.get_students_promote,name="get_students_promote"),
    path('promote_class',AdminViews.promote_class,name="promote_class"),
    path('promote_student_action',AdminViews.promote_student_action,name="promote_student_action"),
    path('promote_student',AdminViews.promote_student,name="promote_student"),
    path('remove_student_action',AdminViews.remove_student_action,name="remove_student_action"),
    path('remove_student',AdminViews.remove_student,name="remove_student"),
    
    path('add-material/', AdminViews.add_material, name='add_material'),
    path('materials/', AdminViews.materials_list, name='materials_list'),
    path('materials/update/<int:material_id>/', AdminViews.update_material, name='update_material'),
    path('materials/delete/<int:material_id>/', AdminViews.delete_material, name='delete_material'),
    
    path('exam-files/', AdminViews.exam_files_view, name='exam_files'),
    path('exam-files/add/', AdminViews.add_exam_file, name='add_exam_file'),
    path('exam-files/update/<int:file_id>/', AdminViews.update_exam_status, name='update_exam_status'),
    path('exam-files/delete/<int:file_id>/', AdminViews.delete_exam_file, name='delete_exam_file'),
    

    #old results
    path('old_results',AdminViews.old_results,name="old_results"),
    path('my_result_action',StudentViews.my_result_action,name="my_result_action"),
    path('old_cumm',AdminViews.old_cumm,name="old_cumm"),
    
    # ----CBT-----
    path('chsadmin/cbt/', AdminViews.admin_cbt, name='admin_cbt'),
    path('chsadmin/quiz/<int:quiz_id>/', AdminViews.admin_view_quiz, name='admin_view_quiz'),
    path('chsadmin/quiz/<int:quiz_id>/delete/', AdminViews.admin_delete_quiz, name='admin_delete_quiz'),
    path('chsadmin/schedule/<int:schedule_id>/delete/', AdminViews.admin_delete_schedule, name='admin_delete_schedule'),
    path('chsadmin/question/objective/<int:question_id>/delete/', AdminViews.admin_delete_objective_question, name='admin_delete_objective_question'),
    path('chsadmin/question/theory/<int:question_id>/delete/', AdminViews.admin_delete_theory_question, name='admin_delete_theory_question'),
    
    
    # new result
    path('action_result',AdminViews.action_result,name="action_result"),
    path('student_results',AdminViews.student_results,name="student_results"),
    path('broadsheet_analysis',AdminViews.broadsheet_analysis,name="broadsheet_analysis"),
    path('admin_results',AdminViews.admin_results,name="admin_results"),
    
    path('combmid_save', AdminViews.combmid_save, name='combmid_save'),
    path('combend_save', AdminViews.combend_save, name='combend_save'),
    
    path('domainviews', AdminViews.domainviews, name='domainviews'),


    #hostel
    path('hostel_home',HostelViews.hostel_home,name="hostel_home"),
    path('hostel_student',HostelViews.hostel_student,name="hostel_student"),
    path('hostel_profile',HostelViews.hostel_profile,name="hostel_profile"),
    path('manage_hostels',AdminViews.manage_hostels,name="manage_hostels"),
    path('hostels_manage',HostelViews.hostels_manage,name="hostels_manage"),
    path('manage_rooms',AdminViews.manage_rooms,name="manage_rooms"),
    path('rooms_manage',HostelViews.rooms_manage,name="rooms_manage"),
    path('hostel_all_notification',HostelViews.hostel_all_notification,name="hostel_all_notification"),
    path('hostel_feedback',HostelViews.hostel_feedback,name="hostel_feedback"),
    path('allocate_room',HostelViews.allocate_room,name="allocate_room"),
    path('get_rooms',HostelViews.get_rooms,name="get_rooms"),
    path('create_log',HostelViews.create_log,name="create_log"),
    path('view_logs',HostelViews.view_logs,name="view_logs"),
    path('report_preview/<str:report_id>',HostelViews.report_preview,name="report_preview"),
    path('delete_room/<str:item_id>',HostelViews.delete_room,name="delete_room"),
    path('hostel_analytics',AdminViews.hostel_analytics,name="hostel_analytics"),
    path('hostel_grading',HostelViews.hostel_grading,name="hostel_grading"),
    


    #old results
    path('admin_results',AdminViews.admin_results,name="admin_results"),
    path('old_results',AdminViews.old_results,name="old_results"),
    path('my_result_action',StudentViews.my_result_action,name="my_result_action"),
    
    #hostel
    path('hostel_home',HostelViews.hostel_home,name="hostel_home"),
    path('hostel_profile',HostelViews.hostel_profile,name="hostel_profile"),
    path('manage_hostels',AdminViews.manage_hostels,name="manage_hostels"),
    path('hostels_manage',HostelViews.hostels_manage,name="hostels_manage"),
    path('manage_rooms',AdminViews.manage_rooms,name="manage_rooms"),
    path('rooms_manage',HostelViews.rooms_manage,name="rooms_manage"),
    path('hostel_all_notification',HostelViews.hostel_all_notification,name="hostel_all_notification"),
    path('hostel_feedback',HostelViews.hostel_feedback,name="hostel_feedback"),
    path('allocate_room',HostelViews.allocate_room,name="allocate_room"),
    path('get_rooms',HostelViews.get_rooms,name="get_rooms"),
    path('create_log',HostelViews.create_log,name="create_log"),
    path('view_logs',HostelViews.view_logs,name="view_logs"),
    path('report_preview/<str:report_id>',HostelViews.report_preview,name="report_preview"),






    #Tutors URLs
    path('tutors_home',TutorViews.tutors_home,name="tutors_home"),
    path('subject_students',TutorViews.subject_students,name="subject_students"),
    path('get_tutor_students',TutorViews.get_tutor_students,name="get_tutor_students"),
    path('form_class',TutorViews.form_class,name="form_class"),
    path('tutors_subjects',TutorViews.tutors_subjects,name="tutors_subjects"),
    path('take_attendance',TutorViews.take_attendance,name="take_attendance"),
    path('get_students',TutorViews.get_students,name="get_students"),
    path('save_attendance_date',TutorViews.save_attendance_date,name="save_attendance_date"),
    path('student_attendance',TutorViews.student_attendance,name="student_attendance"),
    path('get_attendance_date',TutorViews.get_attendance_date,name="get_attendance_date"),
    path('get_attendance_student',TutorViews.get_attendance_student,name="get_attendance_student"),
    path('update_attendance_date',TutorViews.update_attendance_date,name="update_attendance_date"), 
    path('staff_leave',TutorViews.staff_leave,name="staff_leave"),
    path('staff_leave_save',TutorViews.staff_leave_save,name="staff_leave_save"),
    path('staff_feedback',TutorViews.staff_feedback,name="staff_feedback"),
    path('staff_feedback_save',TutorViews.staff_feedback_save,name="staff_feedback_save"),
    path('tutors_profile',TutorViews.tutors_profile,name="tutors_profile"),
    path('staff_profile',TutorViews.staff_profile,name="staff_profile"),
    path('staff_profile_save',TutorViews.staff_profile_save,name="staff_profile_save"),
    path('staff_fcmtoken_save',TutorViews.staff_fcmtoken_save,name="staff_fcmtoken_save"),
    path('staff_all_notification',TutorViews.staff_all_notification,name="staff_all_notification"),
    path('form_students/<str:class_id>',TutorViews.form_students,name="form_students"),
    path('submit_plan',TutorViews.submit_plan,name="submit_plan"),

    path('delete_plan/<str:item_id>',TutorViews.delete_plan,name="delete_plan"),
    path('delete_mid/<str:item_id>',TutorViews.delete_mid,name="delete_mid"),
    path('delete_end/<str:item_id>',TutorViews.delete_end,name="delete_end"),
    path('class_results/<str:class_id>',TutorViews.class_results,name="class_results"),
    path('class_student/<str:std_id>',TutorViews.class_student,name="class_student"),
    path('delete_score/<int:restype>/<int:score_id>',TutorViews.delete_score,name="delete_score"),
    path('combmidterm_save', TutorViews.combmidterm_save, name='combmidterm_save'),
    path('combendterm_save', TutorViews.combendterm_save, name='combendterm_save'),
    path('tutorattestation', TutorViews.tutorattestation, name='tutorattestation'),
    path('formbroadsheet', TutorViews.formbroadsheet, name='formbroadsheet'),
    # Tutor CBT
    path('tutor_quizes/', TutorViews.quiz_management, name='tutor_quiz_management'),
    path('tutor_quizes/add/', TutorViews.add_quiz, name='tutor_add_quiz'),
    path('tutor_quizes/schedule/add/', TutorViews.add_quiz_schedule, name='tutor_add_quiz_schedule'),
    path('tutor_edit_quiz/<int:quiz_id>/', TutorViews.edit_quiz, name='tutor_edit_quiz'), 
    path('tutor_quizes/schedule/<int:schedule_id>/delete/', TutorViews.delete_quiz_schedule, name='tutor_delete_quiz_schedule'),
    path('tutor_edit_quiz_schedule/<int:schedule_id>/', TutorViews.edit_quiz_schedule, name='tutor_edit_quiz_schedule'), 
    path('tutor_quizes/<int:quiz_id>/add-objective-question/', TutorViews.add_objective_question, name='tutor_add_objective_question'),
    path('tutor_add_theory/<int:quiz_id>/', TutorViews.add_theory_question, name='tutor_add_theory'),
    path('tutor_view_questions/<int:quiz_id>/', TutorViews.question_view, name='tutor_question_view'),
    path('schedule/<int:schedule_id>/students/', TutorViews.schedule_students, name='schedule_students'),
    path('results/<int:schedule_id>/<int:student_id>/', TutorViews.result_details, name='result_details'),


    path('addquiz/', TutorViews.AddQuizView.as_view(), name='addquiz'),
    path('addquestion/<quiz_id>/', TutorViews.add_questions, name='addquestion'),


        #  Result Actions
    path('result_action',TutorViews.result_action,name="result_action"),
    path('result_action_midterm',TutorViews.result_action_midterm,name="result_action_midterm"),
    path('result_action_endterm',TutorViews.result_action_endterm,name="result_action_endterm"),
    path('tutor_add_midterm_result',TutorViews.tutor_add_midterm_result,name="tutor_add_midterm_result"),
    path('tutor_add_endterm_result',TutorViews.tutor_add_endterm_result,name="tutor_add_endterm_result"),
    path('result_get_students',TutorViews.result_get_students,name="result_get_students"),
    path('save_midterm_result',TutorViews.save_midterm_result,name="save_midterm_result"),
    path('save_endterm_result',TutorViews.save_endterm_result,name="save_endterm_result"),
    path('get_midterm_result',TutorViews.get_midterm_result,name="get_midterm_result"),
    path('manage_midterm_result',TutorViews.manage_midterm_result,name="manage_midterm_result"),
    path('manage_endterm_result',TutorViews.manage_endterm_result,name="manage_endterm_result"),
    path('get_endterm_result',TutorViews.get_endterm_result,name="get_endterm_result"),
    path('save_add_endterm_result',TutorViews.save_add_endterm_result,name="save_add_endterm_result"),
    path('manage_save_midterm_result',TutorViews.manage_save_midterm_result,name="manage_save_midterm_result"),
    path('manage_save_endterm_result',TutorViews.manage_save_endterm_result,name="manage_save_endterm_result"),
    path('tutorview_midterm_result',TutorViews.tutorview_midterm_result,name="tutorview_midterm_result"),
    path('get_midterm_result',TutorViews.get_midterm_result,name="get_midterm_result"),
    path('tutorview_endterm_result',TutorViews.tutorview_endterm_result,name="tutorview_endterm_result"),
    path('manage_form_class/<str:class_id>',TutorViews.manage_form_class,name="manage_form_class"),
    path('asses_formclass',TutorViews.asses_formclass,name="asses_formclass"),
    path('tutors_assesment/<str:class_id>',TutorViews.tutors_assesment,name="tutors_assesment"),
    path('tutor_assess_student/<str:students_id>',TutorViews.tutor_assess_student,name="tutor_assess_student"),
    path('save_assessment',TutorViews.save_assessment,name="save_assessment"),

    
    # G and C
    path('gandc', TutorViews.gandc, name='gandc'),

    #student Portal URLs
    path('students_home',StudentViews.students_home,name="students_home"),
    path('student_view_attendance',StudentViews.student_view_attendance,name="student_view_attendance"),
    path('student_view_attendance_post',StudentViews.student_view_attendance_post,name="student_view_attendance_post"),
    path('student_leave',StudentViews.student_leave,name="student_leave"),
    path('student_leave_save',StudentViews.student_leave_save,name="student_leave_save"),
    path('student_feedback',StudentViews.student_feedback,name="student_feedback"),
    path('student_feedback_save',StudentViews.student_feedback_save,name="student_feedback_save"),
    path('student_subjects',StudentViews.student_subjects,name="student_subjects"),
    path('student_profile',StudentViews.student_profile,name="student_profile"),
    path('student_profile_save',StudentViews.student_profile_save,name="student_profile_save"),
    path('student_fcmtoken_save',StudentViews.student_fcmtoken_save,name="student_fcmtoken_save"),
    path('firebase-messaging-sw.js',views.showFirebaseJs,name="show_firebase_js"),
    path('student_all_notification',StudentViews.student_all_notification,name="student_all_notification"),
    path('my_results/<str:res_type>',StudentViews.my_results,name="my_results"),
    path('online_class',StudentViews.online_classes,name="online_class"),
    path('e_library',StudentViews.e_library,name="e_library"),
    path('student_faq',StudentViews.student_faq,name="student_faq"),
    path('result_preview/<int:res_id>',StudentViews.result_preview,name="result_preview"),
    path('tuition_preview',StudentViews.tuition_preview,name="tuition_preview"),

    path('inter_records',StudentViews.inter_records,name="inter_records"),
    path('saveinterests',StudentViews.saveinterests,name="saveinterests"),
    
    path('student/assignments/', StudentViews.student_assignments, name='student_assignments'),
    path('student/notes/', StudentViews.student_notes, name='student_notes'),
    path('student/textbooks/', StudentViews.student_textbooks, name='student_textbooks'),
    path('student/textbook/<int:material_id>/', StudentViews.view_textbook, name='view_textbook'),
    
     # Student CBT
    path('cbt_view',StudentViews.cbt_view,name="cbt_view"),
    path('cbt_objective/<int:schedule_id>/', StudentViews.quiz_view, name='cbt_objective'),
    path('cbt_theory/<int:schedule_id>/', StudentViews.theory_view, name='cbt_theory'),
    path('submit_quiz/<int:schedule_id>/', StudentViews.submit_quiz, name='submit_quiz'),
    path('handle_timeout/<int:schedule_id>/', StudentViews.handle_timeout, name='handle_timeout'),
    path('save_answer/<int:schedule_id>/', StudentViews.save_answer, name='save_answer'),
    path('cbt_result/<int:schedule_id>/', StudentViews.quiz_result_view, name='cbt_result'),
    path('cbt_complete/<int:schedule_id>/', StudentViews.quiz_complete, name='quiz_complete'),


    path('cbt_view',StudentViews.cbt_view,name="cbt_view"),





    # Principal Darchboard URLs
    path('principal_home',PrincipalViews.principal_home,name="principal_home"),
    path('principal_view_students',PrincipalViews.principal_view_students,name="principal_view_students"),
    path('principal_view_staff',PrincipalViews.principal_view_staff,name="principal_view_staff"),
    path('principal_view_subjects',PrincipalViews.principal_view_subjects,name="principal_view_subjects"),
    path('principal_result_action',PrincipalViews.principal_result_action,name="principal_result_action"),
    path('principal_get_result',PrincipalViews.principal_get_result,name="principal_get_result"),
    path('principal_profile',PrincipalViews.principal_profile,name="principal_profile"),
    path('edit_principal_profile',PrincipalViews.edit_principal_profile,name="edit_principal_profile"),
    path('principal_leave',PrincipalViews.principal_leave,name="principal_leave"),
    path('leave_approve/<str:leave_id>',PrincipalViews.leave_approve,name="leave_approve"),
    path('leave_decline/<str:leave_id>',PrincipalViews.leave_decline,name="leave_decline"),
    path('principal_feedback',PrincipalViews.principal_feedback,name="principal_feedback"),
    path('principal_feedback_save',PrincipalViews.principal_feedback_save,name="principal_feedback_save"),
    path('student_feedbacks',PrincipalViews.student_feedbacks,name="student_feedbacks"),
    path('job_applications',PrincipalViews.job_applications,name="job_applications"),
    path('student_applications',PrincipalViews.student_applications,name="student_applications"),
    path('lession_plan/<str:subject_id>',PrincipalViews.lession_plan,name="lession_plan"),

    
    # principal result
    path('management_result',PrincipalViews.management_result,name="management_result"),
    path('management_studentresults',PrincipalViews.management_studentresults,name="management_studentresults"),
    path('thebroadsheet_analysis',PrincipalViews.thebroadsheet_analysis,name="thebroadsheet_analysis"),
    path('management_subjectresults',PrincipalViews.management_subjectresults,name="management_subjectresults"),
    path('host_analytics',PrincipalViews.hostel_analytics,name="host_analytics"),





    # Managment Darshboard URLs
    path('management_home',ManagementViews.management_home,name="management_home"),


    # Admin Sec. Darshboard URLs
    path('adminsec_home',AdminsecViews.adminsec_home,name="adminsec_home"),
    path('payment_history',AdminsecViews.payment_history,name="payment_history"),
    path('adminsec_students',AdminsecViews.adminsec_students,name="adminsec_students"),
    path('adminsec_get_students',AdminsecViews.adminsec_get_students,name="adminsec_get_students"),
    path('adminsec_profile',AdminsecViews.adminsec_profile,name="adminsec_profile"),
    path('adminsec_feedback',AdminsecViews.adminsec_feedback,name="adminsec_feedback"),
    path('adminsec_feedback_save',AdminsecViews.adminsec_feedback_save,name="adminsec_feedback_save"),
    path('adminsec_view_subjects',AdminsecViews.adminsec_view_subjects,name="adminsec_view_subjects"),
    path('adminsec_message',AdminsecViews.adminsec_message,name="adminsec_message"),
    path('student_application',AdminsecViews.student_application,name="student_application"),
    path('job_application',AdminsecViews.job_application,name="job_application"),
    path('add_event',AdminsecViews.add_event,name="add_event"),
    path('adminsec_staff_todo',AdminsecViews.adminsec_staff_todo,name="adminsec_staff_todo"),
    path('add_posts',AdminsecViews.add_posts,name="add_posts"),
    path('assign_post',AdminsecViews.assign_post,name="assign_post"),
    path('adminsec_staff',AdminsecViews.adminsec_staff,name="adminsec_staff"),
    path('assign_task',AdminsecViews.assign_task,name="assign_task"),


   # Tuck shop urls
    path('tuckshop_home',TuckshopViews.tuckshop_home,name="tuckshop_home"),
    path('tuckshop_students',TuckshopViews.tuckshop_students,name="tuckshop_students"),
    path('tuckshop_get_students',TuckshopViews.tuckshop_get_students,name="tuckshop_get_students"),
    path('tuckshop_staff',TuckshopViews.tuckshop_staff,name="tuckshop_staff"),
    path('requisition',TuckshopViews.t_requisition,name="requisition"),
    path('m_analysis',TuckshopViews.m_analysis,name="m_analysis"),
    path('a_analysis',TuckshopViews.a_analysis,name="a_analysis"),
    path('tuckshop_profile',TuckshopViews.tuckshop_profile,name="tuckshop_profile"),
    path('tuckshop_feedback',TuckshopViews.tuckshop_feedback,name="tuckshop_feedback"),
    path('tuckshop_feedback_save',TuckshopViews.tuckshop_feedback_save,name="tuckshop_feedback_save"),
    path('add-item/', TuckshopViews.AddItemView.as_view(), name='add_item'),
    path('add-stock/', TuckshopViews.StockOperationView, name='add_stock'),
    path('add-quantity/', TuckshopViews.add_quantity, name='add_quantity'),
    path('update-stock/', TuckshopViews.update_stock, name='update_stock'),
    path('view-report/', TuckshopViews.view_report, name='view_report'),
    path('damage-report/', TuckshopViews.damage_report, name='damage_report'),

    # to be implemented later
    path('billings',AdminsecViews.billings,name="billings"),
    path('bill_student/<str:students_id>',AdminsecViews.bill_student,name="bill_student"),
    path('bill_student_save',AdminsecViews.bill_student_save,name="bill_student_save"),

    #    implemented 
    path('billing_action',AdminsecViews.billing_action,name="billing_action"),
    path('manual_bill',AdminsecViews.manual_bill,name="manual_bill"),
    path('manual_pay',AdminsecViews.manual_pay,name="manual_pay"),
    path('pay_save',AdminsecViews.pay_save,name="pay_save"),
    path('get_class',AdminsecViews.get_class,name="get_class"),
    path('bill_class',AdminsecViews.bill_class,name="bill_class"),
    path('breakdown_action',AdminsecViews.breakdown_action,name="breakdown_action"),
    path('breakdown_item_save',AdminsecViews.breakdown_item_save,name="breakdown_item_save"),
    path('edit_items/<str:item_id>',AdminsecViews.edit_items,name="edit_items"),
    path('item_edit_save',AdminsecViews.item_edit_save,name="item_edit_save"),
    path('delete_item/<str:item_id>',AdminsecViews.delete_item,name="delete_item"),
    path('newsletter_compose',AdminsecViews.newsletter_compose,name="newsletter_compose"),




    #Paystack Payments
    path('',include('paystackpayments.urls')),
    # path('initiate_payment/', PayViews.initiate_payment, name="initiate_payment"),
    # path('<str:ref>/', PayViews.verify_payment, name="verify_payment"),
    # path('paystack_webhook', PayViews.paystack_webhook, name="paystack_webhook"),
    
    #Online CBT URLS
    path('', include('onlinecbt.urls')),
    #Accounts
    path('', include('accounts.urls')),

    #Online CBT URLS
    path('', include('onlinecbt.urls', namespace='quiz')),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

handler404 = 'accounts.views.error_404'
