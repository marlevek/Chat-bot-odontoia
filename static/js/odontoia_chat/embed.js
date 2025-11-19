(function() {
  console.log("📌 [OdontoIA Chat] embed.js carregado");

  // Captura atributos do script
  const scriptTag = document.currentScript;
  const clinicId = scriptTag.getAttribute("clinic") || "default";

  // Cria container do chatbot
  const chatContainer = document.createElement("div");
  chatContainer.id = "odontoia-chat-root";
  document.body.appendChild(chatContainer);

  // Carrega CSS do chatbot
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = "https://odontoiachat.com/static/odontoia_chat/chatbot.css";
  document.head.appendChild(css);

  // Carrega o HTML do chatbot
  fetch(`https://odontoiachat.com/chatbot-embed/?clinic=${clinicId}`)
    .then(res => res.text())
    .then(html => {
      chatContainer.innerHTML = html;

      // Carrega lógica JS principal do chatbot
      const mainJs = document.createElement("script");
      mainJs.src = "https://odontoiachat.com/static/odontoia_chat/chatbot.js";
      mainJs.defer = true;
      document.body.appendChild(mainJs);
    })
    .catch(err => console.error("[OdontoIA Chat] Erro ao carregar embed:", err));
})();
