from django.shortcuts import render

def chatbot_embed(request):
    clinic_id = request.GET.get("clinic", "default")

    # (Em breve puxaremos dados da clínica pelo ID)
    clinic_data = {
        "name": "Clínica OdontoIA",
        "color": "#1A0066",
    }

    return render(request, "odontoia_chat/chatbot_embed.html", {
        "clinic_id": clinic_id,
        "clinic": clinic_data,
    })
