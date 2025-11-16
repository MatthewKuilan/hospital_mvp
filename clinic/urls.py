from django.urls import path
from . import views

urlpatterns = [
    # Patients
    path("", views.base, name="base"),
    path("patients/", views.patient_list, name="patient_list"),
    path("patients/new/", views.patient_create, name="patient_create"),
    path("patients/<int:patient_id>/edit/", views.patient_edit, name="patient_edit"),
    path("patients/search/", views.patient_search, name="patient_search"),

    # Appointments
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/new/", views.appointment_create, name="appointment_create"),
    path("appointments/<int:appointment_id>/edit/", views.appointment_edit, name="appointment_edit"),
    path("appointments/<int:appointment_id>/cancel/", views.appointment_cancel, name="appointment_cancel"),

    # Provider calendar
    path("calendar/", views.provider_calendar, name="provider_calendar"),
]
