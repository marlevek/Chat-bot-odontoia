import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Lead

@csrf_exempt
def save_lead(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        first_message = data.get("first_message", "")
        clinic_name = data.get("clinic_name", "")

        if not name or not phone:
            return JsonResponse({"error": "Nome e telefone são obrigatórios"}, status=400)

        Lead.objects.create(
            name=name,
            phone=phone,
            first_message=first_message,
            clinic_name=clinic_name
        )

        return JsonResponse({"success": True})

    except Exception as e:
        print("Erro ao salvar lead:", e)
        return JsonResponse({"error": "Falha ao salvar lead"}, status=500)
