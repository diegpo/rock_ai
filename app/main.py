import os
import sys
import logging
import time
import requests
import threading
from dotenv import load_dotenv

load_dotenv()

# ─── Configura logging para arquivo + console ─────────────────
log_file = os.getenv("ROCKS_LOG_FILE", "logs/rocks_ia.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        # SEM StreamHandler aqui — o PrintToLog já cuida do terminal
    ]
)


# Redireciona print() para o log
class PrintToLog:
    def __init__(self, logger):
        self.logger = logger
        self.terminal = sys.__stdout__

    def write(self, msg):
        # Flask/click pode mandar bytes — converte para str
        if isinstance(msg, bytes):
            msg = msg.decode("utf-8", errors="replace")
        if msg.strip():
            self.terminal.write(msg)
            self.logger.info(msg.strip())

    def flush(self):
        self.terminal.flush()

    # Necessário para compatibilidade com algumas libs
    def isatty(self):
        return False


sys.stdout = PrintToLog(logging.getLogger("rocks_ia"))

# ─── Imports das interfaces (após configurar o log) ───────────
from interfaces.slack.slack_app import app as slack_app
from interfaces.web.app import app as web_app


def wait_ollama():
    """Aguarda Ollama remoto/local ficar pronto."""

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    ollama_url = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )

    base_url = ollama_url.replace("/api/generate", "")

    print("🔍 Verificando Ollama...")

    for i in range(20):

        try:

            r = requests.get(
                f"{base_url}/api/tags",
                timeout=10
            )

            if r.status_code != 200:
                raise Exception("Servidor não respondeu")

            r2 = requests.post(
                f"{base_url}/api/show",
                json={"name": model},
                timeout=10
            )

            if r2.status_code == 200:

                print(f"✅ Ollama ONLINE")
                print(f"Modelo ativo: {model}")

                return

        except Exception as e:

            print(f"Aguardando Ollama... ({i+1}/20)")
            print(f"{e}")

        time.sleep(3)

    raise Exception("❌ Ollama não respondeu.")


# 🌐 WEB
def run_web():

    print("Iniciando Web UI na porta 5000")

    web_app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )


# 💬 SLACK
def run_slack():

    print("Iniciando Slack na porta 6000")

    slack_app.run(
        host="0.0.0.0",
        port=6000,
        threaded=True
    )


def main():

    print("\nROCK AI")
    print("=" * 50)

    wait_ollama()

    print("\n Inicializando interfaces...\n")

    # WEB
    web_thread = threading.Thread(
        target=run_web,
        daemon=True
    )

    web_thread.start()

    # SLACK
    slack_thread = threading.Thread(
        target=run_slack,
        daemon=True
    )

    slack_thread.start()

    time.sleep(2)

    print("✅ WEB ONLINE  -> http://localhost:5000")
    print("✅ SLACK ONLINE -> porta 6000")
    print("✅ CLI DISPONÍVEL")
    print("\n🎯 ROCK AI iniciado com sucesso.")
    print("🛑 CTRL+C para encerrar.\n")

    # Mantém processo vivo
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()