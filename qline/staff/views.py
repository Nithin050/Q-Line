import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Staff, Organization, TimeSlot, Holiday
from .forms import OrganizationForm, TimeSlotForm
from django.contrib.auth import logout
from datetime import datetime, date
from bookings.models import Appointment
from django.utils import timezone


def service_register(request):
    if request.method == "POST":
        org_form = OrganizationForm(request.POST)
        slot_values = request.POST.getlist("time_slots[]")
        slot_forms = [TimeSlotForm({"slot_range": s}) for s in slot_values]

        if org_form.is_valid() and all(sf.is_valid() for sf in slot_forms):
            request.session["org_data"] = org_form.cleaned_data
            request.session["slot_data"] = [sf.cleaned_data for sf in slot_forms]
            return redirect("service_register2")

        return render(request, "staff/service_register.html", {
            "org_form": org_form,
            "slot_forms": slot_forms,
            "org_data": request.POST,
        })

    if "org_data" in request.session:
        org_form = OrganizationForm(initial=request.session["org_data"])
        slot_forms = [TimeSlotForm(initial=s) for s in request.session.get("slot_data", [])]
        return render(request, "staff/service_register.html", {
            "org_form": org_form,
            "slot_forms": slot_forms,
            "org_data": request.session["org_data"],
        })

    return render(request, "staff/service_register.html", {
        "org_form": OrganizationForm(),
        "slot_forms": [TimeSlotForm()],
        "org_data": {},
    })


def service_register2(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|net|org|in|edu|gov|co|io)$", email, re.IGNORECASE):
            context["email_error"] = "Please enter a valid staff email"
            return render(request, "staff/service_register2.html", context)

        if Staff.objects.filter(email=email).exists():
            context["email_error"] = "This email is already registered"
            return render(request, "staff/service_register2.html", context)

        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            context["confirm_error"] = "Password must be at least 8 characters, with letters + numbers"
            return render(request, "staff/service_register2.html", context)

        if password != confirm_password:
            context["confirm_error"] = "Passwords do not match"
            return render(request, "staff/service_register2.html", context)


        staff = Staff(email=email)
        staff.set_password(password)
        staff.save()
        request.session["staff_id"] = staff.id
        request.session["staff_email"] = staff.email


        org_data = request.session.get("org_data")
        slot_data = request.session.get("slot_data", [])
        if not org_data:
            return redirect("service_register")

        org = Organization.objects.create(
            staff=staff,
            org_name=org_data["org_name"],
            service_type=org_data["service_type"],
            location=org_data["location"],
            branch_address=org_data["branch_address"],
            phone_number=org_data["phone_number"],
            working_hours=org_data["working_hours"],
            appointment_duration=org_data["appointment_duration"],
        )

        for slot in slot_data:
            TimeSlot.objects.create(organization=org, slot_range=slot["slot_range"])

        request.session.pop("org_data", None)
        request.session.pop("slot_data", None)

        messages.success(request, "Service registered successfully!")
        return redirect("staff_dashboard", org_id=org.id)

    return render(request, "staff/service_register2.html", context)


def staff_login(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        staff = Staff.objects.filter(email=email).first()
        if not staff:
            context["email_error"] = "This staff email is not registered"
            return render(request, "staff/staff_login.html", context)

        if staff.check_password(password):
            request.session["staff_id"] = staff.id
            request.session["staff_email"] = staff.email

            org = Organization.objects.filter(staff=staff).first()
            if org:
                return redirect("staff_dashboard", org_id=org.id)
            return redirect("view_service")
        else:
            context["password_error"] = "Invalid email or password"
            return render(request, "staff/staff_login.html", context)

    return render(request, "staff/staff_login.html", context)


def staff_dashboard(request, org_id):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("staff_login")

    staff = get_object_or_404(Staff, id=staff_id)
    org = get_object_or_404(Organization, id=org_id, staff=staff)
    today = date.today()

    todays_appointments = Appointment.objects.filter(
        org=org, date=today
    ).order_by("time_slot")

    upcoming_count = Appointment.objects.filter(
        org=org, date__gt=today, status="Booked"
    ).count()

    completed_count = Appointment.objects.filter(
        org=org, status="Completed"
    ).count()

    missed_count = Appointment.objects.filter(
        org=org, status="Missed"
    ).count()

    return render(request, "staff/staff_dashboard.html", {
        "staff_org": org,
        "organizations": Organization.objects.filter(staff=staff),
        "today_count": todays_appointments.count(),
        "upcoming_count": upcoming_count,
        "completed_count": completed_count,
        "missed_count": missed_count,
        "todays_appointments": todays_appointments,
    })

def staff_serve(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "Completed"
    appointment.save()
    messages.success(request, "Appointment marked as served ")
    return redirect("staff_dashboard", org_id=appointment.org.id)

def staff_skip(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "Missed"
    appointment.save()
    messages.warning(request, "Appointment marked as skipped ")
    return redirect("staff_dashboard", org_id=appointment.org.id)


def staff_view_service(request):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("staff_login")
    return render(request, "staff/view_service.html", {
        "services": Organization.objects.filter(staff_id=staff_id)
    })


def staff_edit_service(request):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("staff_login")

    staff = get_object_or_404(Staff, id=staff_id)
    org = Organization.objects.filter(staff=staff).first()
    if not org:
        return render(request, "staff/edit_service.html", {"error": "No organization found."})

    if request.method == "POST":
        org.branch_address = request.POST.get("address")
        org.phone_number = request.POST.get("contact")
        org.location = request.POST.get("location")
        org.service_type = request.POST.get("description")
        org.save()

        org.time_slots.all().delete()
        for slot in request.POST.getlist("time_slots[]"):
            if slot.strip():
                TimeSlot.objects.create(organization=org, slot_range=slot.strip())

        messages.success(request, "Organization updated successfully!")
        return redirect("staff_edit_service")

    return render(request, "staff/edit_service.html", {
        "branch": {
            "name": org.org_name,
            "address": org.branch_address,
            "contact": org.phone_number,
            "location": org.location,
            "services": org.service_type,
        },
        "time_slots": org.time_slots.all(),
        "staff_org": org,
    })


def staff_appointments(request):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("staff_login")

    org = Organization.objects.filter(staff_id=staff_id).first()
    if not org:
        return render(request, 'staff/appointments.html', {
            "appointments": [],
            "staff_org": None
        })

    today = date.today()
    filter_type = request.GET.get("filter")
    search_query = request.GET.get("search", "")

    appointments = Appointment.objects.filter(org=org).order_by("date", "time_slot")

    if request.method == "POST" and request.POST.get("action") == "delete":
        appointment_id = request.POST.get("appointment_id")
        Appointment.objects.filter(id=appointment_id, org=org).delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect("staff_appointments")

    appointments = Appointment.objects.filter(
        org=org, status="Booked"
    ).order_by("date", "time_slot")


    if filter_type == "today":
        appointments = appointments.filter(date=today)
    elif filter_type == "upcoming":
        appointments = appointments.filter(date__gt=today)


    if search_query:
        appointments = appointments.filter(name__icontains=search_query)

    return render(request, 'staff/appointments.html', {
        "appointments": appointments,
        "staff_org": org,
    })



def staff_history(request):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("staff_login")

    org = Organization.objects.filter(staff_id=staff_id).first()
    if not org:
        return render(request, "staff/staff_history.html", {"appointments": []})
    search_query = request.GET.get("q")
    appointments = Appointment.objects.filter(org=org).exclude(status="Booked")
    if search_query:
        appointments = appointments.filter(name__icontains=search_query)


    return render(request, "staff/staff_history.html", {
        "appointments": appointments.order_by("-updated_at"),
        "staff_org": org
    })


def staff_slots(request):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("staff_login")

    staff = get_object_or_404(Staff, id=staff_id)
    org = Organization.objects.filter(staff=staff).first()
    if not org:
        messages.error(request, "No organization found for this staff.")
        return redirect("staff_dashboard", org_id=staff_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            slot_range = request.POST.get("slot_range")
            if slot_range:
                TimeSlot.objects.create(organization=org, slot_range=slot_range)
                messages.success(request, "Time slot added successfully.")

        elif action == "edit":
            slot_id = request.POST.get("slot_id")
            slot_range = request.POST.get("slot_range")
            slot = get_object_or_404(TimeSlot, id=slot_id, organization=org)
            slot.slot_range = slot_range
            slot.save()
            messages.success(request, "Time slot updated successfully.")

        elif action == "delete":
            slot_id = request.POST.get("slot_id")
            slot = get_object_or_404(TimeSlot, id=slot_id, organization=org)
            slot.delete()
            messages.success(request, "Time slot deleted successfully.")


        elif action == "add_holiday":
            holiday_date = request.POST.get("holiday_date")
            Holiday.objects.create(organization=org, date=holiday_date)
            messages.success(request, f"Holiday on {holiday_date} added.")

        elif action == "delete_holiday":
            holiday_id = request.POST.get("holiday_id")
            Holiday.objects.filter(id=holiday_id, organization=org).delete()
            messages.success(request, "Holiday removed.")

        elif action == "toggle_service":
            org.is_active = not org.is_active
            if not org.is_active:
                org.disabled_since = date.today()
            else:
                org.disabled_since = None
            org.save()
            messages.success(request, f"Service {'enabled' if org.is_active else 'disabled'}.")

        return redirect("staff_slots")

    return render(request, "staff/staff_slots.html", {
        "staff_org": org,
        "time_slots": org.time_slots.all(),
        "holidays": org.holidays.all(),
    })




def staff_notifications(request):
    staff_id = request.session.get("staff_id")
    if not staff_id:
        return redirect("staff_login")

    staff = get_object_or_404(Staff, id=staff_id)
    org = Organization.objects.filter(staff=staff).first()

    if not org:
        messages.error(request, "No organization found for this staff.")
        return redirect("staff_dashboard", org_id=staff_id)

    recent_appointments = Appointment.objects.filter(org=org).order_by("-updated_at")[:15]

    return render(request, "staff/notifications.html", {
        "staff_org": org,
        "recent_appointments": recent_appointments
    })


def staff_logout(request):
    request.session.pop("staff_id", None)
    request.session.pop("staff_email", None)
    messages.success(request, "You have been logged out successfully.")
    return redirect("staff_login")

