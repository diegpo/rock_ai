from flask import Flask, request, jsonify
from core.orchestrator import Orchestrator
import os
import time
import hmac
import hashlib
import threading
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
orch = Orchestrator()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

usuarios_interagiram = set()

# 🔐 Segurança Slack
def verificar_assinatura_slack(req):
    timestamp = req.headers.get("X-Slack-Request-Timestamp")
    slack_signature = req.headers.get("X-Slack-Signature")

    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    body = req.get_data(as_text=True)

    sig_basestring = f"v0:{timestamp}:{body}"

    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)

def formatar_nome(user_name):
    if not user_name:
        return ""

    nome = user_name.split(".")[0]
    nome = ''.join([c for c in nome if c.isalpha()])

    return nome.capitalize()

# 🚀 Endpoint Slack
@app.route("/slack/rocks", methods=["POST"])
def slack_rocks():

    if not verificar_assinatura_slack(request):
        return jsonify({"text": "Assinatura inválida."}), 403

    user_text = request.form.get("text")
    user_name = request.form.get("user_name")
    response_url = request.form.get("response_url")

    if not user_text or not response_url:
        return jsonify({"text": "Requisição inválida."}), 400

    def processar():
        try:
            resposta = orch.handle(user_text)
            nome = formatar_nome(user_name)

            # ✅ Converte markdown para formato Slack
            resposta_slack = str(resposta)
            resposta_slack = resposta_slack.replace("**", "*")  # negrito
            resposta_slack = resposta_slack.replace("```", "")  # remove code blocks

            if user_name not in usuarios_interagiram:
                usuarios_interagiram.add(user_name)
                resposta_final = f"{nome}, {resposta_slack}"
            else:
                resposta_final = resposta_slack

            requests.post(response_url, json={
                "response_type": "in_channel",
                "text": resposta_final
            })

        except Exception as e:
            requests.post(response_url, json={
                "response_type": "ephemeral",
                "text": "Erro ao processar sua solicitação."
            })

            print(f"Erro Slack: {e}")

    threading.Thread(target=processar, daemon=True).start()

    return jsonify({
        "response_type": "ephemeral",
        "text": "⏳ Processando..."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)