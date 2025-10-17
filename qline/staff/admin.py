from django.contrib import admin
from .models import Staff, Organization, TimeSlot


class TimeSlotInline(admin.TabularInline): 
    model = TimeSlot
    extra = 1   
    fields = ["slot_range"] 


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("org_name", "service_type", "location", "phone_number")
    inlines = [TimeSlotInline]


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("email",)
