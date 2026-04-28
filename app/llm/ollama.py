import requests
import os
from dotenv import load_dotenv

class OllamaProvider:
    # ✅ NOVO: aceita model como parâmetro (para suportar Qwen e outros)
    def __init__(self, model: str = None):
        load_dotenv()
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma4:e2b")
        self.url = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")

    def ask(self, prompt: str) -> str:
        try:
            response = requests.post(self.url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }, timeout=120)

            response.raise_for_status()
            return response.json()["response"]

        except requests.exceptions.ConnectionError:
            return "❌ Ollama não está acessível. Verifique se o container está rodando."

        except Exception as e:
            return f"❌ Erro Ollama: {e}"

    def generate(self, prompt: str) -> str:
        return self.ask(prompt)
