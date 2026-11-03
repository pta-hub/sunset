from django.contrib import admin

from .models import MemberProfile, VolunteerRegistration


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "county", "is_verified", "date_joined")
    search_fields = ("full_name", "user__username", "user__email", "phone_number")
    list_filter = ("county", "is_verified")


@admin.register(VolunteerRegistration)
class VolunteerRegistrationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "county", "interest", "created_at")
    search_fields = ("full_name", "email", "phone_number")
    list_filter = ("county", "interest", "created_at")
    readonly_fields = ("created_at",)
