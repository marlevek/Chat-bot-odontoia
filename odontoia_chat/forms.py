from django import forms 
from .models import Clinic 


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ["name", "city", "welcome_message", "treatments", "primary_color", "avatar"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "welcome_message": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "treatments": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "primary_color": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
    }