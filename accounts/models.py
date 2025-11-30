from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group 

from django.contrib.auth.base_user import BaseUserManager 

class Address(models.Model):

    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, verbose_name="Province")
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100) 
    
    def __str__(self):
        return self.street

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)

class SchoolBranch(models.Model):
    name = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 
    

class User(AbstractUser):
    
    username = None
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  
    
    objects = UserManager()

    def __str__(self):
        return self.email
    
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    user_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    school_branch = models.ForeignKey(SchoolBranch, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self): 
        return f"{self.user.email} Profile"
    

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.ManyToManyField("school.Subject", null=True, blank=True)
    bio = models.TextField(blank=True)
    school_branch = models.ForeignKey(SchoolBranch, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        teacher_group, _ = Group.objects.get_or_create(name="Teachers")
        if teacher_group not in self.user.groups.all():
            raise ValidationError("User must belong to the Teachers group to create a TeacherProfile.")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs) 
    
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_grade = models.ForeignKey("school.Grades", on_delete=models.SET_NULL, null=True, blank=True)


    def clean(self):
        student_group, _ = Group.objects.get_or_create(name="Students")
        if student_group not in self.user.groups.all():
            raise ValidationError("User must belong to the Students group to create a StudentProfile.")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs) 
    
    def __str__(self):
        return f"{self.user.email} Student Profile"
    
class GuardianProfile(models.Model): 
    
    TEXT_CHOICES = [('mother', 'Mother'), ('father', 'Father'), ('guardian', 'Guardian'), ('other', 'Other')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=100, choices=TEXT_CHOICES)
    contact_number = models.CharField(max_length=15)
    pupil = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="guardian_profiles")

    def clean(self):
        guardian_group, _ = Group.objects.get_or_create(name="Guardians")
        if guardian_group not in self.user.groups.all():
            raise ValidationError("User must belong to the Guardians group to create a GuardianProfile.")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs) 
    
    def __str__(self):
        return f"{self.user.email} Guardian Profile"    
    
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    school_branch = models.OneToOneField(SchoolBranch, on_delete=models.SET_NULL, null=True, blank=True)
 
    def clean(self):
        admin_group, _ = Group.objects.get_or_create(name="Admins")
        if admin_group not in self.user.groups.all():
            raise ValidationError("User must belong to the Admins group to create an AdminProfile.")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs) 
    
    def __str__(self):
        return f"{self.user.email} Admin Profile" 
    
