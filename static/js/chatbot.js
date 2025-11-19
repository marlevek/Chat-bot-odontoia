// /static/js/chatbot.js
(function () {
  console.log("🤖 [OdontoIA Chat] Script carregado");

  // ==========================
  // CONFIGURAÇÕES GERAIS
  // ==========================

  // URL da API Django (ajuste se usar prefixo, subdomínio etc.)
  const API_URL = "/api/odontoia-chat/";

  // Informações da clínica (pode vir do template Django depois)
  const CLINIC_INFO = {
    name: "Clínica Odontológica",
    city: "Curitiba - PR",
    treatments: ["Implantes", "Clareamento", "Ortodontia", "Próteses"],
    tone: "linguagem humanizada, clara e acolhedora",
  };

  // Histórico de mensagens enviado para a API
  let chatHistory = [];

  // Flag se o chat está aberto
  let isOpen = false;

  // ==========================
  // SELEÇÃO DE ELEMENTOS DOM
  // ==========================

  const chatBtn = document.getElementById("chatbot-btn");
  const chatWindow = document.getElementById("chatbot-window");
  const chatMessages = document.getElementById("chatbot-messages");
  const chatForm = document.getElementById("chatbot-form");
  const chatInput = document.getElementById("chatbot-input");

  if (!chatBtn || !chatWindow || !chatMessages || !chatForm || !chatInput) {
    console.warn(
      "⚠️ [OdontoIA Chat] Elementos do chatbot não encontrados. Verifique os IDs no HTML."
    );
    return;
  }

  // ==========================
  // FUNÇÕES AUXILIARES
  // ==========================

  // Abre/fecha a janela do chat
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

  // Rolagem automática para a última mensagem
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Cria e adiciona uma bolha de mensagem no DOM
  function addMessageBubble(role, text, options = {}) {
    const msgWrapper = document.createElement("div");
    msgWrapper.classList.add("chatbot-message-row");
    msgWrapper.classList.add(role === "user" ? "from-user" : "from-bot");

    const bubble = document.createElement("div");
    bubble.classList.add("chatbot-bubble");

    if (options.isThinking) {
      bubble.classList.add("chatbot-thinking");
    }

    bubble.textContent = text;
    msgWrapper.appendChild(bubble);

    chatMessages.appendChild(msgWrapper);
    scrollToBottom();

    return bubble;
  }

  // Mostra mensagem inicial do bot
  function showWelcomeMessage() {
    const welcome =
      "Olá! 👋 Sou o OdontoIA Chat. Posso te ajudar com dúvidas sobre tratamentos, valores aproximados e como agendar uma consulta 😀";
    addMessageBubble("assistant", welcome);
    chatHistory.push({ role: "assistant", content: welcome });
  }

  // Envia mensagem para a API Django
  async function sendMessageToAPI(userMessage) {
    // Monta o payload
    const payload = {
      message: userMessage,
      history: chatHistory,
      clinic_info: CLINIC_INFO,
    };

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || "Erro ao se comunicar com a API.");
    }

    const data = await response.json();
    if (!data.reply) {
      throw new Error("Resposta inválida da API.");
    }

    return data.reply;
  }

  // ==========================
  // EVENTOS
  // ==========================

  // Clique no botão flutuante abre/fecha o chat
  chatBtn.addEventListener("click", () => {
    toggleChat();

    // Primeira abertura, mostra mensagem de boas-vindas
    if (isOpen && chatHistory.length === 0) {
      showWelcomeMessage();
    }
  });

  // Fechar ao clicar fora (opcional, se quiser depois dá pra tirar)
  document.addEventListener("click", (event) => {
    const clickedInside =
      chatWindow.contains(event.target) || chatBtn.contains(event.target);

    if (!clickedInside && isOpen) {
      toggleChat();
    }
  });

  // Envio do formulário
  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // Adiciona mensagem do usuário
    addMessageBubble("user", userMessage);
    chatHistory.push({ role: "user", content: userMessage });

    // Limpa input
    chatInput.value = "";
    chatInput.focus();

    // Adiciona bolha de "digitando..."
    const thinkingBubble = addMessageBubble(
      "assistant",
      "Digitando...",
      { isThinking: true }
    );

    try {
      const reply = await sendMessageToAPI(userMessage);

      // Atualiza bolha de "digitando..." com a resposta real
      thinkingBubble.textContent = reply;
      thinkingBubble.classList.remove("chatbot-thinking");

      chatHistory.push({ role: "assistant", content: reply });
      scrollToBottom();
    } catch (error) {
      console.error("Erro no chatbot:", error);
      thinkingBubble.textContent =
        "Desculpe, tive um problema para responder agora. Tente novamente em instantes.";
      thinkingBubble.classList.remove("chatbot-thinking");
    }
  });

  // Enviar com Enter (sem Shift)
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  console.log("✅ [OdontoIA Chat] Chatbot inicializado");
})();
