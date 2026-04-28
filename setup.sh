#!/bin/bash
# ─────────────────────────────────────────────────
# ROCKS AI — Script de inicialização
# ─────────────────────────────────────────────────

echo ""
echo "🪨 ROCKS AI — Setup"
echo "─────────────────────────────────────────────"

# 1. Verificar .env
if [ ! -f ".env" ]; then
  echo "⚠️  Arquivo .env não encontrado!"
  echo "   Copiando .env.example → .env"
  cp .env.example .env
  echo "   ✅ .env criado. Configure suas chaves antes de continuar."
  echo "   Abra o arquivo .env e preencha:"
  echo "     - SLACK_SIGNING_SECRET"
  echo "     - SLACK_BOT_TOKEN"
  echo "     - NGROK_AUTHTOKEN"
  echo "     - GEMINI_API_KEY (opcional)"
  echo ""
  read -p "Pressione Enter após configurar o .env..."
fi

# 2. Criar pasta de conhecimento se não existir
mkdir -p knowledge/protheus/erros
mkdir -p knowledge/protheus/servicos
mkdir -p knowledge/protheus/modulos
mkdir -p knowledge/protheus/validacoes
mkdir -p knowledge/protheus/exemplos
echo "✅ Pastas de conhecimento criadas em ./knowledge/"

# 3. Garantir permissão no entrypoint
chmod +x entrypoint.sh
echo "✅ entrypoint.sh com permissão de execução"

# 4. Build e inicialização
echo ""
echo "🚀 Iniciando containers..."
docker compose up --build -d

echo ""
echo "⏳ Aguardando containers ficarem prontos (30s)..."
sleep 30

# 5. Verificar status
echo ""
echo "📊 Status dos containers:"
docker compose ps

echo ""
echo "─────────────────────────────────────────────"
echo "✅ ROCKS AI iniciado!"
echo ""
echo "  🖥️  Web UI:     http://localhost:5000"
echo "  📡 Slack Bot:  http://localhost:6000/slack/rocks"
echo "  🔭 Ngrok UI:   http://localhost:4040"
echo "  🗄️  ChromaDB:  http://localhost:8000"
echo "  🤖 Ollama:     http://localhost:11434"
echo ""
echo "  CLI interativo:"
echo "  docker exec -it rocks_app python main.py"
echo ""
echo "  Ver logs em tempo real:"
echo "  docker compose logs -f rocks"
echo "─────────────────────────────────────────────"
