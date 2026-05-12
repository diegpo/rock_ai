from flask import Flask, request, jsonify
from core.orchestrator import Orchestrator

import os
import time
import hmac
import hashlib
import threading
import traceback
import requests

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
orch = Orchestrator()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

usuarios_interagiram = set()


# 🔐 Verifica assinatura do Slack
def verificar_assinatura_slack(req):

    timestamp = req.headers.get("X-Slack-Request-Timestamp")
    slack_signature = req.headers.get("X-Slack-Signature")

    # Headers obrigatórios
    if not timestamp or not slack_signature:
        print("❌ Headers Slack ausentes")
        return False

    try:
        timestamp_int = int(timestamp)
    except ValueError:
        print("❌ Timestamp inválido")
        return False

    # Proteção replay attack
    if abs(time.time() - timestamp_int) > 60 * 5:
        print("❌ Timestamp expirado")
        return False

    body = req.get_data(as_text=True)

    sig_basestring = f"v0:{timestamp}:{body}"

    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    valido = hmac.compare_digest(my_signature, slack_signature)

    if not valido:
        print("❌ Assinatura Slack inválida")

    return valido


# 👤 Formata nome
def formatar_nome(user_name):

    if not user_name:
        return ""

    nome = user_name.split(".")[0]
    nome = ''.join([c for c in nome if c.isalpha()])

    return nome.capitalize()


# 🚀 Endpoint principal Slack
@app.route("/slack/rocks", methods=["POST"])
def slack_rocks():

    print("🔥 Requisição Slack recebida")

    # 🔐 Verifica assinatura
    if not verificar_assinatura_slack(request):
        return jsonify({
            "text": "Assinatura inválida."
        }), 403

    user_text = request.form.get("text")
    user_name = request.form.get("user_name")
    response_url = request.form.get("response_url")

    print(f"Usuário: {user_name}")
    print(f"Texto: {user_text}")

    # Validação
    if not user_text or not response_url:
        return jsonify({
            "text": "Requisição inválida."
        }), 400

    #Processamento IA em background
    def processar():

        try:

            print("Iniciando processamento IA...")

            inicio = time.time()

            resposta = orch.handle(user_text)

            fim = time.time()

            print(f"IA respondeu em {fim - inicio:.2f}s")

            nome = formatar_nome(user_name)

            # Slack markdown cleanup
            resposta_slack = str(resposta)

            resposta_slack = resposta_slack.replace("**", "*")
            resposta_slack = resposta_slack.replace("```", "")

            # Limite Slack
            resposta_slack = resposta_slack[:2900]

            # Primeira interação
            if user_name not in usuarios_interagiram:

                usuarios_interagiram.add(user_name)

                resposta_final = f"{nome}, {resposta_slack}"

            else:
                resposta_final = resposta_slack

            print("Enviando resposta ao Slack...")

            requests.post(
                response_url,
                json={
                    "response_type": "in_channel",
                    "text": resposta_final
                },
                timeout=20
            )

            print("Resposta enviada ao Slack")

        except Exception as e:

            print("Erro no processamento Slack")
            traceback.print_exc()

            try:

                requests.post(
                    response_url,
                    json={
                        "response_type": "ephemeral",
                        "text": f"Erro ao processar solicitação: {str(e)}"
                    },
                    timeout=20
                )

            except Exception as slack_error:

                print("Erro ao responder Slack")
                print(slack_error)

    #Thread separada
    threading.Thread(
        target=processar,
        daemon=True
    ).start()

    # ⚡ Resposta imediata ao Slack
    return jsonify({
        "response_type": "ephemeral",
        "text": "ROCK AI processando sua solicitação..."
    })


#Inicialização
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=6000,
        threaded=True
    )