from django.db import models
from accounts.models import User
from school.models import ClassRoom

class JobListing(models.Model):
    JOB_TYPES = [
        ("TUTOR", "Tutor"),
        ("ADMIN", "Admin"),
    ]

    job_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPES,
        default="TUTOR"
    )
    description = models.TextField(null=True, blank=True)
    school_branch = models.ForeignKey("accounts.SchoolBranch", on_delete=models.CASCADE, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_job_type_display()})"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("REVIEWED", "Reviewed"),
        ("SHORTLISTED", "Shortlisted"),
        ("INTERVIEW", "Interview"),
        ("REJECTED", "Rejected"),
    ]

    application_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default="PENDING"
    )

    def __str__(self):
        return f"{self.user.username} -> {self.job.title} ({self.get_status_display()})"




class ClassApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('enrolled', 'Enrolled'),  # Add this new status
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_applications')
    class_applied = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'class_applied')

    def __str__(self):
        return f"{self.student.username} -> {self.class_applied.name} ({self.status})"