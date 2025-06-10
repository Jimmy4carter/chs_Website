from django.db import models

from accounts.models import CustomUser, SessionYearModel, Staff, Students, Terms

# Create your models here.
class Hostel(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    Sex=models.CharField(max_length=255)
    room_count=models.IntegerField(default=0)
    capacity=models.IntegerField(default=0)
    hparent1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hparent2 = models.CharField(max_length=255)
    hprefect = models.ForeignKey(Students,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Rooms(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    capacity=models.IntegerField(default=0)
    hostels = models.ForeignKey(Hostel,on_delete=models.CASCADE)
    roomhead = models.ForeignKey(Students,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
    def get_members(self):
        # Filter allocations for active session (status=1)
        return Allocations.objects.filter(
            room=self,
            sessionid__status=1
        )

    def get_members_count(self):
        return self.get_members().count()

class Allocations(models.Model):
    id=models.AutoField(primary_key=True)
    student=models.ForeignKey(Students, on_delete=models.CASCADE)
    room=models.ForeignKey(Rooms, on_delete=models.CASCADE)
    allocator=models.ForeignKey(Staff, on_delete=models.CASCADE)
    sessionid = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Logbook(models.Model):
    id=models.AutoField(primary_key=True)
    rdate = models.CharField(max_length=255)
    report=models.TextField()
    reporter=models.ForeignKey(Staff, on_delete=models.CASCADE)
    sessionid = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    

class StudentEthosRecords(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    term = models.ForeignKey(Terms, on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
   # Positive Ethos Attributes
    leadership = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    neatness = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    room_represent_compet = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    room_represent_inspect = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    selfconfidence = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    team_spirit = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    return_lost_items = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    obidience_to_staff = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    obidience_to_rules = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    volunteerism = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    reporting_unacceptable_behavior = models.PositiveSmallIntegerField(default=0, choices=[
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    prayerfullness = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent')
    ])
    
    
    
    # Negative Ethos Attributes
    loitering = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    immoral_relation_conduct = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    poor_timing = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    negative_influence = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    noise_making = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    hostel_disobidience = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    bullying_fighting = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    negative_civil = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    gossip = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    avoiding_meals = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    carelessness_personal = models.PositiveSmallIntegerField(default=0, choices=[
        (0, '---'),
        (1, 'Poor'),
        (2, 'Very Poor'),
        (3, 'Bad'),
        (4, 'Very Bad'),
        (5, 'Very Very Bad')
    ])
    
    

    remark = models.TextField(blank=True, null=True)
    result_type = models.PositiveSmallIntegerField(default=0, choices=[
        (0, 'First Half'),
        (1, 'End of Term'),
    ])

    objects = models.Manager()

    def __str__(self):
        return f"{self.student_id} - {self.term} - {self.session_year}"
        
    class Meta:
        unique_together = ('student_id', 'term', 'session_year', 'result_type')


