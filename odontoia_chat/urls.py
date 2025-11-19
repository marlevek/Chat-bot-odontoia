# odontoia_chat/urls.py
from django.urls import path
from .views import odontoia_chat_api


urlpatterns = [
    path('api/odontoia-chat/', odontoia_chat_api, name='odontoia_chat_api'),
]