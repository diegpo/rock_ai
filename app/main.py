from interfaces.slack.slack_app import app as slack_app
from interfaces.web.app import app as web_app
from core.orchestrator import Orchestrator
import time
import requests
import threading

from interfaces.cli.cli import main as cli_main


def wait_ollama():
    """Aguarda o Ollama e o modelo ficarem prontos."""
    model = __import__("os").getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

    for i in range(20):
        try:
            # ✅ /api/tags é o endpoint correto para checar se o servidor está vivo
            r = requests.get("http://ollama:11434/api/tags", timeout=2)

            if r.status_code != 200:
                raise Exception("Ollama ainda não pronto")

            # Verifica se o modelo está disponível
            r2 = requests.post(
                "http://ollama:11434/api/show",
                json={"name": model},
                timeout=2
            )

            if r2.status_code == 200:
                print(f"✅ Ollama e modelo '{model}' prontos!")
                return

        except Exception:
            pass

        print(f"⏳ Aguardando Ollama + modelo... ({i+1}/20)")
        time.sleep(3)

    raise Exception("❌ Ollama não ficou pronto a tempo. Verifique o container.")


def run_slack():
    """Sobe o bot do Slack na porta 6000."""
    slack_app.run(host="0.0.0.0", port=6000)


def run_web():
    """✅ CORRIGIDO: Sobe a interface web na porta 5000."""
    web_app.run(host="0.0.0.0", port=5000)


def main():
    print("🚀 Iniciando ROCKS AI...\n")

    # Espera infra ficar pronta
    wait_ollama()

    print("🧠 Iniciando interfaces...\n")

    # Sobe Slack em background (porta 6000)
    threading.Thread(target=run_slack, daemon=True).start()
    print("📡 Slack Bot ativo na porta 6000")

    # ✅ CORRIGIDO: Sobe Web em background (porta 5000)
    threading.Thread(target=run_web, daemon=True).start()
    print("🌐 Web UI ativa na porta 5000")

    # CLI no foreground (mantém o processo vivo)
    cli_main()


if __name__ == "__main__":
    main()
