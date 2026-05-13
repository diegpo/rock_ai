import json
import uuid
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from core.orchestrator import Orchestrator
from core.conversation import session_store
from core.logger import get_logger
import requests as http_requests
import os

logger = get_logger("web")

app  = Flask(__name__)
orch = Orchestrator()


# ──────────────────────────────────────────────────────────────────
# Chat — resposta completa (usado por Slack, CLI, etc.)
# ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Mensagem não enviada"}), 400

    session_id   = data.get("session_id") or "default"
    ollama_url   = data.get("ollama_url")
    ollama_model = data.get("ollama_model")

    if ollama_url or ollama_model:
        orch.switch_ollama(url=ollama_url, model=ollama_model)

    resposta = orch.handle(data["message"], session_id=session_id)
    return jsonify({"response": str(resposta)})


# ──────────────────────────────────────────────────────────────────
# Chat — streaming SSE
# ──────────────────────────────────────────────────────────────────

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Mensagem não enviada"}), 400

    session_id   = data.get("session_id") or "default"
    user_message = data["message"]
    ollama_url   = data.get("ollama_url")
    ollama_model = data.get("ollama_model")

    if ollama_url or ollama_model:
        orch.switch_ollama(url=ollama_url, model=ollama_model)

    def generate():
        try:
            full_response = orch.handle(user_message, session_id=session_id)

            if not full_response:
                full_response = "Sem resposta do modelo."

            # Envia em chunks de ~5 palavras para efeito de digitação
            words   = full_response.split(" ")
            CHUNK   = 5
            buffer  = []

            for i, word in enumerate(words):
                buffer.append(word)
                is_last = (i == len(words) - 1)

                if len(buffer) >= CHUNK or is_last:
                    token = " ".join(buffer) + (" " if not is_last else "")
                    payload = json.dumps({"token": token, "done": False}, ensure_ascii=False)
                    yield f"data: {payload}\n\n"
                    buffer = []

            # Sinal de fim
            yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Erro no stream: {e}")
            err = json.dumps({"token": f"⚠️ Erro: {e}", "done": True}, ensure_ascii=False)
            yield f"data: {err}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":    "no-cache, no-store",
            "X-Accel-Buffering": "no",
            "Connection":       "keep-alive",
        },
    )


# ──────────────────────────────────────────────────────────────────
# Sessões
# ──────────────────────────────────────────────────────────────────

@app.route("/session/new", methods=["POST"])
def new_session():
    sid = str(uuid.uuid4())
    return jsonify({"session_id": sid})


@app.route("/session/clear", methods=["POST"])
def clear_session():
    data = request.get_json() or {}
    sid  = data.get("session_id", "default")
    session_store.clear(sid)
    return jsonify({"status": "cleared", "session_id": sid})


# ──────────────────────────────────────────────────────────────────
# Status e modelos
# ──────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({
        "status":          "ok",
        "model":           orch.llm.current_model(),
        "rag_ready":       orch.ai_planner.rag.is_ready(),
        "rag_empty":       orch.ai_planner.rag.is_empty(),
        "active_sessions": session_store.active_count(),
    })


@app.route("/api/models")
def get_models():
    base_url = request.args.get("base_url") or \
               os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate").replace("/api/generate", "")
    try:
        r      = http_requests.get(f"{base_url}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        return jsonify({"models": models, "base_url": base_url})
    except Exception as e:
        return jsonify({"models": [], "error": str(e)}), 500


@app.route("/api/switch", methods=["POST"])
def switch_provider():
    data   = request.get_json()
    result = orch.switch_ollama(url=data.get("ollama_url"), model=data.get("ollama_model"))
    return jsonify({"status": result})


if __name__ == "__main__":
    # use_reloader=False evita que o Orchestrator (e o RAG) seja iniciado duas vezes
    app.run(host="0.0.0.0", port=5000, use_reloader=False)
