const chatBox = document.querySelector('#chat-box');
const input = document.querySelector('#msg-input');
const botaoEnviar = document.querySelector('#send-btn');

let imagemSelecionada = null;

const botaoAnexo = document.querySelector('#attach-btn');

let miniaturaImagem = null;


// ==========================
// 📎 Upload de imagem
// ==========================
async function pegarImagem() {

    let fileInput = document.createElement("input");

    fileInput.type = "file";
    fileInput.accept = "image/*";

    fileInput.onchange = async e => {

        if (miniaturaImagem) {

            miniaturaImagem.remove();
            miniaturaImagem = null;
        }

        imagemSelecionada = e.target.files[0];

        if (!imagemSelecionada) return;

        miniaturaImagem = document.createElement('img');

        miniaturaImagem.src = URL.createObjectURL(imagemSelecionada);

        miniaturaImagem.style.maxWidth = '70px';
        miniaturaImagem.style.maxHeight = '70px';
        miniaturaImagem.style.borderRadius = '10px';
        miniaturaImagem.style.marginBottom = '10px';
        miniaturaImagem.style.border = '1px solid #30363d';

        document
            .querySelector('#input-zone')
            .prepend(miniaturaImagem);

        try {

            let formData = new FormData();

            formData.append('imagem', imagemSelecionada);

            const response = await fetch('/upload_imagem', {
                method: 'POST',
                body: formData
            });

            const resposta = await response.text();

            console.log("📎 Upload:", resposta);

        } catch (erro) {

            console.error("❌ Erro upload:", erro);
        }
    };

    fileInput.click();
}


// ==========================
// 💬 Enviar mensagem
// ==========================
async function enviarMensagem() {

    const mensagem = input.value.trim();

    if (!mensagem) return;

    removerWelcome();

    adicionarMensagemUsuario(mensagem);

    input.value = "";

    autoResize();

    input.focus();

    // Remove miniatura
    if (miniaturaImagem) {

        miniaturaImagem.remove();

        miniaturaImagem = null;
        imagemSelecionada = null;
    }

    // 🤖 typing
    const typing = criarTyping();

    chatBox.appendChild(typing);

    vaiParaFinalDoChat();

    try {

        const resposta = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                message: mensagem
            }),
        });

        const data = await resposta.json();

        typing.remove();

        adicionarMensagemBot(data.response);

    } catch (erro) {

        typing.remove();

        adicionarMensagemBot(
            "⚠️ Erro ao conectar com o servidor."
        );

        console.error("Erro:", erro);
    }

    vaiParaFinalDoChat();
}


// ==========================
// 👤 Usuário
// ==========================
function adicionarMensagemUsuario(texto) {

    const mensagem = document.createElement('div');

    mensagem.className = 'message user-message';

    mensagem.innerHTML = `
        <div class="message-content">
            ${escapeHtml(texto)}
        </div>
    `;

    chatBox.appendChild(mensagem);
}


// ==========================
// 🤖 Bot
// ==========================
function adicionarMensagemBot(texto) {

    const mensagem = document.createElement('div');

    mensagem.className = 'message bot-message';

    mensagem.innerHTML = `
        <div class="message-content">
            ${marked.parse(texto)}
        </div>
    `;

    chatBox.appendChild(mensagem);
}


// ==========================
// ⏳ Typing
// ==========================
function criarTyping() {

    const typing = document.createElement('div');

    typing.className = 'message bot-message typing';

    typing.innerHTML = `
        <div class="message-content">
            ⏳ ROCKS AI pensando...
        </div>
    `;

    return typing;
}


// ==========================
// 🧹 Remove welcome
// ==========================
function removerWelcome() {

    const welcome = document.querySelector('.welcome');

    if (welcome) {
        welcome.remove();
    }
}


// ==========================
// ⬇️ Scroll automático
// ==========================
function vaiParaFinalDoChat() {

    chatBox.scrollTop = chatBox.scrollHeight;
}


// ==========================
// 🔒 Escape HTML
// ==========================
function escapeHtml(text) {

    const div = document.createElement("div");

    div.innerText = text;

    return div.innerHTML;
}


// ==========================
// 📏 Auto resize textarea
// ==========================
function autoResize() {

    input.style.height = "auto";

    input.style.height = (input.scrollHeight) + "px";
}

input.addEventListener("input", autoResize);


// ==========================
// ⌨️ Enter inteligente
// ==========================
input.addEventListener("keydown", function (e) {

    if (e.key === "Enter" && !e.shiftKey) {

        e.preventDefault();

        enviarMensagem();
    }
});


// ==========================
// 🎯 Eventos
// ==========================
botaoEnviar.addEventListener('click', enviarMensagem);

if (botaoAnexo) {

    botaoAnexo.addEventListener('click', pegarImagem);
}