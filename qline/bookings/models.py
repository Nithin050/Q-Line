from django.db import models
from django.contrib.auth.models import User
from staff.models import Organization 

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, default="Booked")  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.name} - {self.org.org_name} ({self.date} {self.time_slot})"

