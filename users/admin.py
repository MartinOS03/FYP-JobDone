from django.contrib import admin
from django.utils import timezone
from .models import Profile, Notification, Favourite, Qualification

# REF-031: Iteration 4 - admin registration for Favourite, Qualification; qualification verification action


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "trade", "service_area", "average_rating")
    list_filter = ("role", "trade")
    search_fields = ("user__username", "company_name", "trade", "service_area")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "message", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ("customer", "tradesman", "created_at")
    list_filter = ("created_at",)
    search_fields = ("customer__username", "tradesman__username")


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ("tradesman", "title", "verified", "verified_at", "uploaded_at")
    list_filter = ("verified",)
    search_fields = ("tradesman__username", "title")
    actions = ["mark_verified"]

    # REF-031: Iteration 4 (US 27) - admin action to verify qualifications
    @admin.action(description="Mark selected as verified")
    def mark_verified(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(verified=True, verified_at=now)
        self.message_user(request, f"{updated} qualification(s) marked as verified.")
