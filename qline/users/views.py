from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from staff.models import Organization, TimeSlot, Holiday
from datetime import datetime, timedelta
from bookings.models import Appointment

import re

def user_register(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
            context["email_error"] = "Please enter a valid email address"
            return render(request, "users/register.html", context)

        if User.objects.filter(username=email).exists():
            context["email_error"] = "This email is already registered"
            return render(request, "users/register.html", context)

        if len(password) < 4:
            context["confirm_error"] = "Password must be at least 4 characters long"
            return render(request, "users/register.html", context)

        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            context["confirm_error"] = "Password must contain both letters and numbers"
            return render(request, "users/register.html", context)

        if password != confirm_password:
            context["confirm_error"] = "Passwords do not match"
            return render(request, "users/register.html", context)

        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect("user_login")

    return render(request, "users/register.html", context)


def user_login(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not User.objects.filter(username=email).exists():
            context["email_error"] = "This email is not registered"
            return render(request, "users/login.html", context)

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")  
        else:
            context["password_error"] = "Invalid email or password"
            return render(request, "users/login.html", context)

    return render(request, "users/login.html", context)


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('user_login')


@login_required
def dashboard(request):
    user = request.user
    display_name = user.first_name or user.username.split("@")[0].title()

    active_appointments = Appointment.objects.filter(user=user, status="Booked").order_by("date", "time_slot")
    past_appointments = Appointment.objects.filter(user=user).exclude(status="Booked").order_by("-date", "-time_slot")

    return render(request, "users/dashboard.html", {
        "username_display": display_name,
        "email": user.email,
        "active_appointments": active_appointments,
        "past_appointments": past_appointments,
    })

@login_required
def branch_details(request, branch_id):
    org = get_object_or_404(Organization, id=branch_id, is_active=True)
    slots = org.time_slots.all()
    today = datetime.now().date()

    pre_name = (request.GET.get("user_name") or request.POST.get("user_name") or "").strip()
    pre_phone = (request.GET.get("phone") or request.POST.get("phone") or "").strip()
    date_for_generation = request.GET.get("date") or request.POST.get("date") or ""

    grouped_slots = []
    holiday = False
    if date_for_generation:
        try:
            date_obj = datetime.strptime(date_for_generation, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Invalid date format.")
            date_obj = None

        if date_obj:
            if Holiday.objects.filter(organization=org, date=date_obj).exists():
                holiday = True
            else:
                appointment_duration = org.appointment_duration
                for slot_group in slots:
                    slot_list = []

                    try:
                        start_str, end_str = [t.strip() for t in slot_group.slot_range.split("-")]
                        start_time = datetime.strptime(start_str, "%I:%M %p").time()
                        end_time = datetime.strptime(end_str, "%I:%M %p").time()
                    except Exception:
                        continue

                    start_dt = datetime.combine(date_obj, start_time)
                    end_dt = datetime.combine(date_obj, end_time)

                    current = start_dt
                    while current + timedelta(minutes=appointment_duration) <= end_dt:
                        next_dt = current + timedelta(minutes=appointment_duration)
                        slot_str = f"{current.strftime('%I:%M %p')} – {next_dt.strftime('%I:%M %p')}"
                        booked = Appointment.objects.filter(org=org, date=date_obj, time_slot=slot_str).exists()

                        slot_list.append({
                            "slot_str": slot_str,
                            "available": not booked
                        })
                        current = next_dt

                    grouped_slots.append({
                        "group_label": slot_group.slot_range,
                        "slots": slot_list
                    })

    # Handle POST booking
    if request.method == "POST":
        user_name = (request.POST.get("user_name") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        date_str = request.POST.get("date") or date_for_generation or ""
        selected_slot = request.POST.get("selected_slot") or ""

        if not (user_name and phone and date_str and selected_slot):
            messages.error(request, "Please fill all fields and select a slot.")
            return render(request, "users/branch_details.html", {
                "org": org,
                "today": today,
                "grouped_slots": grouped_slots,
                "selected_date": date_for_generation,
                "pre_name": user_name,
                "pre_phone": phone,
            })

        if not re.match(r'^\d{10}$', phone):
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return render(request, "users/branch_details.html", {
                "org": org,
                "today": today,
                "grouped_slots": grouped_slots,
                "selected_date": date_for_generation,
                "pre_name": user_name,
                "pre_phone": phone,
            })

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()


        if Holiday.objects.filter(organization=org, date=date_obj).exists():
            messages.error(request, "This date is marked as holiday. No bookings allowed.")
            return redirect("branch_details", branch_id=org.id)

        if Appointment.objects.filter(org=org, date=date_obj, time_slot=selected_slot).exists():
            messages.error(request, "Slot already booked.")
            return render(request, "users/branch_details.html", {
                "org": org,
                "today": today,
                "grouped_slots": grouped_slots,
                "selected_date": date_for_generation,
                "pre_name": user_name,
                "pre_phone": phone,
            })


        if Appointment.objects.filter(user=request.user, org=org, status="Booked").count() >= 2:
            messages.error(request, "You can only book up to 2 active appointments at this branch.")
            return redirect("branch_details", branch_id=org.id)

        #  Create appointment
        appointment = Appointment.objects.create(
            user=request.user,
            org=org,
            name=user_name,
            date=date_obj,
            time_slot=selected_slot,
            phone=phone,
            status="Booked"
        )

        return render(request, "users/booking_confirmed.html", {
            "appointment": appointment
        })

    return render(request, "users/branch_details.html", {
        "org": org,
        "today": today,
        "grouped_slots": grouped_slots,
        "selected_date": date_for_generation,
        "pre_name": pre_name,
        "pre_phone": pre_phone,
        "holiday": holiday,
    })




@login_required
def book_slot(request, org_id):
    org = get_object_or_404(Organization, id=org_id, is_active=True)
    slots = org.time_slots.all()

    if request.method == "POST":
        user_name = request.POST.get("user_name")
        phone = request.POST.get("phone")
        date_str = request.POST.get("date")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        if Holiday.objects.filter(organization=org, date=date_obj).exists():
            messages.error(request, "This date is marked as holiday. No bookings allowed.")
            return redirect("branch_details", branch_id=org.id)

        appointment_duration = org.appointment_duration
        grouped_slots = []

        for slot_group in slots:
            slot_list = []
            if hasattr(slot_group, "is_active") and not slot_group.is_active:
                grouped_slots.append({
                    "group_label": slot_group.slot_range,
                    "slots": [{"slot_str": slot_group.slot_range, "available": False, "disabled": True}]
                })
                continue

            start_str, end_str = [t.strip() for t in slot_group.slot_range.split("-")]
            start_dt = datetime.strptime(start_str, "%I:%M %p")
            end_dt = datetime.strptime(end_str, "%I:%M %p")
            start_dt = datetime.combine(date_obj, start_dt.time())
            end_dt = datetime.combine(date_obj, end_dt.time())

            current = start_dt
            while current + timedelta(minutes=appointment_duration) <= end_dt:
                slot_str = f"{current.strftime('%I:%M %p')} – {(current + timedelta(minutes=appointment_duration)).strftime('%I:%M %p')}"
                booked = Appointment.objects.filter(org=org, date=date_obj, time_slot=slot_str).exists()
                slot_list.append({
                    "slot_str": slot_str,
                    "available": not booked
                })
                current += timedelta(minutes=appointment_duration)

            grouped_slots.append({
                "group_label": slot_group.slot_range,
                "slots": slot_list
            })

        request.session['booking_info'] = {
            "user_name": user_name,
            "phone": phone,
            "org_id": org.id,
            "date": date_str
        }

        return render(request, "users/booking_confirmed.html", {
            "org": org,
            "grouped_slots": grouped_slots,
            "date": date_str
        })

    today = datetime.now().date()
    return render(request, "users/branch_details.html", {"org": org, "slots": slots, "today": today})
