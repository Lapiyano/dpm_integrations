from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.contrib.auth import get_user_model
from applications.models import *
from .models import *
from school.models import *
from guardian.shortcuts import assign_perm 
from django.conf import settings


@receiver(post_migrate)
def setup_groups_permissions(sender, **kwargs):

    admin, _ = Group.objects.get_or_create(name="Admins")
    teachers, _ = Group.objects.get_or_create(name="Teachers")
    students, _ = Group.objects.get_or_create(name="Students")
    guardian, _ = Group.objects.get_or_create(name="Guardians")

    # Setup admin permissions for accounts
    admin_permissions = Permission.objects.filter(
        content_type__in = 
            ContentType.objects.get_for_models(
          Grades, Subject, SchoolBranch, JobListing
        ).values()
        
        ,
        codename__in=["view_grades", "view_subject", "view_schoolbranch", "view_joblisting"]
    )
    admin.permissions.set(admin_permissions)  
    
    # Setting up Teachers for account permission  
    teacher_permissions = Permission.objects.filter( 
        content_type__in = ContentType.objects.get_for_models( 
            TeacherProfile, SchoolBranch, Grades, AssessmentType, Subject, JobListing
        )   .values(), 
        codename__in = ["view_teacherprofile", "view_schoolbranch", "view_grades", "view_assessmenttype", "view_subject", "view_joblisting"]   
    )  
    
    teachers.permissions.set(teacher_permissions)
    
    #Setiing up Guardian permissions for account models 
    guardian_permissions = Permission.objects.filter( 
        content_type__in = ContentType.objects.get_for_models( 
        SchoolBranch, Grades, Subject, JobListing
        ).values(), 
        codename__in = ["view_schoolbranch", "view_grades", "view_subject", "view_joblisting"]   
    )   
    
    guardian.permissions.set(guardian_permissions)
    
    #Setiing up STUDENT permissions for account models 
    students_permissions = Permission.objects.filter( 
        content_type__in = ContentType.objects.get_for_models( 
        SchoolBranch, Grades, Subject, StudentProfile, JobListing
        ).values(), 
        codename__in = ["view_schoolbranch", "view_grades", "view_subject", "view_studentprofile", "view_joblisting"]   
    )  
    students.permissions.set(students_permissions)
    
    
@receiver(post_save, sender=User)
def user_post_save(sender, **kwargs):
    """
    Create a Profile instance for all newly created User instances. We only
    run on user creation to avoid having to check for existence on each call
    to User.save.
    """
    user, created = kwargs["instance"], kwargs["created"]
    if created:
        from accounts.models import UserProfile
        profile = UserProfile.objects.create(pk=user.pk, user=user)
        assign_perm("change_user", user, user)
        assign_perm("change_userprofile", user, profile) 


@receiver(post_save, sender=ClassApplication)
def classapplication_post_save(sender, instance, created, **kwargs):
    """
    Give permissions when a ClassApplication is created/updated.
    The student should be able to view their own application.
    """
    user = instance.student
    
    # Give the student permission to view their own application
    assign_perm("view_classapplication", user, instance)

@receiver(post_save, sender=Enrollment)
def enrollment_post_save(sender, instance, created, **kwargs):

    user = instance.user

    # 1) ADD USER TO "Students" GROUP
    students_group, _ = Group.objects.get_or_create(name="Students")
    user.groups.add(students_group)

    # 2) GIVE OBJECT PERMISSION FOR THIS ENROLLMENT
    # Use "view" because you want students to see their enrollment record
    assign_perm("view_enrollment", user, instance)
    assign_perm("view_classroom", user, instance.classroom)
    assign_perm("view_classapplication", user, instance.ClassApplication)

    # 3) CREATE STUDENT PROFILE IF NOT EXISTS
    StudentProfile.objects.get_or_create(user=user)
    


@receiver(post_save, sender=JobApplication)
def jobapplication_post_save(sender, instance, created, **kwargs):
    """
    Give the applicant permission to view their own job application.
    """
    user = instance.user
    
    # Give the user permission to view their own job application
    assign_perm("view_jobapplication", user, instance)