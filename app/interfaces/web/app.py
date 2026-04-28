from flask import Flask, render_template, request, jsonify
from core.orchestrator import Orchestrator

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
    resposta = orch.handle(data["message"])
    return jsonify({"response": str(resposta)})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": orch.llm.current_model()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
