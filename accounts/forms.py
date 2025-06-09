from django.forms.widgets import EmailInput, FileInput
from accounts.models import Classes, EntryAttestation, Item, GncQuestion, GncResponse, SessionYearModel, SiteControls, Stock, Subjects, StockLog, StudyMaterial, Terms, DamageReport
from django import forms


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email",max_length=50,widget=EmailInput(attrs={"class":"form-control","autocomplete":"off"}))
    password = forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="ID",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
    
    classes_list=[]
    classes=Classes.objects.all()
    
    for classes in classes:
        small_class=(classes.id,classes.name)
        classes_list.append(small_class)

    session_list=[]
    sessions=SessionYearModel.objects.all()    
    for ses in sessions:
        small_ses=(ses.id, ses.session_start_year+"/"+ses.session_end_year)
        session_list.append(small_ses)

    gender_choice=(
        ("Male","Male"),
        ("Female","Female")
    )
    religion_choice=(
        ("Christain","Christain"),
        ("Catholic","Catholic"),
        ("Muslim","Muslim")
    )
    state_choice=(
        ( "Abia","Abia"),
        ("Adamawa","Adamawa"),
        ("Akwa Ibom","Akwa Ibom"),
        ("Anambra","Anambra"),
        ("Bauchi","Bauchi"),
        ("Bayelsa","Bayelsa"),
        ("Benue","Benue"),
        ("Borno","Borno"),
        ("Cross River","Cross River"),
        ("Delta","Delta"),
        ("Ebonyi","Ebonyi"),
        ("Edo","Edo"),
        ("Ekiti","Ekiti"),
        ("Enugu","Enugu"),
        ("FCT - Abuja","FCT - Abuja"),
        ("Gombe","Gombe"),
        ("Imo","Imo"),
        ("Jigawa","Jigawa"),
        ("Kaduna","Kaduna"),
        ("Katsina","Katsina"),
        ("Kebbi","Kebbi"),
        ("Kogi","Kogi"),
        ("Kwara","Kwara"),
        ("Lagos","Lagos"),
        ("Nasarawa","Nasarawa"),
        ("Niger","Niger"),
        ("Ogun","Ogun"),
        ("Ondo","Ondo"),
        ("Osun","Osun"),
        ("Oyo","Oyo"),
        ("Plateau","Plateau"),
        ("Rivers","Rivers"),
        ("Sokoto","Sokoto"),
        ("Taraba","Taraba"),
        ("Yobe","Yobe"),
        ("Zamfara","Zamfara")
    )
    class_categories=(
        ("A","A"),
        ("B","B"),
        ("C","C"),
        ("D","D")
    )
    classes = forms.ChoiceField(label="Admission Class",choices=classes_list,widget=forms.Select(attrs={"class":"form-control"}))
    class_category = forms.ChoiceField(label="Class Category",choices=class_categories,widget=forms.Select(attrs={"class":"form-control"}))
    religion = forms.ChoiceField(label="Religion/Denomination",choices=religion_choice,widget=forms.Select(attrs={"class":"form-control"}))
    origin_state = forms.ChoiceField(label="State Of Origin",choices=state_choice,widget=forms.Select(attrs={"class":"form-control"}))
    dob = forms.DateField(label="Date of Birth", widget=DateInput(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Admission Session",widget=forms.Select(attrs={"class":"form-control"}),choices=session_list)
    address = forms.CharField(label="Home Address",max_length=150,widget=forms.TextInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Passport",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}))
    parent_name = forms.CharField(label="Parent Full Name",max_length=100,widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_phone = forms.CharField(label="Parent Phone",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_email = forms.EmailField(label="Parent Email",max_length=100,widget=EmailInput(attrs={"class":"form-control","autocomplete":"off"}))


class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email",max_length=50,widget=EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))

    classes_list=[]
    classes=Classes.objects.all()
        
    for classes in classes:
        small_class=(classes.id,classes.name)
        classes_list.append(small_class)

    session_list=[]
    sessions=SessionYearModel.objects.all()
    
    for ses in sessions:
        small_ses=(ses.id, str(ses.session_start_year)+"    To   "+str(ses.session_end_year))
        session_list.append(small_ses)

    gender_choice=(
        ("Male","Male"),
        ("Female","Female")
    )
    religion_choice=(
        ("Christain","Christain"),
        ("Catholic","Catholic"),
        ("Muslim","Muslim")
    )
    state_choice=(
        ( "Abia","Abia"),
        ("Adamawa","Adamawa"),
        ("Akwa Ibom","Akwa Ibom"),
        ("Anambra","Anambra"),
        ("Bauchi","Bauchi"),
        ("Bayelsa","Bayelsa"),
        ("Benue","Benue"),
        ("Borno","Borno"),
        ("Cross River","Cross River"),
        ("Delta","Delta"),
        ("Ebonyi","Ebonyi"),
        ("Edo","Edo"),
        ("Ekiti","Ekiti"),
        ("Enugu","Enugu"),
        ("FCT - Abuja","FCT - Abuja"),
        ("Gombe","Gombe"),
        ("Imo","Imo"),
        ("Jigawa","Jigawa"),
        ("Kaduna","Kaduna"),
        ("Katsina","Katsina"),
        ("Kebbi","Kebbi"),
        ("Kogi","Kogi"),
        ("Kwara","Kwara"),
        ("Lagos","Lagos"),
        ("Nasarawa","Nasarawa"),
        ("Niger","Niger"),
        ("Ogun","Ogun"),
        ("Ondo","Ondo"),
        ("Osun","Osun"),
        ("Oyo","Oyo"),
        ("Plateau","Plateau"),
        ("Rivers","Rivers"),
        ("Sokoto","Sokoto"),
        ("Taraba","Taraba"),
        ("Yobe","Yobe"),
        ("Zamfara","Zamfara")
    )
    class_categories=(
        ("A","A"),
        ("B","B"),
        ("C","C"),
        ("D","D")
    )

    classes = forms.ChoiceField(label="Class",choices=classes_list,widget=forms.Select(attrs={"class":"form-control"}))
    class_category = forms.ChoiceField(label="Class Category",choices=class_categories,widget=forms.Select(attrs={"class":"form-control"}))
    religion = forms.ChoiceField(label="Religion/Denomination",choices=religion_choice,widget=forms.Select(attrs={"class":"form-control"}))
    origin_state = forms.ChoiceField(label="State Of Origin",choices=state_choice,widget=forms.Select(attrs={"class":"form-control"}))
    dob = forms.DateField(label="Date of Birth", widget=DateInput(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year",widget=forms.Select(attrs={"class":"form-control"}),choices=session_list)
    address = forms.CharField(label="Address",max_length=150,widget=forms.TextInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Passport",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}),required=False)
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class": "form-control"}), required=False)
    parent_name = forms.CharField(label="Parent Full Name",max_length=100,widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_phone = forms.CharField(label="Parent Phone",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_email = forms.EmailField(label="Parent Email",max_length=100,widget=EmailInput(attrs={"class":"form-control","autocomplete":"off"}))


class EditResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.staff_id=kwargs.pop("staff_id")
        super().__init__()
        subject_list=[]
        try:
            subjects=Subjects.objects.filter(tutor=self.staff_id)
            for subject in subjects:
                subject_single=(subject.id,subject.subject_name)
                subject_list.append(subject_single)
        except:
            subject_list=[]
        
        # subject_id=forms.ChoiceField(label="Subject",choices=subject_list,widget=forms.Select(attrs={"class":"form-control"}))

class EntryAttestationForm(forms.ModelForm):
    class Meta:
        model = EntryAttestation
        fields = ['remark', 'term', 'result_type', 'subjects', 'session_year']
        widgets = {
            'remark': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Attestation note'}),
            'term': forms.HiddenInput(),
            'session_year': forms.HiddenInput(),
            'result_type': forms.HiddenInput(),
            'subjects': forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super(EntryAttestationForm, self).__init__(*args, **kwargs)
        active_term = Terms.objects.get(status=1)
        active_session = SessionYearModel.objects.get(status=1)
        self.fields['term'].initial = active_term
        self.fields['session_year'].initial = active_session
        site_control = SiteControls.objects.filter(c_code='RT').first()
        if site_control and site_control.status == 0:
            self.fields['result_type'].initial = 0  # First Half
        elif site_control and site_control.status == 1:
            self.fields['result_type'].initial = 1  # End of Term



class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['subject', 'title', 'material_type', 'file', 'pdf_url', 'status']

    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        file = cleaned_data.get('file')
        pdf_url = cleaned_data.get('pdf_url')

        if material_type == StudyMaterial.TEXTBOOK and not pdf_url:
            self.add_error('pdf_url', "A URL is required for textbooks.")
        elif material_type in [StudyMaterial.NOTE, StudyMaterial.ASSIGNMENT] and not file:
            self.add_error('file', "A file is required for notes and assignments.")

        return cleaned_data


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label


    class Meta:
        model = Item
        fields = ['name', 'brand', 'package_type', 'description', 'note', 'expected_marketprice']
        
        

class StockOperationForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['item', 'quantity', 'price', 'notes']
        
class DateForm(forms.Form):
    general_note = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    

# forms.py
class AddQuantityForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['item', 'quantity', 'price']

AddQuantityFormSet = forms.formset_factory(AddQuantityForm, extra=1)

class DamageReportForm(forms.ModelForm):
    class Meta:
        model = DamageReport
        fields = ['item', 'date', 'image1', 'image2','notes']





#gnc
class QuestionForm(forms.ModelForm):
    class Meta:
        model = GncQuestion
        fields = ['text', 'field_type', 'form_type']
        
        
class GncResponseForm(forms.ModelForm):
    form_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = GncResponse
        fields = ['question', 'answer_choice']
        widgets = {
            'question': forms.HiddenInput(),
            'answer_choice': forms.RadioSelect(choices=[(str(k), v) for k, v in GncQuestion.OPTIONS.items()]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance'].question:
            self.fields['question_text'] = forms.CharField(
                initial=kwargs['instance'].question.text,
                required=False,
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )
            self.fields['question_text'].label = kwargs['instance'].question.text
            self.fields['form_type'].initial = question.form_type
        elif 'initial' in kwargs and 'question' in kwargs['initial']:
            question = GncQuestion.objects.get(pk=kwargs['initial']['question'])
            self.fields['question_text'] = forms.CharField(
                initial=question.text,
                required=False,
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )
            self.fields['question_text'].label = question.text
            self.fields['form_type'].initial = question.form_type

    def clean(self):
        cleaned_data = super().clean()
        answer_choice = cleaned_data.get('answer_choice')
        if answer_choice:
            answer_choice_int = int(answer_choice)
            cleaned_data['answer_text'] = GncQuestion.OPTIONS[answer_choice_int]
            cleaned_data['answer_choice'] = answer_choice_int
        return cleaned_data
