# ROCK AI

Assistente virtual de suporte técnico para o sistema **Protheus (TOTVS)**, com integração ao Slack, interface web e CLI. Roda localmente via Docker com LLM embarcado (Ollama) e suporte opcional ao Gemini.

---

## ✨ Funcionalidades

- 💬 **Chat inteligente** com contexto de suporte Protheus
- 🎯 **Reconhecimento de intents** — identifica domínios como TSS, RH, REST, WS automaticamente
- 🧠 **Dual LLM** — usa Gemini (nuvem) com fallback automático para Ollama (local)
- 📚 **Base de conhecimento RAG** — indexa documentos `.md` e responde com base neles
- 📡 **Slack Bot** integrado via slash command
- 🌐 **Interface Web** em `localhost:5000`
- 💻 **CLI interativo** no terminal
- 🔒 **100% local** quando usando Ollama — sem dados saindo da máquina

---

## 🏗️ Arquitetura

```
rock_ai/
├── app/
│   ├── main.py                  # Entrypoint principal
│   ├── core/
│   │   ├── orchestrator.py      # Roteador central de mensagens
│   │   └── ai_planner.py        # Planejador com RAG + LLM
│   ├── llm/
│   │   ├── provider.py          # Gerenciador de providers (Gemini/Ollama)
│   │   ├── ollama.py            # Cliente Ollama
│   │   └── gemini.py            # Cliente Gemini
│   ├── intents/
│   │   ├── matcher.py           # Match de intents por domínio
│   │   └── domains/             # Domínios: protheus, tss, rh, rest, ws
│   ├── tools/
│   │   ├── tool_registry.py     # Registro de ferramentas
│   │   └── implementations/     # Ferramentas: logs, URLs, TSS, etc.
│   ├── interfaces/
│   │   ├── web/                 # Flask Web UI (porta 5000)
│   │   ├── slack/               # Slack Bot (porta 6000)
│   │   └── cli/                 # CLI interativo
│   └── knowledge/
│       └── protheus/            # Base de conhecimento (erros, serviços, RH...)
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh                # Inicialização do Ollama + pull de modelos
├── .env                         # Variáveis de ambiente (não versionado)
└── .env.example                 # Template de variáveis
```

---

## 🚀 Como rodar

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/diegpo/rock_ai.git
cd rock_ai
```

### 2. Configure o `.env`

```bash
cp .env.example .env
```

Edite o `.env` com suas chaves:

```env
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_URL=http://ollama:11434/api/generate

# Gemini (opcional — se não informado, usa só Ollama)
GEMINI_API_KEY=sua_chave_aqui

# Slack (opcional)
SLACK_SIGNING_SECRET=seu_secret_aqui
NGROK_AUTHTOKEN=seu_token_aqui
```

### 3. Suba os containers

```bash
docker compose up --build
```

Na primeira execução, o Ollama vai baixar o modelo automaticamente. Pode levar alguns minutos dependendo da conexão.

### 4. Acesse

| Interface | URL |
|---|---|
| Web UI | http://localhost:5000 |
| Slack Bot | http://localhost:6000 |
| Ngrok dashboard | http://localhost:4040 |
| Ollama API | http://localhost:11434 |

---

## 💻 Comandos úteis

```bash
# Subir em background
docker compose up -d

# Acompanhar logs
docker compose logs -f rocks_app
docker compose logs -f ollama

# Entrar no CLI interativo
docker exec -it rocks_app python interfaces/cli/cli.py

# Reiniciar só o app (sem rebuild)
docker compose restart rocks

# Parar tudo
docker compose stop

# Derrubar tudo (mantém volumes)
docker compose down

# Derrubar tudo incluindo volumes (apaga modelos baixados)
docker compose down -v
```

---

## 🧠 Trocar de LLM em tempo real

Dentro do chat (web, CLI ou Slack):

```
usar gemini     → muda para Gemini (requer GEMINI_API_KEY no .env)
usar ollama     → muda para Ollama local
usar qwen       → muda para modelo rápido (OLLAMA_MODEL_FAST)
```

---

## 📚 Base de Conhecimento

Adicione documentos `.md` em `app/knowledge/protheus/` para enriquecer as respostas:

```
knowledge/protheus/
├── erros/          ← Erros conhecidos com causa e solução
├── servicos/       ← AppServer, DBAccess, etc.
├── modulos/        ← Financeiro, Estoque, Fiscal...
├── rh/             ← Módulo RH / MeuRH
├── validacoes/     ← Checklists e procedimentos
└── tss/            ← TSS / NFS-e
```

O sistema re-indexa automaticamente ao reiniciar. Para forçar manualmente:

```bash
docker exec -it rocks_app python -c "
from knowledge.rag_engine import RAGEngine
rag = RAGEngine()
rag.index_documents()
print('Re-indexado!')
"
```

### Template para documentar erros

```markdown
# [Título do Erro]

## Descrição
[Mensagem de erro exata]

## Sintomas
- O que o usuário vê
- Em qual tela/rotina ocorre

## Causa Provável
1. Causa mais comum
2. Causa secundária

## Solução Passo a Passo
1. Primeiro passo
2. Segundo passo

## Validação
[Como confirmar que foi resolvido]
```

---

## 🐳 Exportar imagem para outro PC

```bash
# Remover volume de dev do docker-compose.yml antes do build final:
# volumes:
#   - ./app:/app   ← comentar esta linha

docker build -t rock_ai-rocks:latest .
docker save -o rocks.tar rock_ai-rocks:latest

# No outro PC:
docker load -i rocks.tar
docker compose up
```

---

## ⚙️ Modelos recomendados

O modelo padrão é leve para desenvolvimento. Para produção, recomenda-se algo maior:

| Modelo | RAM necessária | Qualidade |
|---|---|---|
| `qwen2.5:0.5b` | ~500 MB | Desenvolvimento |
| `qwen2.5:3b` | ~2 GB | Uso leve |
| `qwen2.5:7b` | ~5 GB | **Recomendado** |
| `llama3:8b` | ~5 GB | Boa alternativa |
| `qwen2.5:14b` | ~9 GB | Alta qualidade |

Para trocar, edite o `.env`:
```env
OLLAMA_MODEL=qwen2.5:7b
```

E o `entrypoint.sh`:
```sh
pull_model "qwen2.5:7b"
```

---

## 🔧 Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `OLLAMA_MODEL` | Modelo principal do Ollama | `qwen2.5:0.5b` |
| `OLLAMA_MODEL_FAST` | Modelo rápido (comando `usar qwen`) | `qwen2.5:0.5b` |
| `OLLAMA_URL` | Endpoint da API Ollama | `http://ollama:11434/api/generate` |
| `GEMINI_API_KEY` | Chave da API Gemini (opcional) | — |
| `GEMINI_API_KEYS` | Múltiplas chaves separadas por vírgula | — |
| `SLACK_SIGNING_SECRET` | Secret de verificação do Slack | — |
| `NGROK_AUTHTOKEN` | Token do Ngrok para expor o Slack Bot | — |

---

## 🛠️ Desenvolvido com

- [Python 3.12](https://python.org)
- [Ollama](https://ollama.com)
- [ChromaDB](https://trychroma.com)
- [Flask](https://flask.palletsprojects.com)
- [Ngrok](https://ngrok.com)
- [Docker](https://docker.com)

---

## 📄 Licença

Uso interno. Todos os direitos reservados.