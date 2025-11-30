from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.contrib.auth import get_user_model
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
          Grades, Subject, SchoolBranch
        ).values()
        
        ,
        codename__in=["view_grades", "view_subject", "view_schoolbranch"]
    )
    admin.permissions.set(admin_permissions)  
    
    # Setting up Teachers for account permission  
    teacher_permissions = Permission.objects.filter( 
        content_type__in = ContentType.objects.get_for_models( 
            TeacherProfile, SchoolBranch, Grades, AssessmentType, Subject
        )   .values(), 
        codename__in = ["view_teacherprofile", "view_schoolbranch", "view_grades", "view_assessmenttype", "view_subject"]   
    )  
    
    teachers.permissions.set(teacher_permissions)
    
    #Setiing up Guardian permissions for account models 
    guardian_permissions = Permission.objects.filter( 
        content_type__in = ContentType.objects.get_for_models( 
        SchoolBranch, Grades, Subject
        ).values(), 
        codename__in = ["view_schoolbranch", "view_grades", "view_subject"]   
    )   
    
    guardian.permissions.set(guardian_permissions)
    
    #Setiing up STUDENT permissions for account models 
    students_permissions = Permission.objects.filter( 
        content_type__in = ContentType.objects.get_for_models( 
        SchoolBranch, Grades, Subject, StudentProfile
        ).values(), 
        codename__in = ["view_schoolbranch", "view_grades", "view_subject", "view_studentprofile"]   
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
        
