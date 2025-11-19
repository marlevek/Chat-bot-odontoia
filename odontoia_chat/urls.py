# odontoia_chat/urls.py
from django.urls import path
from .views import odontoia_chat_api
from .lead_views import save_lead
from .embed_views import chatbot_embed
from .views_auth import register, ClinicLoginView, ClinicLogoutView
from .views_dashboard import dashboard, embed_code

urlpatterns = [
    
    # painel
    path("registrar/", register, name="register"),
    path('login/', ClinicLoginView.as_view(), name='login'),
    path('logout/', ClinicLogoutView.as_view(), name='logout'),

    path("dashboard/", dashboard, name="dashboard"),
    path("embed-code/", embed_code, name="embed_code"),

    # suas APIs
    path('api/odontoia-chat/', odontoia_chat_api, name='odontoia_chat_api'),
    path('api/save-lead/', save_lead, name='save_lead'),
    path('chatbot-embed/', chatbot_embed, name='chatbot_embed'),
]
