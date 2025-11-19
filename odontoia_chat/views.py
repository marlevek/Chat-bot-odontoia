import os
import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


SAFE_PRICE_RESPONSE = (
    "Sobre valores, eles variam conforme o caso 😊. "
    "A equipe da clínica consegue te informar direitinho. "
    "Posso pedir para te chamarem — quer deixar seu nome e WhatsApp?"
)

SAFE_DIAGNOSIS_RESPONSE = (
    "Eu não posso fazer diagnóstico aqui 😌. "
    "Somente o dentista, avaliando presencialmente, pode dizer exatamente o que está acontecendo. "
    "Quer que eu peça para a clínica te chamar?"
)

SAFE_MEDICATION_RESPONSE = (
    "Eu não posso indicar remédios ou doses 🙏. "
    "Isso só pode ser feito pelo dentista após avaliação. "
    "Se você quiser, eu peço para a equipe te chamar e te orientar direitinho."
)

# -----------------------------
#  ROTA DO CHATBOT
# -----------------------------
@csrf_exempt
def odontoia_chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []
    clinic_info = data.get("clinic_info") or {}

    if not user_message:
        return JsonResponse({"error": "Mensagem vazia"}, status=400)

    clinic_name = clinic_info.get("name", "a clínica")
    clinic_city = clinic_info.get("city", "sua região")
    tone = clinic_info.get("tone", "humanizado")
    treatments = clinic_info.get("treatments") or ["Clareamento", "Implantes", "Ortodontia"]

    # ---------------------------------------------------
    # DETECÇÃO DE INTENÇÃO — LEAD, PREÇO, CONSULTA ETC.
    # ---------------------------------------------------
    text = user_message.lower()

    asks_price = any(
        p in text for p in [
            "quanto custa", "valor", "preço", "preco", "tabela", "caro",
            "em média", "media", "custa"
        ]
    )

    asks_appointment = any(
        p in text for p in [
            "agendar", "agenda", "consulta", "marcar", "horário",
            "horario", "atendimento", "tem horário", "vocês atendem"
        ]
    )

    asks_diagnosis = any(
        p in text for p in [
            "o que eu tenho", "diagnóstico", "diagnostico", "é grave",
            "é sério", "isso é grave", "o que pode ser", "o que pode ser isso"
        ]
    )

    asks_medication = any(
        p in text for p in [
            "remédio", "remedio", "posso tomar", "antibiótico", "medicamento",
            "dose", "dosagem", "mg", "qual remédio", "qual medicamento"
        ]
    )

    # ---------------------------------------------------
    # GATILHO NATURAL DE LEAD APÓS ALGUMAS MENSAGENS
    # ---------------------------------------------------
    conversation_turns = len(history)
    soft_lead_trigger = conversation_turns >= 3  # após 3 interações

    # ---------------------------------------------------
    # CRIA O PROMPT PROFISSIONAL
    # ---------------------------------------------------
    system_prompt = f"""
Você é o OdontoIA Chat, assistente virtual de clínicas odontológicas.

TOM DE VOZ:
- {tone}, educado e acolhedor.
- Respostas curtas e claras.
- Nunca use termos técnicos difíceis.

VOCÊ REPRESENTA:
- {clinic_name} em {clinic_city}

REGRAS IMPORTANTES:
1. NÃO informar valores. Nunca!
2. NÃO fazer diagnóstico.
3. NÃO indicar remédios, doses ou medicamentos.
4. Explicar tudo de forma simples.
5. Sempre convidar para contato/agendamento.

TRATAMENTOS DISPONÍVEIS:
{", ".join(treatments)}
"""

    # Monta histórico
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    # --------------------------------------------
    # CHAMADA AO OPENAI
    # --------------------------------------------
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
        )
        reply = completion.choices[0].message.content

    except Exception:
        traceback.print_exc()
        return JsonResponse({
            "reply": "Desculpe, tive uma instabilidade. Pode repetir a mensagem? 🙏"
        })

    # --------------------------------------------
    #  FILTROS DE SEGURANÇA DO PÓS-PROCESSAMENTO
    # --------------------------------------------
    collect_lead = False  # Será enviado ao frontend

    # PREÇO
    if asks_price:
        reply = SAFE_PRICE_RESPONSE
        collect_lead = True

    # DIAGNÓSTICO
    if asks_diagnosis:
        reply = SAFE_DIAGNOSIS_RESPONSE
        collect_lead = True

    # MEDICAÇÃO
    if asks_medication:
        reply = SAFE_MEDICATION_RESPONSE
        collect_lead = True

    # AGENDAMENTO
    if asks_appointment:
        reply = (
            "Claro! Posso pedir para a equipe da clínica te chamar 😊\n"
            "Pode me passar seu *nome* e *WhatsApp*?"
        )
        collect_lead = True

    # GATILHO NATURAL DEPOIS DE ALGUMAS MENSAGENS
    if soft_lead_trigger and not collect_lead:
        reply += (
            "\n\nSe quiser, posso pedir para a equipe da clínica te chamar. "
            "Me passa seu nome e WhatsApp?"
        )
        collect_lead = True

    return JsonResponse({
        "reply": reply,
        "collect_lead": collect_lead
    })
