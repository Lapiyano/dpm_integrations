from django.contrib import admin
from accounts.admin_mixins import GuardianPermissionMixin

# Register your models here.
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.http import JsonResponse
from .models import ClassApplication, JobApplication, JobListing
from school.models import Enrollment
from guardian.shortcuts import get_objects_for_user
from guardian.admin import GuardedModelAdmin
# -----------------------------
# JobListing Admin
# -----------------------------
@admin.register(JobListing)
class JobListingAdmin(GuardianPermissionMixin, admin.ModelAdmin):
    list_display = ['job_id', 'title', 'job_type', 'school_branch', 'salary']
    list_filter = ['job_type', 'school_branch']
    search_fields = ['title', 'description']

    def get_list_display(self, request):
        base = ['job_id', 'title', 'job_type', 'school_branch', 'salary']

        # Only superuser OR user in Admins group sees "view applications"
        if request.user.is_superuser or request.user.groups.filter(name="Admins").exists():
            return base + ['view_applications_link']

        return base  # Do NOT show the link

    def view_applications_link(self, obj):
        return format_html(
            '<a class="button" style="background-color:#007bff; color:white; border-radius:8px; padding:2px 8px; text-decoration:none;" href="{}">View Applications</a>',
            reverse('admin:view_job_applications', args=[obj.pk])
        )
    view_applications_link.short_description = 'Applications'

 

# -----------------------------
# JobApplication Admin
# -----------------------------
from django.contrib import admin, messages
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from guardian.admin import GuardedModelAdmin

from .models import JobApplication, JobListing
from accounts.models import AdminProfile


@admin.register(JobApplication)
class JobApplicationAdmin(GuardedModelAdmin):
    list_display = ['application_id', 'job', 'user', 'status']
    list_filter = ['status', 'job']
    search_fields = ['user__username', 'user__email', 'job__title']

    actions = ['mark_reviewed', 'mark_shortlisted', 'mark_interview', 'mark_rejected']

    # ---------------------------------------------------------------------
    # PERMISSION HELPERS
    # ---------------------------------------------------------------------
    def _is_admin(self, request):
        return request.user.is_superuser or request.user.groups.filter(name="Admins").exists()

    def _deny_if_not_admin(self, request):
        if not self._is_admin(request):
            return HttpResponseForbidden("You do not have permission.")

    # ---------------------------------------------------------------------
    # ADMIN PERMISSIONS
    # ---------------------------------------------------------------------
    def has_view_permission(self, request, obj=None):
        # All staff can view THEIR OWN applications
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        # Only admins can change statuses
        return self._is_admin(request)

    def has_delete_permission(self, request, obj=None):
        # Only admins can delete
        return self._is_admin(request)

    def has_module_permission(self, request):
        # Anyone who is staff (including low-level staff) can see the module
        return request.user.is_staff

    # ---------------------------------------------------------------------
    # QUERYSET FILTERING
    # ---------------------------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # SUPERUSER → sees everything
        if request.user.is_superuser:
            return qs

        # ADMINS → see applications for jobs in THEIR BRANCH
        if request.user.groups.filter(name="Admins").exists():
            profile = getattr(request.user, "adminprofile", None)
            if profile and profile.school_branch:
                return qs.filter(job__school_branch=profile.school_branch)
            return qs.none()

        # STAFF (non-admin) → see ONLY their own applications
        return qs.filter(user=request.user)

    # ---------------------------------------------------------------------
    # REMOVE ACTIONS FOR STAFF USERS
    # ---------------------------------------------------------------------
    def get_actions(self, request):
        if self._is_admin(request):
            return super().get_actions(request)
        return {}  # no actions for normal staff

    # ---------------------------------------------------------------------
    # CUSTOM URLS
    # ---------------------------------------------------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:job_id>/applications/', self.admin_site.admin_view(self.job_applications_view),
                 name='view_job_applications'),

            path('<int:application_id>/review/', self.admin_site.admin_view(self.review_application),
                 name='review_job_application'),

            path('<int:application_id>/shortlist/', self.admin_site.admin_view(self.shortlist_application),
                 name='shortlist_job_application'),

            path('<int:application_id>/interview/', self.admin_site.admin_view(self.interview_application),
                 name='interview_job_application'),

            path('<int:application_id>/reject/', self.admin_site.admin_view(self.reject_application),
                 name='reject_job_application'),

            path('confirm-action/', self.admin_site.admin_view(self.confirm_action),
                 name='confirm_job_action'),
        ]
        return custom_urls + urls

    # ---------------------------------------------------------------------
    # CUSTOM VIEWS
    # ---------------------------------------------------------------------
    def job_applications_view(self, request, job_id):
        """List applications for a job."""
        # Staff users cannot see this URL — only admins
        if not self._is_admin(request):
            return HttpResponseForbidden("Not allowed.")

        job = get_object_or_404(JobListing, pk=job_id)
        applications = JobApplication.objects.filter(job=job)

        return render(request, 'admin/job_applications_list.html', {
            **self.admin_site.each_context(request),
            'job': job,
            'applications': applications
        })

    def confirm_action(self, request):
        """Confirm modal for actions."""
        if not self._is_admin(request):
            return HttpResponseForbidden("Not allowed.")

        if request.method == 'POST':
            action = request.POST.get('action')
            application_id = request.POST.get('application_id')

            if action and application_id:
                return JsonResponse({
                    'confirmed': True,
                    'redirect_url': reverse(f'admin:{action}_job_application', args=[application_id])
                })

        return JsonResponse({'confirmed': False})

    # ---------------------------------------------------------------------
    # STATUS ACTION HELPERS
    # ---------------------------------------------------------------------
    def _set_status(self, request, application_id, status, message):
        if not self._is_admin(request):
            return HttpResponseForbidden("Not allowed.")

        application = get_object_or_404(JobApplication, pk=application_id)
        application.status = status
        application.save()

        messages.success(request, message.format(application.user.username))
        return redirect('admin:view_job_applications', job_id=application.job.pk)

    def review_application(self, request, application_id):
        return self._set_status(request, application_id, "REVIEWED", "{}'s application marked as Reviewed.")

    def shortlist_application(self, request, application_id):
        return self._set_status(request, application_id, "SHORTLISTED", "{}'s application marked as Shortlisted.")

    def interview_application(self, request, application_id):
        return self._set_status(request, application_id, "INTERVIEW", "{}'s application marked for Interview.")

    def reject_application(self, request, application_id):
        return self._set_status(request, application_id, "REJECTED", "{}'s application rejected.")

    # ---------------------------------------------------------------------
    # BULK ACTIONS (Admins only)
    # ---------------------------------------------------------------------
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(status="REVIEWED")
        self.message_user(request, f"{updated} applications marked as Reviewed.", messages.SUCCESS)

    def mark_shortlisted(self, request, queryset):
        updated = queryset.update(status="SHORTLISTED")
        self.message_user(request, f"{updated} applications marked as Shortlisted.", messages.SUCCESS)

    def mark_interview(self, request, queryset):
        updated = queryset.update(status="INTERVIEW")
        self.message_user(request, f"{updated} applications marked for Interview.", messages.SUCCESS)

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status="REJECTED")
        self.message_user(request, f"{updated} applications rejected.", messages.WARNING)


# -----------------------------
# ClassApplication Admin
# -----------------------------
@admin.register(ClassApplication)
class ClassApplicationAdmin(GuardianPermissionMixin, admin.ModelAdmin ):
    list_display = ['id', 'student', 'class_applied', 'status', 'applied_at', 'list_actions']
    list_filter = ['status', 'class_applied__grade', 'applied_at']
    search_fields = ['student__username', 'student__email', 'class_applied__name']
    actions = ['approve_applications', 'reject_applications', 'enroll_students']

    def list_actions(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button button-small button-success confirm-action" style="margin-right:5px;" href="{}" data-action="approve" data-student="{}">Approve</a>'
                '<a class="button button-small button-danger confirm-action" href="{}" data-action="reject" data-student="{}">Reject</a>',
                reverse('admin:approve_application', args=[obj.pk]),
                obj.student.username,
                reverse('admin:reject_application', args=[obj.pk]),
                obj.student.username
            )
        elif obj.status == 'approved':
            return format_html(
                '<a class="button button-small confirm-action" style="background-color:#007bff; color:white; border-radius:8px; padding:2px 8px; text-decoration:none;" href="{}" data-action="enroll" data-student="{}">Enroll</a>',
                reverse('admin:enroll_student', args=[obj.pk]),
                obj.student.username
            )
        elif obj.status == 'enrolled':
            return "Enrolled"
        elif obj.status == 'rejected':
            return "Rejected"
        return ""
    list_actions.short_description = 'Actions'

    def approve_applications(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} applications approved.', messages.SUCCESS)
    approve_applications.short_description = "Mark selected applications as approved"

    def reject_applications(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} applications rejected.', messages.WARNING)
    reject_applications.short_description = "Mark selected applications as rejected"

    def enroll_students(self, request, queryset):
        enrolled_count = 0
        already_enrolled = 0

        for app in queryset:
            if app.status != 'approved':
                continue
            if Enrollment.objects.filter(user=app.student, classroom=app.class_applied, is_active=True).exists():
                already_enrolled += 1
                continue
            Enrollment.objects.create(user=app.student, classroom=app.class_applied, is_active=True)
            app.status = 'enrolled'
            app.save()
            enrolled_count += 1

        if enrolled_count:
            self.message_user(request, f"Successfully enrolled {enrolled_count} students.", messages.SUCCESS)
        if already_enrolled:
            self.message_user(request, f"{already_enrolled} students were already enrolled.", messages.WARNING)
    enroll_students.short_description = "Enroll approved students"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/', self.admin_site.admin_view(self.approve_view), name='approve_application'),
            path('<path:object_id>/reject/', self.admin_site.admin_view(self.reject_view), name='reject_application'),
            path('<path:object_id>/enroll/', self.admin_site.admin_view(self.enroll_view), name='enroll_student'),
        ]
        return custom_urls + urls

    def approve_view(self, request, object_id):
        application = get_object_or_404(ClassApplication, pk=object_id)
        if application.status == 'pending':
            application.status = 'approved'
            application.save()
            messages.success(request, f"{application.student.username}'s application approved.")
        else:
            messages.warning(request, "Application is not pending.")
        return redirect('admin:applications_classapplication_changelist')

    def reject_view(self, request, object_id):
        application = get_object_or_404(ClassApplication, pk=object_id)
        if application.status == 'pending':
            application.status = 'rejected'
            application.save()
            messages.success(request, f"{application.student.username}'s application rejected.")
        else:
            messages.warning(request, "Application is not pending.")
        return redirect('admin:applications_classapplication_changelist')

    def enroll_view(self, request, object_id):
        application = get_object_or_404(ClassApplication, pk=object_id)
        if application.status != 'approved':
            messages.error(request, "Only approved applications can be enrolled.")
            return redirect('admin:applications_classapplication_changelist')

        if Enrollment.objects.filter(user=application.student, classroom=application.class_applied, is_active=True).exists():
            messages.warning(request, f"{application.student.username} is already enrolled.")
        else:
            Enrollment.objects.create(user=application.student, classroom=application.class_applied, is_active=True)
            application.status = 'enrolled'
            application.save()
            messages.success(request, f"{application.student.username} enrolled successfully.")
        return redirect('admin:applications_classapplication_changelist')