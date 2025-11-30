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



# --------------------------------------------------------
# SCHOOL BRANCH
# --------------------------------------------------------
@admin.register(SchoolBranch)
class SchoolBranchAdmin(GuardedModelAdmin): 
    compressed_fields = False 
    
    warn_unsaved_form = True
    
    list_display = ("name", "phone_number", "email", "created_at")
    search_fields = ("name", "email", "phone_number")
    list_filter = ("created_at",)
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    
    def has_module_permission(self, request):
        if super().has_module_permission(request):
            return True
        return self.get_model_objects(request).exists()

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        data = self.get_model_objects(request)
        return data

    def get_model_objects(self, request, action=None, klass=None):
        opts = self.opts
        actions = [action] if action else ['view','edit','delete']
        klass = klass if klass else opts.model
        model_name = klass._meta.model_name
        return get_objects_for_user(user=request.user, perms=[f'{perm}_{model_name}' for perm in actions], klass=klass, any_perm=True)

    def has_permission(self, request, obj, action):
        opts = self.opts
        code_name = f'{action}_{opts.model_name}'
        if obj:
            return request.user.has_perm(f'{opts.app_label}.{code_name}', obj)
        else:
            return self.get_model_objects(request).exists()

    def has_view_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'view')

    def has_change_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'change')

    def has_delete_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'delete')


# --------------------------------------------------------
# USER ADMIN
# --------------------------------------------------------
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
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
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


# --------------------------------------------------------
# USER PROFILE
# --------------------------------------------------------
@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ("user", "school_branch", "website")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    list_filter = ("school_branch",)
    ordering = ("user__email",)


# --------------------------------------------------------
# ADDRESS
# --------------------------------------------------------
@admin.register(Address)
class AddressAdmin(GuardedModelAdmin):
    list_display = ("street", "city", "state", "postal_code", "country")
    search_fields = ("street", "city", "state", "postal_code", "country")
    list_filter = ("country", "state", "city")
    ordering = ("city", "street")


# --------------------------------------------------------
# TEACHER PROFILE
# --------------------------------------------------------
@admin.register(TeacherProfile)
class TeacherProfileAdmin(GuardedModelAdmin):
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
class StudentProfileAdmin(GuardedModelAdmin):
    list_display = ("user", )
    search_fields = ("user__email", )
  #  list_filter = (,)
    ordering = ("user__email",)

  #  readonly_fields = (,)


# --------------------------------------------------------
# GUARDIAN PROFILE
# --------------------------------------------------------
@admin.register(GuardianProfile)
class GuardianProfileAdmin(ModelAdmin):
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
class AdminProfileAdmin(ModelAdmin):
    list_display = ("user", "department", "school_branch")
    search_fields = ("user__email", "department")
    list_filter = ("department", "school_branch")
    ordering = ("user__email",)
