from django.db import models
from django.contrib.auth.models import User


class Clinic(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=120, blank=True, null=True)
    primary_color = models.CharField(max_length=20, default="#1A0066")
    welcome_message = models.TextField(
        default="Olá! 👋 Sou o assistente virtual da clínica. Como posso te ajudar hoje?"
    )
    treatments = models.TextField(
        default="Implantes, Clareamento, Ortodontia, Limpeza, Restaurações"
    )

    embed_id = models.CharField(max_length=20, unique=True)
    
    # Avatar da clínica
    avatar = models.ImageField(upload_to='clinic_avatars/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Captura de leads
class Lead(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    first_message = models.TextField()
    clinic_name = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} - {self.phone}'
    