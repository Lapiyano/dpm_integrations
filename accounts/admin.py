from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm

from .models import (
    SchoolBranch, User, UserProfile, Address,
    TeacherProfile, StudentProfile, GuardianProfile, AdminProfile
) 
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user
from .admin_mixins import GuardianPermissionMixin


# --------------------------------------------------------
# SCHOOL BRANCH
# --------------------------------------------------------
@admin.register(SchoolBranch)
class SchoolBranchAdmin(GuardedModelAdmin, GuardianPermissionMixin): 
    compressed_fields = False 
    
    warn_unsaved_form = True
    
    list_display = ("name", "phone_number", "email", "created_at")
    search_fields = ("name", "email", "phone_number")
    list_filter = ("created_at",)
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

# --------------------------------------------------------
# USER ADMIN
# --------------------------------------------------------
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin,GuardianPermissionMixin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ("email", "first_name", "last_name", "is_active", "is_staff", "is_admin")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    list_filter = ("is_active", "is_staff", "is_admin", "groups") 
    
    list_filter_sheet = True

    fieldsets = (
        ("Login Details", {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "is_admin", "groups", "user_permissions")
        }),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    add_fieldsets = (
        ("Create User", {
            "classes": ("wide",),
            "fields": (
                "email", "first_name", "last_name",
                "password1", "password2",
                "is_active", "is_staff", "is_superuser", "is_admin"
            )
        }),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin, GuardianPermissionMixin):
    pass


# --------------------------------------------------------
# USER PROFILE
# --------------------------------------------------------
@admin.register(UserProfile)
class UserProfileAdmin(GuardianPermissionMixin, ModelAdmin ):
    list_display = ("user", "school_branch", "website")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    list_filter = ("school_branch",)
    ordering = ("user__email",)


# --------------------------------------------------------
# ADDRESS
# --------------------------------------------------------
@admin.register(Address)
class AddressAdmin(GuardedModelAdmin, GuardianPermissionMixin):
    list_display = ("street", "city", "state", "postal_code", "country")
    search_fields = ("street", "city", "state", "postal_code", "country")
    list_filter = ("country", "state", "city")
    ordering = ("city", "street")


# --------------------------------------------------------
# TEACHER PROFILE
# --------------------------------------------------------
@admin.register(TeacherProfile)
class TeacherProfileAdmin(GuardedModelAdmin, GuardianPermissionMixin):
    list_display = ("user", "school_branch")
    search_fields = ("user__email", "user__first_name", "user__last_name", )
    list_filter = ("school_branch",)
    ordering = ("user__email",)

    readonly_fields = ()  # left empty intentionally
    # clean() already validates the group membership


# --------------------------------------------------------
# STUDENT PROFILE
# --------------------------------------------------------
@admin.register(StudentProfile)
class StudentProfileAdmin(GuardianPermissionMixin, GuardedModelAdmin):
    list_display = ("user", )
    search_fields = ("user__email", )
  #  list_filter = (,)
    ordering = ("user__email",)

  #  readonly_fields = (,)


# --------------------------------------------------------
# GUARDIAN PROFILE
# --------------------------------------------------------
@admin.register(GuardianProfile)
class GuardianProfileAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("user", "relationship", "contact_number", "pupil")
    search_fields = (
        "user__email",
        "contact_number",
        "relationship",
        "pupil__email",
    )
    list_filter = ("relationship",)
    ordering = ("user__email",)


# --------------------------------------------------------
# ADMIN PROFILE
# --------------------------------------------------------
@admin.register(AdminProfile)
class AdminProfileAdmin(GuardianPermissionMixin, ModelAdmin ):
    list_display = ("user", "department", "school_branch")
    search_fields = ("user__email", "department")
    list_filter = ("department", "school_branch")
    ordering = ("user__email",)
