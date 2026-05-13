import requests
import os
from dotenv import load_dotenv

class OllamaProvider:
    def __init__(self, model: str = None, url: str = None):
        load_dotenv()
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        raw_url = url or os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        
        # Garante que sempre termina com /api/generate
        if not raw_url.endswith("/api/generate"):
            raw_url = raw_url.rstrip("/") + "/api/generate"
        
        self.url = raw_url

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
            return "Ollama não está acessível. Verifique se q LLM está rodando."

        except Exception as e:
            return f"Erro Ollama: {e}"

    def generate(self, prompt: str) -> str:
        return self.ask(prompt)
