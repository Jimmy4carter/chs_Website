from django import forms
from django.db.models import Q
from accounts.models import CombineSubjects, Subjects
from .models import ObjectiveQuestion, ObjectiveOption, Quiz, QuizSchedule

# Form for adding/editing a Quiz
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'subject']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter quiz title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter quiz description', 
                'rows': 3
            }),
            'subject': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop('tutor', None)
        super().__init__(*args, **kwargs)

        if tutor:
            # Get subjects directly linked to the tutor or through CombineSubjects
            subjects = Subjects.objects.filter(
                Q(tutor=tutor) | 
                Q(id__in=CombineSubjects.objects.filter(tutor=tutor).values('subject_main'))
            ).distinct()
            
            # Create subject choices list
            self.fields['subject'].choices = [
                (subject.id, subject.outline.name.split('/')[-1] if subject.outline else "No Outline")
                for subject in subjects
            ]
        
        # Ensure 'form-control' class is applied
        self.fields['subject'].widget.attrs.update({'class': 'form-control'})

# Form for adding/editing a QuizSchedule
class QuizScheduleForm(forms.ModelForm):
    class Meta:
        model = QuizSchedule
        fields = ['name', 'quiz', 'start_time', 'duration', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter schedule name'
            }),
            'quiz': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Select start time',
                'type': 'datetime-local'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter duration in minutes'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop('tutor', None)  # Get the current user (tutor)
        super(QuizScheduleForm, self).__init__(*args, **kwargs)
        if tutor:
            # Filter quizzes based on subjects where the tutor is the current user
            subjects_taught = Subjects.objects.filter(
                Q(tutor=tutor) | 
                Q(id__in=CombineSubjects.objects.filter(tutor=tutor).values('subject_main'))
            ).distinct()
            quizzes = Quiz.objects.filter(subject__in=subjects_taught)
            self.fields['quiz'].queryset = quizzes  # Set filtered queryset for quiz field


# Form for adding/editing an Objective Question
class ObjectiveQuestionForm(forms.ModelForm):
    class Meta:
        model = ObjectiveQuestion
        fields = ['question', 'diagram']
        widgets = {
            'question': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the objective question',
                'rows': 3,
            }),
        }

# Form for adding/editing an Objective Option
class ObjectiveOptionForm(forms.ModelForm):
    class Meta:
        model = ObjectiveOption
        fields = ['option_text', 'option_value', 'is_correct']
        widgets = {
            'option_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter option text',
            }),
            'option_value': forms.Select(attrs={
                'class': 'form-control',
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
