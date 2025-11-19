import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import Clinic


# ========================
#  REGISTRO DE USUÁRIO
# ========================
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Cria a clínica básica
            Clinic.objects.create(
                owner=user,
                name=f"Clínica de {user.username}",
                embed_id=f"cli_{uuid.uuid4().hex[:8]}"
            )

            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "odontoia_chat/register.html", {"form": form})


# ========================
#  LOGIN PERSONALIZADO
# ========================
class ClinicLoginView(LoginView):
    template_name = "odontoia_chat/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard")


# ========================
#  LOGOUT (opcional)
# ========================
class ClinicLogoutView(LogoutView):
    next_page = reverse_lazy("login")
