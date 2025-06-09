from django.db import models
from accounts.models import Students, Subjects

# Create your models here.

class JobApp(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    email=models.CharField(max_length=255)
    phone=models.CharField(max_length=255)
    qualification=models.CharField(max_length=255)
    letter = models.FileField()
    cv = models.FileField()
    status=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-created_at',)

class Events(models.Model):
    id=models.AutoField(primary_key=True)
    event_title=models.CharField(max_length=255)
    event_year=models.CharField(max_length=255)
    event_month=models.CharField(max_length=255)
    event_day=models.CharField(max_length=255)
    future_image = models.FileField()
    event_location=models.CharField(max_length=255)
    blog_post=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-created_at',)
        
        
class CBTresult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject1 = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='subject1')
    subject2 = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='subject2')
    subject3 = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='subject3')
    subject4 = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='subject4')
    sub1 = models.IntegerField(default=0)
    sub2 = models.IntegerField(default=0)
    sub3 = models.IntegerField(default=0)
    sub4 = models.IntegerField(default=0)
    Total = models.IntegerField(default=0)
    entrydate = models.CharField(max_length=255,default="00-00-000")
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-entrydate',)