#Rock AI

> Agente de suporte técnico inteligente para ambientes **Cloud Protheus / TSS / TAF**, com RAG, multi-LLM e múltiplas interfaces.

---

## Índice

- [O que é](#-o-que-é)
- [Arquitetura](#-arquitetura)
- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos](#-pré-requisitos)
- [Configuração do ambiente (.env)](#-configuração-do-ambiente-env)
- [Base de Conhecimento (knowledge/)](#-base-de-conhecimento-knowledge)
- [Como executar](#-como-executar)
  - [Opção 1 — Docker Compose (recomendado)](#opção-1--docker-compose-recomendado)
  - [Opção 2 — Python / Flask direto](#opção-2--python--flask-direto)
- [Interfaces disponíveis](#-interfaces-disponíveis)
- [Provedores de LLM](#-provedores-de-llm)
- [Ferramentas (Tools)](#-ferramentas-tools)
- [Domínios e Intents](#-domínios-e-intents)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Variáveis de ambiente — referência completa](#-variáveis-de-ambiente--referência-completa)
- [Dicas e solução de problemas](#-dicas-e-solução-de-problemas)
---

## O que é

**Rock AI** é um agente conversacional especializado em suporte técnico para o ecossistema Prothues / TSS / TAF — principalmente para Cloud. Ele combina:

- **RAG** (Retrieval-Augmented Generation) sobre uma base de documentos Protheus
- **Intent matching** por domínio (REST, WS, RH, TSS, etc.)
- **Execução de ferramentas** (checar URLs, ler logs, reiniciar serviços)
- **Multi-LLM** com suporte a Gemini (online) e Ollama (local/offline), com rotação automática de tokens e fallback
- **Três interfaces**: Web (chat UI), Slack (slash command) e CLI
---

## Arquitetura

```
Usuário
  │
  ├─ Web UI (Flask :5000)
  ├─ Slack slash command (:6000)
  └─ CLI (terminal)
         │
         ▼
    Orchestrator
         │
    ┌────┴────────────────────┐
    │                         │
IntentMatcher            AiPlanner (LLM + RAG)
    │                         │
    ▼                         ▼
ToolRegistry          LLMProvider
    │                ┌────────┴────────┐
    ├─ check_url     │                 │
    ├─ read_logs   Gemini           Ollama
    ├─ restart_ws    │         (qwen2.5, etc.)
    ├─ tss_*         └─ rotação de tokens
    └─ ...                 fallback automático
```

**Fluxo de uma mensagem:**

1. A entrada chega por qualquer interface.
2. O **Orchestrator** verifica se é um comando especial (ex.: "usar gemini").
3. Tenta fazer match via **IntentMatcher** com os domínios cadastrados.
4. Se houver intent, executa o **plano de ferramentas** associado.
5. Caso contrário, passa para o **AiPlanner**, que consulta a RAG e envia ao LLM.
6. A resposta volta formatada para a interface correspondente.
---

## Funcionalidades

- Chat contextualizado sobre Protheus, TSS, REST, WebService, RH ...
- Reconhecimento automático de domínio/intent por palavras-chave
- Execução de ferramentas: verificar URLs, ler logs, reiniciar serviços
- Análise de logs com highlight de erros
- Suporte a múltiplos tokens Gemini com rotação automática (Bloqueado por limitações)
- Fallback automático Gemini → Ollama em caso de erro ou cota esgotada
- Troca de provider em tempo real via chat ("usar gemini" / "usar ollama") (Verificar disponibilidade)
- Interface Slack com verificação de assinatura e processamento assíncrono
- Web UI responsiva com chat em tempo real
---

## Pré-requisitos

| Dependência | Versão mínima | Observação |
|---|---|---|
| Python | 3.12+ | Necessário para execução local |
| Docker + Docker Compose | 24+ | Para execução containerizada |
| Ollama | Qualquer | Necessário se `DEFAULT_PROVIDER=ollama` |
| Conta Gemini | — | Necessário se `DEFAULT_PROVIDER=gemini` |
---

## Configuração do ambiente (.env)

Crie um arquivo `.env` na raiz do projeto com base no exemplo abaixo.  
**Nunca commite este arquivo** — ele já está no `.gitignore`.

```env
# ── Ambiente ──────────────────────────────────────────────────────
ENV=dev
DRY_RUN=True                  # True = não executa ações destrutivas reais

# ── Provider LLM padrão ───────────────────────────────────────────
DEFAULT_PROVIDER=ollama        # "gemini" ou "ollama"

# ── Ollama (local ou remoto) ──────────────────────────────────────
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_URL=http://localhost:11434/api/generate

# Modelo rápido (modo "usar qwen"):
OLLAMA_MODEL_FAST=qwen2.5:0.5b

# ── Gemini (online) ───────────────────────────────────────────────
# Múltiplos tokens separados por vírgula — rotação automática
GEMINI_API_KEY=SUA_CHAVE_AQUI
# GEMINI_API_KEYS=CHAVE1,CHAVE2,CHAVE3

# ── Slack ─────────────────────────────────────────────────────────
SLACK_SIGNING_SECRET=SEU_SECRET_AQUI
SLACK_VERIFICATION_TOKEN=SEU_TOKEN_AQUI

# ── ngrok ─────────────────────────────────────────────────────────
NGROK_AUTHTOKEN=SEU_TOKEN_NGROK

# ── Caminhos e logs ───────────────────────────────────────────────
ROCKS_VERSION=2.0.0
ROCKS_LOG_FILE=rocks_ia.log
KNOWLEDGE_PATH=/app/knowledge/protheus   # Dentro do container
# KNOWLEDGE_PATH=./app/knowledge/protheus  # Para execução local

# ── Protheus (ambiente do cliente) ────────────────────────────────
PROTHEUS_URL=
PROTHEUS_LOG_WS=
PROTHEUS_LOG_RH=

# ── TSS ───────────────────────────────────────────────────────────
TSS_URL=
```

---

## Base de Conhecimento (knowledge/)

A pasta `app/knowledge/` **não está incluída no repositório** (listada no `.gitignore`) por conter documentação sensível de aprendizado

Estrutura esperada:

```
app/knowledge/
└── protheus/
    ├── erros/
    │   ├── rh_errors.md
    │   ├── rest_license_errors.md
    │   ├── jobws_errors.md
    │   ├── ERRO_JOBWS_001.md
    │   └── ERRO_REST_401.md
    ├── servicos/
    │   └── APPSERVER_INI.md
    ├── rh/
    │   └── MEURH_TROUBLESHOOT.md
    ├── validacoes/
    │   └── CHECKLIST_SUBIDA.md
    └── tss/
        └── tss_flow.md
```

> **Nota:** O motor RAG (`app/knowledge/rag_engine.py`) está atualmente com indexação desabilitada temporariamente. Para ativá-lo completamente, implemente a integração com ChromaDB + Sentence Transformers já presentes no `requirements.txt`.

---

## Como executar

### Opção 1 — Docker Compose (recomendado)

Sobe a stack completa: Rock AI + Ollama + ChromaDB + ngrok.

**1. Clone o repositório e configure o `.env`:**

```bash
git clone https://github.com/seu-usuario/rock_ai.git
cd rock_ai
cp .env.example .env
# edite o .env com suas chaves
```

**2. Suba os containers:**

```bash
docker compose up --build
```

**3. Acesse:**

| Interface | URL |
|---|---|
| Web UI | http://localhost:5000 |
| Slack endpoint | http://localhost:6000/slack/rocks |
| ngrok dashboard | http://localhost:4040 |
| ChromaDB | http://localhost:8000 |
| Ollama API | http://localhost:11434 |

**Parar tudo:**

```bash
docker compose down
```

**Parar e remover volumes (apaga modelos e dados do ChromaDB):**

```bash
docker compose down -v
```

> **GPU NVIDIA:** descomente o bloco `deploy.resources` no `docker-compose.yml` para habilitar suporte a GPU no Ollama.

---

### Opção 2 — Python / Flask direto

Útil para desenvolvimento local sem Docker.

**1. Crie o ambiente virtual:**

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
```

**2. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**3. Configure o `.env`:**

```bash
cp .env.example .env
# edite com suas chaves
```

Ajuste as URLs para apontar para serviços locais:

```env
DEFAULT_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434/api/generate
KNOWLEDGE_PATH=./app/knowledge/protheus
```

**4. Certifique-se de que o Ollama está rodando (se for o provider escolhido):**

```bash
ollama serve
ollama pull qwen2.5:7b
```

**5. Execute apenas a Web UI:**

```bash
cd app
python -m flask --app interfaces/web/app.py run --host 0.0.0.0 --port 5000
```

**Ou execute a aplicação completa (Web + Slack em threads):**

```bash
cd app
python main.py
```

> **Atenção:** `main.py` aguarda o Ollama responder antes de inicializar. Se estiver usando Gemini, o health-check do Ollama ainda é executado — edite `main.py` para pular `wait_ollama()` se não for usar Ollama local.

**6. Para rodar somente o Slack:**

```bash
cd app
python -m flask --app interfaces/slack/slack_app.py run --host 0.0.0.0 --port 6000
```

**7. Para usar a CLI:**

```bash
cd app
python interfaces/cli/cli.py
```

---

## Interfaces disponíveis

### Web UI — porta 5000

Chat web com suporte a troca de provider e modelo Ollama em tempo real.

- `GET /` — Interface de chat
- `POST /chat` — Envia mensagem `{ "message": "...", "ollama_url": "...", "ollama_model": "..." }`
- `GET /health` — Status do provider atual
- `GET /api/models?base_url=...` — Lista modelos disponíveis no Ollama
- `POST /api/switch` — Troca modelo/URL do Ollama

### Slack — porta 6000

Slash command `/rocks` no Slack.

- Configure o endpoint no painel do Slack: 
- Processamento assíncrono com resposta imediata (evita timeout do Slack)
- Verificação de assinatura HMAC habilitada

### CLI

Terminal interativo com Rich para uso local sem interface web.

---

## Provedores de LLM

| Provider | Configuração | Características |
|---|---|---|
| **Gemini** | `DEFAULT_PROVIDER=gemini` + `GEMINI_API_KEY` | Online, rotação automática de múltiplos tokens |
| **Ollama** | `DEFAULT_PROVIDER=ollama` + `OLLAMA_URL` | Local/remoto, modelos open source |
| **Ollama rápido** | Comando "usar qwen" no chat | Usa `OLLAMA_MODEL_FAST` (ex.: qwen2.5:0.5b) |

**Trocar provider em tempo real pelo chat:**

```
usar gemini     → muda para Gemini
usar ollama     → muda para Ollama padrão
usar qwen       → muda para modelo rápido
modo rápido     → alias para "usar qwen"
```

**Fallback automático:** se o Gemini falhar (cota, timeout), o sistema troca automaticamente para Ollama.

---

## Ferramentas (Tools)

As ferramentas são executadas automaticamente conforme o plano do intent ou quando o LLM decide usá-las.

| Tool | Descrição |
|---|---|
| `check_url` / `check_api` | Verifica se uma URL do Protheus está respondendo |
| `read_logs` | Lê logs gerais do sistema |
| `read_logs_rh` | Lê logs específicos do módulo RH |
| `restart_ws` | Reinicia o serviço JobWS |
| `restart_rest` | Reinicia o REST Server |
| `check_ws` | Lê log do WebService |
| `tss_extract_context` | Identifica contexto de erro TSS/NFS-e |
| `tss_check_url` | Orienta verificação de URL do TSS |
| `tss_request_log` | Solicita e guia coleta do log TSS |
| `tss_analyze_log` | Analisa log do TSS buscando erros/exceptions |

> **DRY_RUN=True:** com esta flag ativa, ações destrutivas (reiniciar serviços) são simuladas, não executadas.

---

## Domínios e Intents

O sistema reconhece automaticamente o domínio da mensagem por palavras-chave:

| Domínio | Keywords exemplo | Ferramentas acionadas |
|---|---|---|
| **REST** | `rest`, `api`, `401`, `403`, `licenças rest` | check_url, run_tests |
| **WebService** | `ws`, `webservice`, `wsdl`, `soap` | check_ws, read_protheus_log |
| **RH** | `rh`, `meu rh`, `folha`, `holerite`, `ponto` | read_logs_rh, read_protheus_log |
| **TSS/NFS-e** | `nfse`, `nota fiscal`, `tss`, `prefeitura` | tss_extract_context, tss_check_url, tss_request_log |

---

## Estrutura do projeto

```
rock_ai/
├── app/
│   ├── main.py                        # Ponto de entrada (Web + Slack em threads)
│   ├── core/
│   │   ├── orchestrator.py            # Roteador central de mensagens
│   │   └── ai_planner.py              # Planejador com RAG + LLM
│   ├── llm/
│   │   ├── provider.py                # Abstração multi-LLM com fallback
│   │   ├── gemini.py                  # Cliente Gemini com rotação de tokens
│   │   └── ollama.py                  # Cliente Ollama
│   ├── interfaces/
│   │   ├── web/
│   │   │   ├── app.py                 # Flask Web UI
│   │   │   ├── templates/index.html   # Chat frontend
│   │   │   └── static/               # CSS, JS, SVGs
│   │   ├── slack/
│   │   │   └── slack_app.py           # Flask Slack endpoint
│   │   └── cli/
│   │       └── cli.py                 # Interface de terminal
│   ├── tools/
│   │   ├── base_tool.py               # Interface base
│   │   ├── tool_registry.py           # Registro de todas as ferramentas
│   │   └── implementations/
│   │       ├── check_url.py
│   │       ├── read_logs.py
│   │       ├── read_protheus_log.py
│   │       ├── restart_service.py
│   │       ├── run_tests.py
│   │       └── tss_tools.py           # Ferramentas TSS/NFS-e
│   ├── intents/
│   │   ├── matcher.py                 # Matching por keywords
│   │   ├── registry.py                # Registro de domínios
│   │   └── domains/
│   │       ├── ws.py
│   │       ├── rest.py
│   │       ├── rh.py
│   │       └── tss.py
│   └── knowledge/                     # ⚠️ NÃO incluído no repositório
│       ├── rag_engine.py              # Motor RAG (ChromaDB)
│       └── protheus/                  # Documentos .md por domínio
│           ├── erros/
│           ├── servicos/
│           ├── rh/
│           ├── validacoes/
│           └── tss/
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh                      # Script de inicialização do Ollama
├── requirements.txt
├── setup.sh
├── .env                               # ⚠️ NÃO commitado
└── .gitignore
```

---

## Variáveis de ambiente — referência completa

| Variável | Padrão | Descrição |
|---|---|---|
| `ENV` | `dev` | Ambiente (`dev` ou `prod`) |
| `DRY_RUN` | `True` | Simula ações destrutivas sem executar |
| `DEFAULT_PROVIDER` | `gemini` | Provider LLM padrão (`gemini` ou `ollama`) |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Modelo Ollama principal |
| `OLLAMA_MODEL_FAST` | `qwen2.5:0.5b` | Modelo para modo rápido |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | URL da API do Ollama |
| `GEMINI_API_KEY` | — | Token único do Gemini |
| `GEMINI_API_KEYS` | — | Múltiplos tokens separados por vírgula |
| `SLACK_SIGNING_SECRET` | — | Secret para validar requisições Slack |
| `SLACK_VERIFICATION_TOKEN` | — | Token de verificação Slack |
| `NGROK_AUTHTOKEN` | — | Token para tunnel ngrok |
| `ROCKS_VERSION` | `2.0.0` | Versão exibida no boot |
| `ROCKS_LOG_FILE` | `rocks_ia.log` | Nome do arquivo de log |
| `KNOWLEDGE_PATH` | `/app/knowledge/protheus` | Caminho da base de conhecimento |
| `PROTHEUS_URL` | — | URL do AppServer Protheus |
| `PROTHEUS_LOG_WS` | — | Caminho do log do WebService |
| `PROTHEUS_LOG_RH` | — | Caminho do log do módulo RH |
| `TSS_URL` | — | URL do TSS no tcloud do cliente |

---

## Dicas e solução de problemas

**Ollama demora para subir no Docker**
O `docker-compose.yml` aguarda o healthcheck do Ollama (até 15 tentativas × 10s). Se o modelo ainda não estiver baixado, o `entrypoint.sh` faz o pull automaticamente — isso pode levar alguns minutos na primeira vez.

**Gemini retorna "todos os tokens esgotados"**
O plano gratuito do Gemini tem cota por minuto. Adicione mais tokens em `GEMINI_API_KEYS` separados por vírgula, ou use `usar ollama` no chat para trocar de provider temporariamente.

**Slack não recebe eventos (timeout)**
O ngrok expõe a porta 6000. Copie a URL pública do ngrok (disponível em http://localhost:4040) e configure como endpoint do slash command no painel do Slack: 

**RAG não está indexando documentos**
O `rag_engine.py` está com indexação desabilitada temporariamente. Para ativar, implemente o `index_documents()` usando ChromaDB e Sentence Transformers (dependências já instaladas). O ChromaDB já está disponível em `http://localhost:8000` quando executado via Docker.

**Rodar apenas a Web sem aguardar Ollama**
Execute diretamente a interface Flask:
```bash
cd app
python interfaces/web/app.py
```

---

## Licença

Uso interno. Consulte o responsável pelo projeto para informações sobre licenciamento.