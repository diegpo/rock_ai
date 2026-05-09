const chat = document.querySelector('#chat');
const input = document.querySelector('#input');
const botaoEnviar = document.querySelector('#botao-enviar');

let imagemSelecionada = null;
let botaoAnexo = document.querySelector("#mais_arquivo");
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
        miniaturaImagem.style.maxWidth = '3rem';
        miniaturaImagem.style.maxHeight = '3rem';
        miniaturaImagem.style.margin = '0.5rem';

        document
            .querySelector('.entrada__container')
            .insertBefore(miniaturaImagem, input);

        try {
            let formData = new FormData();
            formData.append('imagem', imagemSelecionada);

            const response = await fetch('/upload_imagem', {
                method: 'POST',
                body: formData
            });

            const resposta = await response.text();
            console.log("Upload:", resposta);

        } catch (erro) {
            console.error("Erro ao enviar imagem:", erro);
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

    input.value = "";
    input.focus();

    // Remove miniatura se existir
    if (miniaturaImagem) {
        miniaturaImagem.remove();
        miniaturaImagem = null;
        imagemSelecionada = null;
    }

    // 🧑 Usuário
    const bolhaUsuario = criaBolhaUsuario();
    bolhaUsuario.innerHTML = mensagem;
    chat.appendChild(bolhaUsuario);

    // 🤖 Bot
    const bolhaBot = criaBolhaBot();
    chat.appendChild(bolhaBot);

    vaiParaFinalDoChat();

    // 🔄 Animação "pensando"
    let estados = ["Pensando...", "Processando...", "Quase lá..."];
    let indice = 0;

    bolhaBot.innerHTML = estados[0];

    const intervaloAnimacao = setInterval(() => {
        indice = (indice + 1) % estados.length;
        bolhaBot.innerHTML = estados[indice];
    }, 500);

    try {
        const resposta = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: mensagem }),
        });

        const data = await resposta.json();

        clearInterval(intervaloAnimacao);

        bolhaBot.innerHTML = data.response.replace(/\n/g, '<br>');

    } catch (erro) {
        clearInterval(intervaloAnimacao);

        bolhaBot.innerHTML = "⚠️ Erro ao conectar com o servidor";
        console.error("Erro:", erro);
    }

    vaiParaFinalDoChat();
}

// ==========================
// 💡 Criadores de bolha
// ==========================
function criaBolhaUsuario() {
    let bolha = document.createElement('p');
    bolha.className = 'chat__bolha chat__bolha--usuario';
    return bolha;
}

function criaBolhaBot() {
    let bolha = document.createElement('p');
    bolha.className = 'chat__bolha chat__bolha--bot';
    return bolha;
}

// ==========================
// ⬇️ Scroll automático
// ==========================
function vaiParaFinalDoChat() {
    chat.scrollTop = chat.scrollHeight;
}

// ==========================
// 🎯 Eventos
// ==========================
botaoEnviar.addEventListener('click', enviarMensagem);

input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        enviarMensagem();
    }
});

if (botaoAnexo) {
    botaoAnexo.addEventListener('click', pegarImagem);
}