from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Grades, Subject, ClassRoom, ClassSession, Enrollment,
    Assignment, AssessmentType, GradeRecord, AttendanceRecord
)
from accounts.admin_mixins import GuardianPermissionMixin
from guardian.shortcuts import get_objects_for_user

# --------------------------------------------------------
# GRADES
# --------------------------------------------------------
@admin.register(Grades)
class GradesAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


# --------------------------------------------------------
# SUBJECTS
# --------------------------------------------------------
@admin.register(Subject)
class SubjectAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("code", "name", "created_at")
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")


# --------------------------------------------------------
# CLASSROOM
# --------------------------------------------------------
@admin.register(ClassRoom)
class ClassRoomAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("name", "grade", "school_branch", "created_at")
    search_fields = ("name", "grade__name", "school_branch__name")
    list_filter = ("grade", "school_branch", "subjects")
    ordering = ("name",)

    filter_horizontal = ("subjects",)
    readonly_fields = ("created_at", "updated_at")


# --------------------------------------------------------
# CLASS SESSION
# --------------------------------------------------------
@admin.register(ClassSession)
class ClassSessionAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("classroom", "start_time", "end_time")
    search_fields = ("classroom__name",)
    list_filter = ("classroom", "start_time")
    ordering = ("start_time",)
    readonly_fields = ("created_at", "updated_at")


# --------------------------------------------------------
# ASSIGNMENT INLINE (For Enrollment Admin)
# --------------------------------------------------------
class AssignmentInline(GuardianPermissionMixin, admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ("title", "assessment_type", "due_date")
    readonly_fields = ("created_at", "updated_at")


# --------------------------------------------------------
# GRADED RECORD INLINE (For Enrollment Admin)
# --------------------------------------------------------
class GradeRecordInline(GuardianPermissionMixin, admin.TabularInline):
    model = GradeRecord
    extra = 0
    readonly_fields = ("date_recorded",)


# --------------------------------------------------------
# ATTENDANCE INLINE (For Enrollment Admin)
# --------------------------------------------------------
class AttendanceInline(GuardianPermissionMixin, admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    readonly_fields = ("created_at",)


# --------------------------------------------------------
# ENROLLMENT
# --------------------------------------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("user", "classroom", "is_active", "enrollment_date", "end_date")
    search_fields = ("user__email", "classroom__name")
    list_filter = ("is_active", "classroom", "enrollment_date")
    ordering = ("user__email",)

    readonly_fields = ("created_at", "updated_at", "enrollment_date")

    inlines = [AssignmentInline, GradeRecordInline, AttendanceInline]

    
# --------------------------------------------------------
# ASSIGNMENT
# --------------------------------------------------------
@admin.register(Assignment)
class AssignmentAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("title", "enrollment", "assessment_type", "due_date")
    search_fields = ("title", "enrollment__user__email", "enrollment__classroom__name")
    list_filter = ("assessment_type", "due_date")
    ordering = ("due_date",)

    readonly_fields = ("created_at", "updated_at")


# --------------------------------------------------------
# ASSESSMENT TYPE
# --------------------------------------------------------
@admin.register(AssessmentType)
class AssessmentTypeAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


# --------------------------------------------------------
# GRADE RECORDS
# --------------------------------------------------------
@admin.register(GradeRecord)
class GradeRecordAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("enrollment", "assessment_type", "score", "max_score", "date_recorded")
    search_fields = ("enrollment__user__email", "assessment_type__name")
    list_filter = ("assessment_type", "date_recorded")
    ordering = ("-date_recorded",)
    readonly_fields = ("date_recorded",)


# --------------------------------------------------------
# ATTENDANCE RECORDS
# --------------------------------------------------------
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(GuardianPermissionMixin, ModelAdmin):
    list_display = ("enrollment", "date", "status")
    search_fields = ("enrollment__user__email",)
    list_filter = ("status", "date")
    ordering = ("-date",)
    readonly_fields = ("created_at",)
