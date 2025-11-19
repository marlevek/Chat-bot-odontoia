from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import os
import json


# Inicializa client OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

@csrf_exempt
def odontoia_chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message")
        history = data.get("history", [])
        clinic_info = data.get("clinic_info", {})

        clinic_name = clinic_info.get("name", "a clínica")
        clinic_city = clinic_info.get("city", "sua região")
        tone = clinic_info.get("tone", "humanizado")
        treatments = clinic_info.get("treatments", [])

        # =============================
        #   PROMPT PROFISSIONAL
        # =============================

        system_prompt = f"""
Você é o OdontoIA Chat, um assistente virtual especializado para clínicas odontológicas.

Seu objetivo é:
- responder pacientes com clareza, rapidez e educação
- explicar tratamentos de forma simples e humanizada
- nunca fazer diagnóstico
- nunca informar preços
- incentivar o agendamento com a clínica
- sempre falar como se fosse da clínica: {clinic_name} em {clinic_city}

TOM DE VOZ:
- {tone}
- curto, direto, acolhedor
- nada de respostas longas ou termos médicos difíceis

REGRAS IMPORTANTES:
1. NÃO informar valores (responda: “o valor varia conforme o caso, a clínica informa no agendamento”)
2. NÃO fazer diagnóstico (“somente o dentista pode avaliar presencialmente”)
3. NÃO indicar tratamentos específicos sem avaliação
4. NÃO inventar informações técnicas

TRATAMENTOS DA CLÍNICA:
{", ".join(treatments) if treatments else "Clareamento, Limpeza, Restaurações, Implantes, Ortodontia"}

SEMPRE terminar convidando o paciente para agendar.
"""

        # Construindo histórico
        messages = [{"role": "system", "content": system_prompt}]

        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        # Chamada ao OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
        )

        reply = completion.choices[0].message.content

        return JsonResponse({"reply": reply})

    except Exception as e:
        print("Erro no chatbot:", e)
        return JsonResponse(
            {"reply": "Desculpe, tive uma falha momentânea. Pode tentar novamente?"},
            status=200,
        )