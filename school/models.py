from django.db import models
from accounts.models import Address 
from django.utils import timezone
from datetime import timedelta  

from accounts.models import SchoolBranch

class Grades(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 
    
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}" 
    
class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    school_branch = models.ForeignKey(SchoolBranch, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.grade.name}"  
    
class ClassSession(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.classroom.name} - {self.start_time} to {self.end_time}"

class Enrollment(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    end_date = models.DateField(null=True, blank=True) 
    
    def save(self, *args, **kwargs):
        if not self.end_date:
            # If end_date not set, give it a default
            self.end_date = (self.created_at or timezone.now()) + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} enrolled in {self.classroom.name}"
    
class Assignment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assessment_type = models.ForeignKey("AssessmentType", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} for {self.classroom.name}" 
    
    @property
    def classroom(self):
        return self.enrollment.classroom 

class AssessmentType(models.Model): 
    
    TEXT_CHOICES = [
        ("quiz", "Quiz"),
        ("exam", "Exam"),
        ("assignment", "Assignment"),
        ("term test", "Term Test"),
    ]
                                          
    name = models.CharField(max_length=100, choices=TEXT_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class GradeRecord(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.assessment_type.name}: {self.score}/{self.max_score}"
    
    @property
    def classroom(self):
        return self.enrollment.classroom
    
class AttendanceRecord(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[("present", "Present"), ("absent", "Absent"), ("excused", "Excused")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.date}: {self.status}"
    
    @property
    def classroom(self):
        return self.enrollment.classroom