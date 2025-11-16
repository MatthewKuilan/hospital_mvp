from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Patient(models.Model):
    chart_number = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.chart_number} - {self.last_name}, {self.first_name}"


class Provider(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("canceled", "Canceled"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="appointments")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]
        # Optional: enforce provider + time uniqueness at DB level for scheduled only
        indexes = [
            models.Index(fields=["provider", "start_time", "end_time"]),
            models.Index(fields=["patient", "start_time", "end_time"]),
        ]

    def __str__(self):
        return f"{self.patient} with {self.provider} at {self.start_time}"

    def clean(self):
        # Basic validation
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

        # Only check conflicts for scheduled appointments
        if self.status != "scheduled":
            return

        # Conflict rule:
        # new_start < existing_end AND new_end > existing_start
        overlapping_qs = Appointment.objects.filter(
            status="scheduled",
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)  # exclude self when editing

        # Conflict for same provider
        provider_conflict = overlapping_qs.filter(provider=self.provider).exists()

        # Conflict for same patient
        patient_conflict = overlapping_qs.filter(patient=self.patient).exists()

        if provider_conflict:
            raise ValidationError("Conflict: provider already has an appointment at this time.")

        if patient_conflict:
            raise ValidationError("Conflict: patient already has an appointment at this time.")
