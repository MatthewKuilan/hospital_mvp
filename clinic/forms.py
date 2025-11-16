from django import forms
from .models import Patient, Appointment
from django.utils import timezone


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "date_of_birth", "phone", "email"]

    # chart_number is auto-generated in the view


class PatientSearchForm(forms.Form):
    name = forms.CharField(required=False, label="Name (partial)")
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    phone = forms.CharField(required=False, label="Phone")


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "provider", "start_time", "end_time", "reason", "status"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Convert HTML5 datetime-local to aware datetimes if needed
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # You can do timezone adjustments here if required
        return cleaned_data
