from django import forms

from accounts.models import SiteControls
from .models import StudentEthosRecords, Terms, SessionYearModel, Students

class StudentEthosRecordForm(forms.ModelForm):
    class Meta:
        model = StudentEthosRecords
        fields = ['student_id', 'term', 'session_year', 'result_type', 'leadership', 'neatness', 'room_represent_compet', 'room_represent_inspect', 'selfconfidence', 'team_spirit', 'return_lost_items', 'obidience_to_staff', 'obidience_to_rules', 'volunteerism', 'reporting_unacceptable_behavior', 'prayerfullness', 'loitering', 'immoral_relation_conduct', 'poor_timing', 'negative_influence', 'noise_making', 'hostel_disobidience', 'bullying_fighting', 'negative_civil', 'gossip', 'avoiding_meals', 'carelessness_personal', 'remark']
        widgets = {
            'student_id': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.HiddenInput(),
            'session_year': forms.HiddenInput(),
            'result_type': forms.HiddenInput(),
            'leadership': forms.Select(attrs={'class': 'form-control'}),
            'neatness': forms.Select(attrs={'class': 'form-control'}),
            'room_represent_compet': forms.Select(attrs={'class': 'form-control'}),
            'room_represent_inspect': forms.Select(attrs={'class': 'form-control'}),
            'selfconfidence': forms.Select(attrs={'class': 'form-control'}),
            'team_spirit': forms.Select(attrs={'class': 'form-control'}),
            'return_lost_items': forms.Select(attrs={'class': 'form-control'}),
            'obidience_to_staff': forms.Select(attrs={'class': 'form-control'}),
            'obidience_to_rules': forms.Select(attrs={'class': 'form-control'}),
            'volunteerism': forms.Select(attrs={'class': 'form-control'}),
            'reporting_unacceptable_behavior': forms.Select(attrs={'class': 'form-control'}),
            'prayerfullness': forms.Select(attrs={'class': 'form-control'}),
            'loitering': forms.Select(attrs={'class': 'form-control'}),
            'immoral_relation_conduct': forms.Select(attrs={'class': 'form-control'}),
            'poor_timing': forms.Select(attrs={'class': 'form-control'}),
            'negative_influence': forms.Select(attrs={'class': 'form-control'}),
            'noise_making': forms.Select(attrs={'class': 'form-control'}),
            'hostel_disobidience': forms.Select(attrs={'class': 'form-control'}),
            'bullying_fighting': forms.Select(attrs={'class': 'form-control'}),
            'negative_civil': forms.Select(attrs={'class': 'form-control'}),
            'gossip': forms.Select(attrs={'class': 'form-control'}),
            'avoiding_meals': forms.Select(attrs={'class': 'form-control'}),
            'carelessness_personal': forms.Select(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Remark'}),
        }

    def __init__(self, *args, **kwargs):
        super(StudentEthosRecordForm, self).__init__(*args, **kwargs)
        active_term = Terms.objects.get(status=1)
        active_session = SessionYearModel.objects.get(status=1)
        self.fields['term'].queryset = Terms.objects.all()
        self.fields['term'].initial = active_term
        self.fields['session_year'].queryset = SessionYearModel.objects.all()
        self.fields['session_year'].initial = active_session
        
        students = Students.objects.filter(class_id__lt=7)
        choices = [(student.id, f"{student.admin.first_name} {student.admin.last_name}") for student in students]
        self.fields['student_id'].choices = choices
        
        site_control = SiteControls.objects.filter(c_code='RT').first()
        if site_control and site_control.status == 0:
            self.fields['result_type'].initial = 0  # First Half
        elif site_control and site_control.status == 1:
            self.fields['result_type'].initial = 1  # End of Term
