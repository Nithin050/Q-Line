from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be exactly 10 digits."
)

time_range_validator = RegexValidator(
    regex=r'^(0?[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)\s*-\s*(0?[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)$',
    message="Time must be in format: 09:00 AM - 08:00 PM"
)


class Staff(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email


class Organization(models.Model):
    SERVICE_CHOICES = [
        ('clinic', 'Clinic'),
        ('salon', 'Salon'),
        ('consultancy', 'Consultancy'),
        ('hospital', 'Hospital'),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="organizations")

    org_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    location = models.CharField(max_length=100)
    branch_address = models.TextField()
    phone_number = models.CharField(max_length=10, validators=[phone_validator])
    working_hours = models.CharField(max_length=50, validators=[time_range_validator])
    appointment_duration = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 
    disabled_since = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.org_name} ({self.location})"


class TimeSlot(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="time_slots")
    slot_range = models.CharField(max_length=50, validators=[time_range_validator]) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.organization.org_name} - {self.slot_range}"


class Holiday(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="holidays")
    date = models.DateField()

    def __str__(self):
        return f"{self.organization.org_name} Holiday on {self.date}"
  
