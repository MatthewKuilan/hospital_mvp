from django.contrib import admin
from .models import Patient, Provider, Appointment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("chart_number", "last_name", "first_name", "date_of_birth", "phone")
    search_fields = ("chart_number", "first_name", "last_name", "phone")


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty")
    search_fields = ("name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "provider", "start_time", "end_time", "status")
    list_filter = ("provider", "status", "start_time")
    search_fields = ("patient__last_name", "provider__name", "reason")
