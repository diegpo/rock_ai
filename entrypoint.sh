#!/bin/sh

echo "🚀 Iniciando Ollama..."
ollama serve &
OLLAMA_PID=$!

echo "⏳ Aguardando Ollama iniciar..."
# Usa wget ao invés de curl (disponível na imagem ollama/ollama)
until wget -qO- http://localhost:11434/api/tags > /dev/null 2>&1; do
  sleep 2
done
echo "✅ Ollama está rodando"

pull_model() {
  model=$1
  max_attempts=5
  attempt=1
  wait=10

  if ollama list | grep -q "^${model}"; then
    echo "✅ '${model}' já existe localmente, pulando download"
    return 0
  fi

  while [ "$attempt" -le "$max_attempts" ]; do
    echo "📥 Baixando '${model}' (tentativa ${attempt}/${max_attempts})..."

    if ollama pull "$model"; then
      echo "✅ '${model}' baixado com sucesso!"
      return 0
    fi

    echo "⚠️  Falha. Aguardando ${wait}s antes de tentar novamente..."
    sleep "$wait"
    wait=$((wait * 2))
    attempt=$((attempt + 1))
  done

  echo "❌ Não foi possível baixar '${model}' após ${max_attempts} tentativas."
  return 1
}

# echo "📥 Baixando modelo principal (gemma4:e2b)..."
# pull_model "gemma4:e2b"

echo "⚡ Baixando modelo rápido (qwen2.5:0.5b)..."
pull_model "qwen2.5:0.5b"

echo "✅ Modelos prontos!"
wait "$OLLAMA_PID"