from django.urls import path
from onlinecbt import views

urlpatterns = [
    path('quizes/', views.quiz_management, name='quiz_management'),
    path('quizes/add/', views.add_quiz, name='add_quiz'),
    path('quizes/schedule/add/', views.add_quiz_schedule, name='add_quiz_schedule'),
    path('edit_quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'), 
    path('quizes/schedule/<int:schedule_id>/delete/', views.delete_quiz_schedule, name='delete_quiz_schedule'),
    path('edit_quiz_schedule/<int:schedule_id>/', views.edit_quiz_schedule, name='edit_quiz_schedule'), 
    path('quizes/<int:quiz_id>/add-objective-question/', views.add_objective_question, name='add_objective_question'),
    path('view_objective/<int:quiz_id>/', views.viewobjective, name='view_objective'), 
    path('add_theory_question/<int:quiz_id>/', views.add_theory_question, name='add_theory_question'),
    path('view_theory_questions/<int:quiz_id>/', views.question_view, name='question_view'),
    path('quiz_view/<int:schedule_id>/', views.quiz_view, name='quiz_view'),
    path('quiz_view_theory/<int:schedule_id>/', views.theory_view, name='quiz_view_theory'),
    path('submit_quiz/<int:schedule_id>/', views.submit_quiz, name='submit_quiz'),
    path('handle_timeout/<int:schedule_id>/', views.handle_timeout, name='handle_timeout'),
    path('save_answer/<int:schedule_id>/', views.save_answer, name='save_answer'),
    path('quiz_result/<int:schedule_id>/', views.quiz_result_view, name='quiz_result'),
]

