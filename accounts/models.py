from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.core.validators import FileExtensionValidator
from django.db.models.deletion import DO_NOTHING
from django.db.models.enums import Choices
from django.db.models.signals import post_save
from django.dispatch import receiver
import os



class SessionYearModel(models.Model):
    id=models.AutoField(primary_key= True) 
    session_start_year = models.CharField(max_length=255)
    session_end_year = models.CharField(max_length=255)
    status=models.IntegerField(default=0)
    objects=models.Manager()

class CustomUser(AbstractUser):
    user_type_data=((1,"Admin"),(2,"Tutor"),(3,"Student"),(4,"Principal"),(5,"Adminsec"))
    user_type=models.CharField(default=1,choices=user_type_data,max_length=10)

class Admin(models.Model):
    id = models.AutoField(primary_key = True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class StaffPost(models.Model):
    id = models.AutoField(primary_key = True)
    post_name = models.CharField(max_length=255)
    spec = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
class Staff(models.Model):
    id = models.AutoField(primary_key = True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address = models.TextField()
    profile_pic = models.FileField()
    post_held = models.ForeignKey(StaffPost, on_delete=DO_NOTHING, null=True)
    phone= models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    dob = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=255)
    contact_rel = models.CharField(max_length=255)
    status=models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects = models.Manager()
    class Meta:
        ordering = ('-created_at',)


class Classes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class ClassCategories(models.Model):
    id = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(Classes, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    form_tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Subjects(models.Model):
    id = models.AutoField(primary_key=True)
    class_id= models.ForeignKey(Classes, on_delete=models.CASCADE,default=1)
    subject_name = models.CharField(max_length=255)
    class_category= models.ForeignKey(ClassCategories, on_delete=models.CASCADE,default=1)
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    term1_resources= models.FileField()
    term2_resources= models.FileField()
    term3_resources= models.FileField()
    outline = models.FileField()
    objects = models.Manager()
    
class CombineSubjects(models.Model):
    id = models.AutoField(primary_key=True)
    subject_main= models.ForeignKey(Subjects, on_delete=models.CASCADE,default=1)
    name = models.CharField(max_length=255)
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    objects = models.Manager()

class SubjectsAllo(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    class_cat = models.ForeignKey(ClassCategories, on_delete=models.CASCADE)
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    

class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    gender = models.CharField(max_length=255)
    profile_pic = models.FileField()
    address = models.TextField()
    religion=models.CharField(max_length=255,default="Nigeria")
    origin_state=models.CharField(max_length=255,default="Nigeria")
    dob=models.CharField(max_length=255,default="00-00-000")
    admission_class = models.IntegerField(default=0)
<<<<<<< HEAD
    admission_ses = models.IntegerField(default=1)
=======
    admission_ses = models.IntegerField(default=0)
>>>>>>> 869102c69b442947ca113121ce958681c2b69674
    parent_name=models.CharField(max_length=255,default=" ")
    parent_email=models.CharField(max_length=255,default=" ")
    parent_phone=models.CharField(max_length=255,default="+234")
    class_category = models.ForeignKey(ClassCategories, on_delete=DO_NOTHING)
    class_id = models.ForeignKey(Classes, on_delete=models.DO_NOTHING, default=1)
    session_year_id=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects = models.Manager()


class Contact(models.Model):
    id=models.AutoField(primary_key=True)
    related_to=models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=0)
    Title=models.CharField(max_length=255)
    name=models.CharField(max_length=255)
    gender=models.CharField(max_length=255)
    relationship=models.CharField(max_length=255)
    address=models.TextField()
    phone1=models.CharField(max_length=255)
    phone2=models.CharField(max_length=255)
    email=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        ordering = ('-created_at',)

    

class Terms(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status=models.IntegerField(default=0)
    objects = models.Manager()
    
class CombineMidTerm(models.Model):
    id = models.AutoField(primary_key=True)
    students_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    subjects_id = models.ForeignKey(CombineSubjects,on_delete=models.CASCADE)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    resumption_text = models.FloatField(default=0)
    class_work = models.FloatField(default=0)
    assignment = models.FloatField(default=0)
    midterm_exam = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    grades = models.CharField(max_length=20,default='F')
    remark = models.CharField(max_length=255,default='Poor')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class MidTerm(models.Model):
    id = models.AutoField(primary_key=True)
    students_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    subjects_id = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    resumption_text = models.FloatField(default=0)
    class_work = models.FloatField(default=0)
    assignment = models.FloatField(default=0)
    midterm_exam = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    grades = models.CharField(max_length=20,default='F')
    remark = models.CharField(max_length=255,default='Poor')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class CombineEndTerm(models.Model):
    id = models.AutoField(primary_key=True)
    students_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    subjects_id = models.ForeignKey(CombineSubjects,on_delete=models.CASCADE)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    ca1 = models.FloatField(default=0)
    ca2 = models.FloatField(default=0)
    project_practical = models.FloatField(default=0)
    class_work = models.FloatField(default=0)
    sec_total = models.FloatField(default=0)
    first_total = models.FloatField(default=0)
    second_total = models.FloatField(default=0)
    endterm_exam = models.FloatField(default=0)
    total=models.FloatField(default=0)
    grades=models.CharField(max_length=20,default='F')
    effort=models.CharField(max_length=255,default='00')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class EndTerm(models.Model):
    id = models.AutoField(primary_key=True)
    students_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    subjects_id = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    ca1 = models.FloatField(default=0)
    ca2 = models.FloatField(default=0)
    project_practical = models.FloatField(default=0)
    class_work = models.FloatField(default=0)
    sec_total = models.FloatField(default=0)
    first_total = models.FloatField(default=0)
    second_total = models.FloatField(default=0)
    endterm_exam = models.FloatField(default=0)
    total=models.FloatField(default=0)
    grades=models.CharField(max_length=20,default='F')
    effort=models.CharField(max_length=255,default='00')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class ClassAverage(models.Model):
    id = models.AutoField(primary_key=True)
    students_id = models.ForeignKey(Students,on_delete=models.CASCADE)
    student_class= models.ForeignKey(Classes,on_delete=models.DO_NOTHING)
    term = models.ForeignKey(Terms,on_delete=models.DO_NOTHING)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    avg_percent = models.FloatField(default=0)
    result_type = models.FloatField(default=0)
    p_comment = models.TextField(default="An excellent performance. There is always room for improvement.")
    t_comment = models.TextField(default="Excellent performance. Keep it up and more.")
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    session_year_id=models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class LeaveReport(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_messagee = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        ordering = ('-created_at',)

class StudentExitReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_messagee = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        ordering = ('-created_at',)
  
class FeedBackStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=255)
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        ordering = ('-created_at',)

class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=255)
    Feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
<<<<<<< HEAD
=======

>>>>>>> 869102c69b442947ca113121ce958681c2b69674
    class Meta:
        ordering = ('-created_at',)
  
class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class NotificationStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class NotificationApp(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
class AffectiveDomain(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students, on_delete=models.CASCADE)
    term=models.ForeignKey(Terms, on_delete=models.CASCADE)
    session_year=models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    punctuality=models.IntegerField(default=0)
    neatness=models.IntegerField(default=0)
    initiative=models.IntegerField(default=0)
    leadership=models.IntegerField(default=0)
    health=models.IntegerField(default=0)
    attentiveness=models.IntegerField(default=0)
    perseverance=models.IntegerField(default=0)
    helping=models.IntegerField(default=0)
    co_others=models.IntegerField(default=0)
    emotional=models.IntegerField(default=0)
    result_type=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Psycomotor(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Students, on_delete=models.CASCADE)
    term=models.ForeignKey(Terms, on_delete=models.CASCADE)
    session_year=models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    handwriting=models.IntegerField(default=0)
    verbal=models.IntegerField(default=0)
    sport=models.IntegerField(default=0)
    knitting=models.IntegerField(default=0)
    result_type=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class StudyMaterial(models.Model):
    NOTE = 'note'
    ASSIGNMENT = 'assignment'
    TEXTBOOK = 'textbook'
    MATERIAL_TYPES = [
        (NOTE, 'Note'),
        (ASSIGNMENT, 'Assignment'),
        (TEXTBOOK, 'Textbook'),
    ]

    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)
    status = models.BooleanField(default=True)  # True = Visible, False = Hidden

    def __str__(self):
        return f"{self.title} ({self.get_material_type_display()})"

class ExamFile(models.Model):
    subject = models.ForeignKey('Subjects', on_delete=models.CASCADE)
    session_year = models.ForeignKey('SessionYearModel', on_delete=models.CASCADE)
    class_name = models.ForeignKey('Classes', on_delete=models.CASCADE)
    exam_pdf = models.FileField(upload_to='exam_pdfs/', validators=[FileExtensionValidator(['pdf'])])
    code = models.CharField(max_length=8, unique=True, editable=False)
    status = models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.digits, k=8))
            if not ExamFile.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return f"{self.subject.subject_name} - {self.session_year.session_start_year}/{self.session_year.session_end_year} ({self.code})"


class BilItems(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class SeniorCost(models.Model):
    id=models.AutoField(primary_key=True)
    first_new=models.IntegerField(default=0)
    first_old=models.IntegerField(default=0)
    second_new=models.IntegerField(default=0)
    second_old=models.IntegerField(default=0)
    third_new=models.IntegerField(default=0)
    third_old=models.IntegerField(default=0)
    reference_item = models.ForeignKey(BilItems,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class JuniorCost(models.Model):
    id=models.AutoField(primary_key=True)
    first_new=models.IntegerField(default=0)
    first_old=models.IntegerField(default=0)
    second_new=models.IntegerField(default=0)
    second_old=models.IntegerField(default=0)
    third_new=models.IntegerField(default=0)
    third_old=models.IntegerField(default=0)
    reference_item = models.ForeignKey(BilItems,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Bills(models.Model):
    id=models.AutoField(primary_key=True)
    students = models.ForeignKey(Students,on_delete=models.CASCADE)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    Total = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()  

class Breakdown(models.Model):
    id=models.AutoField(primary_key=True)
    reference_bill = models.ForeignKey(Bills,on_delete=models.CASCADE)
    reference_item = models.ForeignKey(BilItems,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class StudentAccount(models.Model):
    id=models.AutoField(primary_key=True)
    students = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    to_pay = models.FloatField(default=0,null=True)
    total_payed = models.FloatField(default=0,null=True)
    surplus = models.FloatField(default=0,null=True)
    latest_bill=models.FloatField(default=0,null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()



class Subscribers(models.Model):
    id=models.AutoField(primary_key=True)
    email = models.EmailField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class MailMessage(models.Model):
    id=models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=True)
    message = models.TextField(null=True)

    def __str__(self):
        return self.title

class ContactForm(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    email=models.CharField(max_length=255)
    phone=models.CharField(max_length=255)
    title=models.CharField(max_length=255)
    message=models.TextField()
    reply=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-created_at',)

class StudentApplication(models.Model):
    id=models.AutoField(primary_key=True)
    surname=models.CharField(max_length=255)
    other_name=models.CharField(max_length=255)
    dob=models.CharField(max_length=255)
    gender=models.CharField(max_length=255)
    soo=models.CharField(max_length=255)
    religion=models.CharField(max_length=255)
    contact_email=models.CharField(max_length=255)
    contact_phone=models.CharField(max_length=255)
    former_school=models.CharField(max_length=255)
    school_phone=models.CharField(max_length=255)
    applying_for=models.CharField(max_length=255)
    status=models.IntegerField(default=0)
    exam_date=models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-created_at',)
<<<<<<< HEAD
        
=======
>>>>>>> 869102c69b442947ca113121ce958681c2b69674
class OldResults(models.Model):
    id=models.AutoField(primary_key=True)
    students = models.ForeignKey(Students,on_delete=models.CASCADE)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    result_type = models.IntegerField(default=0)
    result_file = models.FileField()
    classes = models.ForeignKey(Classes, on_delete=models.DO_NOTHING, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        ordering = ('-created_at',)
<<<<<<< HEAD
=======


class LessionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    weeks = models.CharField(max_length=255)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    subjects = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    plan_file = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        ordering = ('-created_at',)


>>>>>>> 869102c69b442947ca113121ce958681c2b69674


# G and C
class OldCummulative(models.Model):
    id = models.AutoField(primary_key=True)
    students = models.ForeignKey(Students,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    cummulative_file = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
    
class SubjectStream(models.Model):
    students = models.ForeignKey(Students,on_delete=models.CASCADE)
    choice = models.CharField(max_length=20)
    subj_choice = models.TextField()
    career1 = models.CharField(max_length=100)
    career2 = models.CharField(max_length=100)
    career3 = models.CharField(max_length=100)
    reason1 = models.TextField()
    passsubj1 = models.CharField(max_length=100)
    passsubj2 = models.CharField(max_length=100)
    passsubj3 = models.CharField(max_length=100, blank=True)
    passsubj4 = models.CharField(max_length=100, blank=True)
    passsubj5 = models.CharField(max_length=100, blank=True)
    passsubj6 = models.CharField(max_length=100, blank=True)
    failsubj1 = models.CharField(max_length=100)
    failsubj2 = models.CharField(max_length=100)
    failsubj3 = models.CharField(max_length=100, blank=True)
    failsubj4 = models.CharField(max_length=100, blank=True)
    failsubj5 = models.CharField(max_length=100, blank=True)
    failsubj6 = models.CharField(max_length=100, blank=True)
    pcareer = models.CharField(max_length=100)
    preason = models.TextField()
    pname = models.CharField(max_length=100)
    email = models.EmailField()
    parentcode = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class LessionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    weeks = models.CharField(max_length=255)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    subjects = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    notes = models.CharField(max_length=255, null=True, blank=True)
    plan_file = models.FileField()
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-created_at',)

# Store/Tuckshop
class Item(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    package_type = models.CharField(max_length=50, choices=[('box', 'Box'), ('bag', 'BAG'), ('crate', 'CRATE'), ('satchets', 'SATCHETS'),('carton', 'CARTON'),('pieces', 'PIECES'),('jarican', 'JARICAN'),('measure', 'MEASURE'),('roll', 'ROLL'),('tray', 'TRAY'),('kilo', ' KILO'),('packs', 'PACKS'),('tin', 'TIN'),('gram', 'GRAMS'),('litre', 'LITRE'),('bunch', 'BUNCH'),('tubers', 'TUBERS'),('crowns', 'CROWNS'),('slices', 'SLICES'),('cups', 'CUPS'),('baskets', 'BASKETS'),('foot', 'FOOT')])
    description = models.TextField()
    note = models.TextField()
    expected_marketprice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name




class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    notes = models.TextField()
    updated_at = models.DateTimeField(auto_now_add=True)


class StockLog(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    general_note = models.TextField()
    stock_type = models.CharField(max_length=50, choices=[('incoming', 'Incoming'), ('outgoing', 'Outgoing')])
    general_date = models.DateField()
    quantity_at_entry = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_after_entry = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price_at_entry = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price_after_entry = models.DecimalField(max_digits=10, decimal_places=2)




class DamageReport(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField()
    image1 = models.ImageField(upload_to='damage_reports/')
    image2 = models.ImageField(upload_to='damage_reports/')

    def __str__(self):
        return f"{self.item.name} - {self.date}"
        

class SiteControls(models.Model):
    id = models.AutoField(primary_key=True)
    c_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    status=models.IntegerField(default=0)
    count_value=models.IntegerField(default=0)
    objects = models.Manager()
    
class EntryAttestation(models.Model):
    id = models.AutoField(primary_key=True)
    remark = models.CharField(max_length=255)
    term = models.ForeignKey(Terms,on_delete=models.CASCADE)
    result_type=models.IntegerField(default=0)
    subjects = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
    class Meta:
        unique_together = ('term', 'session_year', 'result_type', 'subjects')


class GncQuestion(models.Model):
    FIELD_TYPE_CHOICES = [
        ('Science', 'Science'),
        ('Humanities', 'Humanities'),
        ('Business', 'Business'),
        ('Technology', 'Technology')
    ]
    
    FORM_TYPE_CHOICES = [
        ('A', 'Form A'),
        ('B', 'Form B'),
        ('C', 'Form C'),
        ('D', 'Form D'),
        ('E', 'Form E'),
        ('F', 'Form F'),
        ('G', 'Form G'),
        ('H', 'Form H'),
        ('I', 'Form I'),
        ('J', 'Form J'),
        ('K', 'Form K'),
        ('L', 'Form L'),
        ('M', 'Form M'),
        ('N', 'Form N'),
        ('O', 'Form O'),
        ('P', 'Form P'),
        ('Q', 'Form Q'),
        ('R', 'Form R'),
        ('S', 'Form S')
    ]

    text = models.CharField(max_length=255)
    field_type = models.CharField(max_length=100, choices=FIELD_TYPE_CHOICES)
    form_type = models.CharField(max_length=100, choices=FORM_TYPE_CHOICES)

    OPTIONS = {
        5: "Like very much",
        4: "Like",
        3: "Indifferent",
        2: "Dislike",
        1: "Dislike very much"
    }

    def __str__(self):
        return self.text

class GncResponse(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    question = models.ForeignKey(GncQuestion, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255, blank=True, null=True)
    answer_choice = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'question')
        
    def __str__(self):
        return f"{self.student.first_name} - {self.question.text}"


@receiver(post_save,sender=CustomUser) 
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        if instance.user_type==1:
            Admin.objects.create(admin=instance)
        if instance.user_type==2:
            Staff.objects.create(admin=instance)
        if instance.user_type==3:
            Students.objects.create(admin=instance,class_id=Classes.objects.get(id=1),session_year_id=SessionYearModel.objects.get(id=1),class_category=ClassCategories.objects.get(id=1),address="",profile_pic="",gender="")
        if instance.user_type==4:
            Staff.objects.create(admin=instance)
        if instance.user_type==5:
            Staff.objects.create(admin=instance)
        if instance.user_type==6:
            Staff.objects.create(admin=instance)
        if instance.user_type==7:
            Staff.objects.create(admin=instance)
@receiver(post_save,sender=CustomUser)
def save_user_profile(sender,instance,**kwargs):
    if instance.user_type==1:
        instance.admin.save()
    if instance.user_type==2:
        instance.staff.save()
    if instance.user_type==3:
        instance.students.save()
    if instance.user_type==4:
        instance.staff.save()
    if instance.user_type==5:
        instance.staff.save()
    if instance.user_type==6:
        instance.staff.save()
    if instance.user_type==7:
        instance.staff.save()
        

