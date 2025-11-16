from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib import messages

from .models import Patient, Provider, Appointment
from .forms import PatientForm, PatientSearchForm, AppointmentForm

import uuid
from datetime import datetime, date

def base(request):
    return render(request, "clinic/base.html")

# --------- Patient Views --------- #

def generate_chart_number():
    # Simple unique ID; you can change the format
    return "P-" + uuid.uuid4().hex[:8].upper()


def patient_list(request):
    patients = Patient.objects.all()
    return render(request, "clinic/patient_list.html", {"patients": patients})


def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.chart_number = generate_chart_number()
            patient.save()
            messages.success(request, "Patient created successfully.")
            return redirect("patient_list")
    else:
        form = PatientForm()
    return render(request, "clinic/patient_form.html", {"form": form, "title": "Add Patient"})


def patient_edit(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect("patient_list")
    else:
        form = PatientForm(instance=patient)
    return render(request, "clinic/patient_form.html", {"form": form, "title": "Edit Patient"})


def patient_search(request):
    form = PatientSearchForm(request.GET or None)
    results = []
    if form.is_valid():
        name = form.cleaned_data.get("name")
        dob = form.cleaned_data.get("date_of_birth")
        phone = form.cleaned_data.get("phone")

        qs = Patient.objects.all()

        if name:
            # Partial, case-insensitive match on first OR last name
            qs = qs.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name)
            )
        if dob:
            qs = qs.filter(date_of_birth=dob)
        if phone:
            qs = qs.filter(phone__icontains=phone)

        results = qs

    context = {
        "form": form,
        "results": results,
    }
    return render(request, "clinic/patient_search.html", context)


# --------- Appointment Views --------- #

def appointment_list(request):
    appointments = Appointment.objects.select_related("patient", "provider").order_by("start_time")
    return render(request, "clinic/appointment_list.html", {"appointments": appointments})


def appointment_create(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            try:
                appointment.full_clean()  # triggers model.clean() for conflict checking
                appointment.save()
                messages.success(request, "Appointment created successfully.")
                return redirect("appointment_list")
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = AppointmentForm()

    return render(request, "clinic/appointment_form.html", {"form": form, "title": "Create Appointment"})


def appointment_edit(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            try:
                appointment.full_clean()
                appointment.save()
                messages.success(request, "Appointment updated successfully.")
                return redirect("appointment_list")
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "clinic/appointment_form.html", {"form": form, "title": "Edit Appointment"})


def appointment_cancel(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.method == "POST":
        appointment.status = "canceled"
        appointment.save()
        messages.success(request, "Appointment canceled successfully.")
        return redirect("appointment_list")

    return render(request, "clinic/appointment_cancel_confirm.html", {"appointment": appointment})


def provider_calendar(request):
    """
    Simple provider availability view:
    - Choose provider
    - Choose date
    - See all appointments for that day
    """
    providers = Provider.objects.all()
    provider_id = request.GET.get("provider")
    date_str = request.GET.get("date")

    selected_provider = None
    appointments = []

    # Default date = today
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    if provider_id:
        selected_provider = get_object_or_404(Provider, pk=provider_id)
        # Get appointments for this provider on selected_date
        start_dt = datetime.combine(selected_date, datetime.min.time())
        end_dt = datetime.combine(selected_date, datetime.max.time())

        appointments = Appointment.objects.filter(
            provider=selected_provider,
            start_time__gte=start_dt,
            start_time__lte=end_dt,
            status="scheduled",
        ).select_related("patient")

    context = {
        "providers": providers,
        "selected_provider": selected_provider,
        "selected_date": selected_date,
        "appointments": appointments,
    }
    return render(request, "clinic/provider_calendar.html", context)
