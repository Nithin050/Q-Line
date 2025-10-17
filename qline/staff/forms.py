from django import forms
import re
from .models import Organization

class OrganizationForm(forms.Form):
    org_name = forms.CharField(max_length=100)
    service_type = forms.ChoiceField(choices=Organization.SERVICE_CHOICES)
    location = forms.CharField(max_length=150)
    branch_address = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=15)
    working_hours = forms.CharField(max_length=50)
    appointment_duration = forms.IntegerField(min_value=5, max_value=180)

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]
        if not re.match(r"^[0-9]{10}$", phone):
            raise forms.ValidationError("Enter a valid 10-digit phone number")
        return phone

    def clean_working_hours(self):
        hours = self.cleaned_data["working_hours"].strip()
        if not re.match(r"^(0[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)\s-\s(0[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)$", hours, re.IGNORECASE):
            raise forms.ValidationError("Working hours must be in format: HH:MM AM - HH:MM PM")
        return hours


class TimeSlotForm(forms.Form):
    slot_range = forms.CharField(max_length=50)

    def clean_slot_range(self):
        slot = self.cleaned_data["slot_range"].strip()
        if not re.match(r"^(0[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)\s-\s(0[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)$", slot, re.IGNORECASE):
            raise forms.ValidationError("Each slot must be in format: HH:MM AM - HH:MM PM")
        return slot
