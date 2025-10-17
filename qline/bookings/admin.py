from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "get_email", "name", "org", "date", "time_slot", "phone", "status")
    list_filter = ("org", "date", "status")
    search_fields = ("name", "user__username", "user__email", "phone", "time_slot")

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Registered Email"
