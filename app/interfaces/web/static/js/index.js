// ============================================================
// Rock AI — Frontend
// ============================================================

const chatBox    = document.querySelector('#chat-box');
const input      = document.querySelector('#msg-input');
const sendBtn    = document.querySelector('#send-btn');
const attachBtn  = document.querySelector('#attach-btn');
const newChatBtn = document.querySelector('#new-chat-btn');

let imagemSelecionada = null;
let miniaturaImagem   = null;
let sessionId         = null;


// ============================================================
// Inicialização
// ============================================================

async function init() {
    await criarSessao();
    await loadModels();
}

async function criarSessao() {
    try {
        const res  = await fetch('/session/new', { method: 'POST' });
        const data = await res.json();
        sessionId  = data.session_id;
    } catch (_) {
        sessionId = 'local-' + Math.random().toString(36).slice(2);
    }
}


// ============================================================
// Upload de imagem
// ============================================================

async function pegarImagem() {
    const fileInput  = document.createElement('input');
    fileInput.type   = 'file';
    fileInput.accept = 'image/*';

    fileInput.onchange = async e => {
        if (miniaturaImagem) { miniaturaImagem.remove(); miniaturaImagem = null; }
        imagemSelecionada = e.target.files[0];
        if (!imagemSelecionada) return;

        miniaturaImagem = document.createElement('img');
        miniaturaImagem.src = URL.createObjectURL(imagemSelecionada);
        miniaturaImagem.style.cssText =
            'max-width:70px;max-height:70px;border-radius:10px;margin-bottom:10px;border:1px solid #30363d;';
        document.querySelector('#input-zone').prepend(miniaturaImagem);
    };
    fileInput.click();
}


// ============================================================
// Enviar mensagem com streaming
// ============================================================

async function enviarMensagem() {
    const mensagem = input.value.trim();
    if (!mensagem) return;

    removerWelcome();
    adicionarMensagemUsuario(mensagem);
    input.value = '';
    autoResize();
    input.focus();

    if (miniaturaImagem) {
        miniaturaImagem.remove();
        miniaturaImagem   = null;
        imagemSelecionada = null;
    }

    sendBtn.disabled    = true;
    sendBtn.textContent = '...';

    // Cria o balão do bot
    const { bubble, textEl, cursorEl } = criarBolhaBot();
    chatBox.appendChild(bubble);
    vaiParaFinalDoChat();

    let fullText = '';

    try {
        const response = await fetch('/chat/stream', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(buildPayload(mensagem)),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const reader  = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let   buf     = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buf += decoder.decode(value, { stream: true });

            // Processa cada linha completa do buffer
            let nlIdx;
            while ((nlIdx = buf.indexOf('\n')) !== -1) {
                const line = buf.slice(0, nlIdx).trimEnd();
                buf = buf.slice(nlIdx + 1);

                if (!line.startsWith('data:')) continue;

                const raw = line.slice(5).trim();
                if (!raw) continue;

                let payload;
                try {
                    payload = JSON.parse(raw);
                } catch (_) {
                    continue; // linha SSE malformada — ignora
                }

                if (payload.token) {
                    fullText += payload.token;
                    // Atualiza o HTML do texto sem tocar no cursorEl
                    textEl.innerHTML = marked.parse(fullText);
                    vaiParaFinalDoChat();
                }

                if (payload.done) {
                    break;
                }
            }
        }

    } catch (erro) {
        fullText = '⚠️ Erro ao conectar com o servidor.';
        textEl.innerHTML = marked.parse(fullText);
        console.error('Erro streaming:', erro);
    }

    // Remove cursor piscante ao terminar
    if (cursorEl && cursorEl.parentNode) {
        cursorEl.remove();
    }

    // Garante que algo aparece se a resposta veio vazia
    if (!fullText.trim()) {
        textEl.innerHTML = marked.parse('⚠️ Sem resposta do modelo.');
    }

    sendBtn.disabled    = false;
    sendBtn.textContent = 'Enviar ➤';
    vaiParaFinalDoChat();
}


// ============================================================
// Novo Chat
// ============================================================

async function novoChat() {
    try {
        await fetch('/session/clear', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ session_id: sessionId }),
        });
    } catch (_) {}

    await criarSessao();

    chatBox.innerHTML = `
        <div class="welcome">
            <h2>ROCK AI</h2>
            <p>Olá! Eu sou seu assistente virtual.<br>Como posso ajudar hoje?</p>
        </div>`;

    const chatList = document.querySelector('#chat-list');
    chatList.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));

    const item = document.createElement('div');
    item.className = 'chat-item active';
    item.innerHTML = '<span class="chat-icon">💬</span><span class="chat-title">Nova Conversa</span>';
    chatList.prepend(item);
}


// ============================================================
// Helpers de UI
// ============================================================

function adicionarMensagemUsuario(texto) {
    const msg     = document.createElement('div');
    msg.className = 'message user-message';
    msg.innerHTML = `<div class="message-content">${escapeHtml(texto)}</div>`;
    chatBox.appendChild(msg);
}

function criarBolhaBot() {
    const bubble     = document.createElement('div');
    bubble.className = 'message bot-message';

    // textEl recebe o markdown — nunca sobrescrito pelo cursor
    const textEl     = document.createElement('div');
    textEl.className = 'message-content';

    // cursorEl é irmão do textEl, não filho — não é afetado pelo innerHTML do textEl
    const cursorEl       = document.createElement('span');
    cursorEl.className   = 'cursor';
    cursorEl.textContent = '▌';

    bubble.appendChild(textEl);
    bubble.appendChild(cursorEl);

    return { bubble, textEl, cursorEl };
}

function removerWelcome() {
    const el = document.querySelector('.welcome');
    if (el) el.remove();
}

function vaiParaFinalDoChat() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(text) {
    const div     = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}

function autoResize() {
    input.style.height = 'auto';
    input.style.height = input.scrollHeight + 'px';
}


// ============================================================
// Payload
// ============================================================

function buildPayload(message) {
    return {
        message,
        session_id:   sessionId,
        ollama_url:   document.getElementById('ollama-url').value.trim() || null,
        ollama_model: document.getElementById('model-select').value || null,
    };
}


// ============================================================
// Ollama — carrega modelos
// ============================================================

async function loadModels(baseUrl = null) {
    const select   = document.getElementById('model-select');
    const urlInput = document.getElementById('ollama-url');

    try {
        let url = '/api/models';
        if (baseUrl) url += `?base_url=${encodeURIComponent(baseUrl)}`;

        const res  = await fetch(url);
        const data = await res.json();

        if (!data.models || data.models.length === 0) {
            select.innerHTML = '<option>Nenhum modelo encontrado</option>';
            return;
        }

        select.innerHTML = data.models
            .map(m => `<option value="${m}">${m}</option>`)
            .join('');

        if (data.base_url) urlInput.value = data.base_url;

    } catch (_) {
        select.innerHTML = '<option>Erro ao carregar</option>';
    }
}


// ============================================================
// Eventos
// ============================================================

input.addEventListener('input', autoResize);

input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarMensagem();
    }
});

sendBtn.addEventListener('click', enviarMensagem);
if (attachBtn) attachBtn.addEventListener('click', pegarImagem);
if (newChatBtn) newChatBtn.addEventListener('click', novoChat);

document.getElementById('reload-models').addEventListener('click', async () => {
    const url   = document.getElementById('ollama-url').value.trim();
    await loadModels(url || null);
    const model = document.getElementById('model-select').value;
    await fetch('/api/switch', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ ollama_url: url, ollama_model: model }),
    });
});


// ============================================================
// Bootstrap
// ============================================================
init();
