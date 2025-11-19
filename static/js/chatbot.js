// /static/js/chatbot.js
(function () {
  console.log("🤖 [OdontoIA Chat] Script carregado");

  // ==========================
  // CONFIGURAÇÕES GERAIS
  // ==========================

  const API_URL = "/api/odontoia-chat/";

  const CLINIC_INFO = {
    name: "Clínica Odontológica",
    city: "Curitiba - PR",
    treatments: ["Implantes", "Clareamento", "Ortodontia", "Próteses"],
    tone: "linguagem humanizada, clara e acolhedora",
  };

  let chatHistory = [];
  let isOpen = false;

  // ==========================
  // ELEMENTOS DOM
  // ==========================

  const chatBtn = document.getElementById("chatbot-btn");
  const chatWindow = document.getElementById("chatbot-window");
  const chatMessages = document.getElementById("chatbot-messages");
  const chatForm = document.getElementById("chatbot-form");
  const chatInput = document.getElementById("chatbot-input");

  if (!chatBtn || !chatWindow || !chatMessages || !chatForm || !chatInput) {
    console.warn("⚠️ Elementos do chatbot não encontrados.");
    return;
  }

  // ==========================
  // FUNÇÕES AUXILIARES
  // ==========================

  function toggleChat() {
    isOpen = !isOpen;
    if (isOpen) {
      chatWindow.classList.add("chatbot-open");
      chatWindow.classList.remove("chatbot-closed");
    } else {
      chatWindow.classList.remove("chatbot-open");
      chatWindow.classList.add("chatbot-closed");
    }
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function addMessageBubble(role, text, options = {}) {
    const msgWrapper = document.createElement("div");
    msgWrapper.classList.add("chatbot-message-row");
    msgWrapper.classList.add(role === "user" ? "from-user" : "from-bot");

    const bubble = document.createElement("div");
    bubble.classList.add("chatbot-bubble");

    if (options.isThinking) bubble.classList.add("chatbot-thinking");

    bubble.innerHTML = text;
    msgWrapper.appendChild(bubble);

    chatMessages.appendChild(msgWrapper);
    scrollToBottom();

    return bubble;
  }

  function addBotMessage(text) {
    addMessageBubble("assistant", text);
  }

  function addUserMessage(text) {
    addMessageBubble("user", text);
  }

  function showWelcomeMessage() {
    const welcome =
      "Olá! 👋 Sou o OdontoIA Chat. Posso te ajudar com dúvidas sobre tratamentos, valores aproximados e como agendar uma consulta 😀";
    addBotMessage(welcome);
    chatHistory.push({ role: "assistant", content: welcome });
  }

  // ==========================
  // ENVIO À API DJANGO
  // ==========================

  async function sendMessageToAPI(userMessage) {
    const payload = {
      message: userMessage,
      history: chatHistory,
      clinic_info: CLINIC_INFO,
    };

    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    return data;
  }

  // ==========================
  // EVENTOS DO CHATBOT
  // ==========================

  chatBtn.addEventListener("click", () => {
    toggleChat();

    if (isOpen && chatHistory.length === 0) {
      showWelcomeMessage();
    }
  });

  document.addEventListener("click", (event) => {
    const inside =
      chatWindow.contains(event.target) || chatBtn.contains(event.target);
    if (!inside && isOpen) toggleChat();
  });

  // ============================================================
  // PASSO 6 — CAPTURA DE LEADS (NOME + TELEFONE)
  // ============================================================

  let waitingLeadName = false;
  let waitingLeadPhone = false;
  let tempLeadName = "";
  let leadAlreadySent = false;

  async function sendLeadToBackend(name, phone, firstMessage) {
    try {
      const res = await fetch("/api/save-lead/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          phone,
          first_message: firstMessage,
          clinic_name: CLINIC_INFO.name,
        }),
      });

      return await res.json();
    } catch (e) {
      console.error("Erro ao enviar lead:", e);
      return { success: false };
    }
  }

  function activateLeadFlow(firstMessage) {
    if (leadAlreadySent) return;

    waitingLeadName = true;
    addBotMessage(
      "Claro! 😊 Para que a equipe da clínica te chame, posso anotar seus dados.<br><br>Qual é o seu <b>nome</b>?"
    );
  }

  async function handleLeadFlow(userText, firstMessage) {
    // Perguntar nome
    if (waitingLeadName) {
      tempLeadName = userText;
      waitingLeadName = false;
      waitingLeadPhone = true;

      addBotMessage(
        `Perfeito, <b>${tempLeadName}</b>! Agora me envie seu <b>WhatsApp</b> com DDD:`
      );
      return true;
    }

    // Perguntar telefone
    if (waitingLeadPhone) {
      const phone = userText.replace(/\D/g, "");

      if (phone.length < 10) {
        addBotMessage(
          "Parece incompleto 🤔<br>Me envie o número completo com DDD (ex: 41998765432)"
        );
        return true;
      }

      waitingLeadPhone = false;

      const result = await sendLeadToBackend(
        tempLeadName,
        phone,
        firstMessage
      );

      if (result.success) {
        leadAlreadySent = true;
        addBotMessage(
          "Obrigado! 🙌<br>A equipe da clínica vai te chamar em breve."
        );
      } else {
        addBotMessage(
          "Tive um problema ao salvar seus dados 😞<br>Pode tentar novamente?"
        );
      }

      return true;
    }

    return false;
  }

  // ============================================================
  // ENVIO DA MENSAGEM DO USUÁRIO
  // ============================================================

  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    addUserMessage(userMessage);
    chatHistory.push({ role: "user", content: userMessage });

    chatInput.value = "";
    chatInput.focus();

    // LEAD FLOW → intercepta
    const leadHandled = await handleLeadFlow(userMessage, userMessage);
    if (leadHandled) return;

    const thinkingBubble = addMessageBubble(
      "assistant",
      "Digitando...",
      { isThinking: true }
    );

    try {
      const data = await sendMessageToAPI(userMessage);

      thinkingBubble.innerHTML = data.reply;
      thinkingBubble.classList.remove("chatbot-thinking");

      chatHistory.push({ role: "assistant", content: data.reply });
      scrollToBottom();

      // API pediu para coletar lead?
      if (data.collect_lead === true && !leadAlreadySent) {
        activateLeadFlow(userMessage);
      }
    } catch (error) {
      console.error("Erro:", error);
      thinkingBubble.innerHTML =
        "Desculpe, tive um problema para responder agora. Tente novamente.";
      thinkingBubble.classList.remove("chatbot-thinking");
    }
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  console.log("✅ [OdontoIA Chat] Chatbot inicializado");
})();
