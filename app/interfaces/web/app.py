from flask import Flask, render_template, request, jsonify
from core.orchestrator import Orchestrator
import requests as http_requests
import os

app  = Flask(__name__)
orch = Orchestrator()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Mensagem não enviada"}), 400
    ollama_url = data.get("ollama_url")
    ollama_model = data.get("ollama_model")
    if ollama_url or ollama_model:
        orch.switch_ollama(url=ollama_url, model=ollama_model)
    resposta = orch.handle(data["message"])
    return jsonify({"response": str(resposta)})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": orch.llm.current_model()})

@app.route("/api/models")
def get_models():
    base_url = request.args.get("base_url") or \
               os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate").replace("/api/generate", "")
    try:
        r = http_requests.get(f"{base_url}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        return jsonify({"models": models, "base_url": base_url})
    except Exception as e:
        return jsonify({"models": [], "error": str(e)}), 500

@app.route("/api/switch", methods=["POST"])
def switch_provider():
    data = request.get_json()
    result = orch.switch_ollama(url=data.get("ollama_url"), model=data.get("ollama_model"))
    return jsonify({"status": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)