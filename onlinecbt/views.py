<<<<<<< HEAD
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from .models import Quiz, QuizResult, QuizSchedule, StudentAnswer, StudentProgress, TheoryQuestion, ObjectiveQuestion, ObjectiveOption
from .forms import ObjectiveQuestionForm, ObjectiveOptionForm, QuizForm, QuizScheduleForm
from django.http import HttpResponseBadRequest
from django.db.models import Prefetch
from django.db.models import OuterRef, Subquery
import datetime


# View to display the page with the accordions for Quiz and Quiz Schedule
def quiz_management(request):
    quizzes = Quiz.objects.all()  # Fetch all quizzes
    schedules = QuizSchedule.objects.all()  # Fetch all quiz schedules

    quiz_form = QuizForm()  # Empty form for adding a quiz
    schedule_form = QuizScheduleForm()  # Empty form for adding a quiz schedule

    context = {
        'quiz_form': quiz_form,
        'schedule_form': schedule_form,
        'quizzes': quizzes,
        'schedules': schedules,
    }
    return render(request, 'quizes/add_quiz.html', context)


# View to handle adding a quiz
def add_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    return redirect('quiz_management')


# View to handle adding a quiz schedule
def add_quiz_schedule(request):
    if request.method == 'POST':
        form = QuizScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    return redirect('quiz_management')


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

    return redirect('quiz_management')


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
            print(form.errors)
            print(request.POST)
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = QuizScheduleForm(instance=schedule)  # Prepopulate the form with the existing schedule data
        return render(request, 'quizes/edit_schedule.html', {'form': form, 'schedule': schedule})




# View to display quiz details with buttons to manage questions
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    objective_questions = quiz.objective_questions.all()  # Fetch associated questions

    context = {
        'quiz': quiz,
        'objective_questions': objective_questions,
    }
    return render(request, 'quizes/quiz_detail.html', context)

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
        return redirect('view_objective', quiz_id=quiz.id)

    # GET request: Show the form to add questions
    return render(request, 'quizes/add_objective.html', {'quiz': quiz})

# View to display success page with all submitted questions
def viewobjective(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.objective_questions.all()

    return render(request, 'quizes/view_objective.html', {'quiz': quiz, 'questions': questions})


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
        return redirect('question_view', quiz_id=quiz.id)

    return render(request, 'quizes/add_theory.html', {'quiz': quiz})


# View to display the submitted theory questions
def question_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    theory_questions = quiz.theory_questions.all()

    return render(request, 'quizes/question_view.html', {'quiz': quiz, 'theory_questions': theory_questions})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def quiz_view(request, schedule_id):
    student = request.user
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)

    # Fetch or create student progress
    progress, created = StudentProgress.objects.get_or_create(student=student, schedule=quiz_schedule)

    # Check if the quiz has already been submitted
    result = QuizResult.objects.filter(student=student, schedule=quiz_schedule).first()
    if result:
        return redirect('quiz_view_theory', schedule_id=schedule_id)

    # Check if current time is before the quiz start time
    current_time = timezone.now()
    start_time = quiz_schedule.start_time

    # If current time is earlier than start time, display countdown to start time
    if current_time < start_time:
        time_until_start = (start_time - current_time).total_seconds()  # Calculate time in seconds
        return render(request, 'quizes/quiz_countdown.html', {
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

    return render(request, 'quizes/quiz_ongoing.html', {
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
        return redirect('quiz_result', schedule_id=schedule_id)

    # Check if all answers for the student are submitted
    student_answers = StudentAnswer.objects.filter(student=student, schedule=quiz_schedule)
    
    # If there are no answers yet, allow the student to proceed
    if not student_answers.exists():
        pass  # Proceed with the quiz
    
    else:
        # If all answers are submitted, redirect to result page
        if student_answers.filter(is_submitted=False).exists():
            pass  # Proceed with the quiz, as not all answers are submitted
        else:
            # All answers are submitted
            return redirect('quiz_result', schedule_id=schedule_id)

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
    
    return render(request, 'quizes/theory_questions.html', {
        'schedule': quiz_schedule,
        'theory_questions': theory_questions,
        'time_remaining': time_remaining
    })


def submit_quiz(request, schedule_id):
    student = request.user
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)

    # Calculate the result or fetch the already existing result
    result, created = QuizResult.objects.get_or_create(student=student, schedule=quiz_schedule)
    result.calculate_score()  # Assuming this method calculates and saves the score

    # Redirect to the quiz result page
    return JsonResponse({'status': 'success', 'message': 'Answer saved successfully', 'code':'theory'})

def handle_timeout(request, schedule_id):
    # Called via AJAX if the quiz time runs out
    return submit_quiz(request, schedule_id)

def quiz_result_view(request, schedule_id):
    student = request.user
    quiz_schedule = get_object_or_404(QuizSchedule, id=schedule_id)
    result = get_object_or_404(QuizResult, student=student, schedule=quiz_schedule)

    return render(request, 'quizes/quiz_result.html', {'result': result, 'quiz_schedule': quiz_schedule})
=======
from django.shortcuts import render
from .models import Quiz, Question, Answer, Result, Students
from django.views.generic import ListView
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
# Create your views here.


class QuizListView(ListView):
    model = Quiz
    template_name = 'quizes/main.html'
    def get_queryset(self):
        student = get_object_or_404(Students, admin=self.request.user.id)
        return Quiz.objects.filter(subject=student.class_id.id)

def quiz_view(request, pk):
    quiz = Quiz.objects.get(pk=pk)
    return render(request, 'quizes/quiz.html', {'obj':quiz})

def quiz_data_view(request, pk):
    quiz = Quiz.objects.get(pk=pk)
    questions = []
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.text)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
        'time': quiz.time
    })

def save_quiz_view(request, pk):
    # print(request.POST)
    if request.is_ajax():
        questions = []
        data = request.POST
        data_ = dict(data.lists())
        data_.pop('csrfmiddlewaretoken')
        
        for k in data_.keys():
            print('keys: ', k)
            question = Question.objects.get(text=k)
            questions.append(question)
        print(questions)

        user = request.user
        quiz = Quiz.objects.get(pk=pk)

        score = 0
        multiplier = 100 / quiz.number_of_questions
        results = []
        correct_answers = None

        for q in questions:
            a_selected = request.POST.get(q.text)

            if a_selected != "":
                question_answers = Answer.objects.filter(question=q)
                for a in question_answers:
                    if a_selected == a.text:
                        if a.correct:
                            score +=1
                            correct_answers = a.text
                    else:
                        if a.correct:
                            correct_answers = a.text

                results.append({str(q): {'correct_answer': correct_answers, 'answered': a_selected}})
            else:
                results.append({str(q): 'not answered'})

        score_ = score * multiplier
        Result.objects.create(quiz=quiz, student=user, score=score_)

        if score_ >= quiz.required_score_to_pass:
            return JsonResponse({'passed': True, 'score': score_, 'results': results})
        else:
            return JsonResponse({'passed': False, 'score': score_, 'results': results})
>>>>>>> 869102c69b442947ca113121ce958681c2b69674
