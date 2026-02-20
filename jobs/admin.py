from django.contrib import admin
from .models import Job, JobRequest, JobReview, JobRequestImage

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "hourly_rate", "date_posted")
    search_fields = ("title", "location")


@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = ("job", "customer", "status", "date_requested", "completed_at", "confirmed_at")
    list_filter = ("status", "date_requested")
    search_fields = ("job__title", "customer__username", "confirmation_code")


@admin.register(JobReview)
class JobReviewAdmin(admin.ModelAdmin):
    list_display = ("job_request", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("job_request__job__title", "job_request__customer__username")


# REF-001: Django Admin - model registration (Iteration 4 US 28 - job request images)
@admin.register(JobRequestImage)
class JobRequestImageAdmin(admin.ModelAdmin):
    list_display = ("job_request", "uploaded_at")
    list_filter = ("uploaded_at",)
