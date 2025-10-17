from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from staff.models import Organization  # import staff's org
from bookings.models import Appointment


@login_required
def book_appointment(request):
    service_type = request.GET.get("service_type", "")
    location = request.GET.get("location", "")
    branches = []

    if service_type and location:
        branches = Organization.objects.filter(
            service_type__iexact=service_type,
            location__iexact=location,
            is_active=True
        )
        
    context = {
        "branches": branches,
        "selected_service": service_type,
        "selected_location": location
    }
    return render(request, "bookings/book_appointment.html", context)


@login_required
def active_appointments(request):
    active_appointments = Appointment.objects.filter(
        user=request.user,
        status="Booked"
    ).order_by("date", "time_slot")

    return render(request, "bookings/active_appointment.html", {
        "active_appointments": active_appointments
    })


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    if request.method == "POST":
        appointment.status = "Cancelled"
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
    return redirect("active_appointment")



@login_required
def appointment_history(request):
    past_appointments = Appointment.objects.filter(
        user=request.user
    ).exclude(status="Booked").order_by("-date", "-time_slot")

    return render(request, 'bookings/history.html', {
        "past_appointments": past_appointments
    })

