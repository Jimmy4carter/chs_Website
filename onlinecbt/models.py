from django.db import models
from accounts.models import Students, Subjects
from django.conf import settings
import random
from django.utils import timezone
from django.contrib.auth import get_user_model


# Create your models here.




class Quiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.subject.subject_name}  - {self.subject.outline} "

class QuizSchedule(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=200)  # Example: 'Midterm Test 1'
    start_time = models.DateTimeField()
    duration = models.IntegerField()  # e.g., timedelta(hours=1, minutes=30)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('ongoing', 'Ongoing'), ('complete', 'Complete'),('result', 'Result')], default='pending')

    def __str__(self):
        return f"{self.name} - {self.quiz.title}"

    @property
    def end_time(self):
        return self.start_time + self.duration

class ObjectiveQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='objective_questions')
    question = models.TextField()
    diagram = models.ImageField(upload_to='question_diagrams/', null=True, blank=True)
 
    def __str__(self):
        return f"Objective Question - {self.quiz.title}"

class ObjectiveOption(models.Model):
    question = models.ForeignKey(ObjectiveQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    option_value = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')])
    is_correct = models.BooleanField(default=False)  # True if this is the correct option

    def __str__(self):
        return f"{self.option_value} - {self.question.quiz.title}"

class TheoryQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='theory_questions')
    question_number = models.IntegerField()  # To maintain question order for theory
    question = models.TextField()
    diagram = models.ImageField(upload_to='question_diagrams/', null=True, blank=True)
    answer_summary = models.TextField(null=True, blank=True)  # Summary of the answer, not visible to students

    def __str__(self):
        return f"Theory Q{self.question_number} - {self.quiz.title}"

class StudentAnswer(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='answers')
    schedule = models.ForeignKey(QuizSchedule, on_delete=models.CASCADE, related_name='student_answers')
    
    # Objective Answer
    objective_question = models.ForeignKey(ObjectiveQuestion, on_delete=models.CASCADE, null=True, blank=True)
    selected_option = models.ForeignKey(ObjectiveOption, on_delete=models.SET_NULL, null=True, blank=True)  # For objective answers
    is_correct = models.BooleanField(null=True)  # True if correct, False if wrong, Null if no answer

    # Theory Answer
    theory_question = models.ForeignKey(TheoryQuestion, on_delete=models.CASCADE, null=True, blank=True)
    theory_answer = models.TextField(null=True, blank=True)

    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'schedule', 'objective_question')

    def __str__(self):
        return f"{self.student.username} - {self.schedule.quiz.title}"

    def save(self, *args, **kwargs):
        # Automatically mark the answer as correct or not for objective questions
        if self.objective_question and self.selected_option:
            self.is_correct = self.selected_option.is_correct
        super().save(*args, **kwargs)

class StudentProgress(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='progress')
    schedule = models.ForeignKey(QuizSchedule, on_delete=models.CASCADE, related_name='progress')
    current_question_number = models.IntegerField(null=True, blank=True)  # Last answered question number
    time_remaining = models.DurationField(null=True, blank=True)  # Time left in the quiz
    last_saved = models.DateTimeField(auto_now=True)  # Automatically update when saved

    class Meta:
        unique_together = ('student', 'schedule')

    def __str__(self):
        return f"Progress: {self.student.username} - {self.schedule.quiz.title}"

class QuizResult(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='results')
    schedule = models.ForeignKey(QuizSchedule, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # For objective scores
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return f"Result: {self.student.username} - {self.schedule.quiz.title}"

    def calculate_score(self):
        correct_answers = StudentAnswer.objects.filter(student=self.student, schedule=self.schedule, is_correct=True).count()
        total_questions = ObjectiveQuestion.objects.filter(quiz=self.schedule.quiz).count()
        self.score = correct_answers  # Assuming 1 point per correct answer
        self.is_passed = self.score >= (total_questions * 0.5)  # Example: pass if >= 50%
        self.save()

