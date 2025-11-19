from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Clinic, Lead
from .forms import ClinicForm


@login_required
def dashboard(request):
    clinic = Clinic.objects.get(owner=request.user)
    if request.method == 'POST':
        form = ClinicForm(request.POST, request.FILES, instance=clinic)
        if form.is_valid:
            form.save()
        return redirect('dashboard')
    
    else:
        form = ClinicForm(instance=clinic)
    
    
    leads = Lead.objects.filter(clinic_name=clinic.name).order_by("-created_at")

    return render(request, "odontoia_chat/dashboard.html", {
        "clinic": clinic,
        "form": form,
        "leads": leads,
    })


@login_required
def embed_code(request):
    clinic = Clinic.objects.get(owner=request.user)
    
    script_code = f"""
<script src="https://odontoiachat.com/embed.js" clinic="{clinic.embed_id}"></script>
"""

    return render(request, "odontoia_chat/embed_code.html", {
        "clinic": clinic,
        "script_code": script_code,
    })