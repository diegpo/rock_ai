import requests
import os
from dotenv import load_dotenv

load_dotenv()


class GeminiLLM:
    def __init__(self):
        # Carrega lista de tokens do .env
        raw = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
        self.api_keys = [k.strip() for k in raw.split(",") if k.strip()]
        self.current_index = 0
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

        if not self.api_keys:
            raise ValueError("❌ Nenhuma GEMINI_API_KEY configurada no .env")

        print(f"Gemini iniciado com {len(self.api_keys)} token(s)")

    @property
    def current_key(self) -> str:
        return self.api_keys[self.current_index]

    def _rotate(self) -> bool:
        """Tenta passar pro próximo token. Retorna False se não houver mais."""
        if self.current_index + 1 < len(self.api_keys):
            self.current_index += 1
            print(f"Gemini: token {self.current_index} esgotado, usando token {self.current_index + 1}/{len(self.api_keys)}")
            return True

        print("❌ Gemini: todos os tokens esgotados")
        return False

    def _is_quota_error(self, response: requests.Response) -> bool:
        """Detecta erros de quota/rate limit do Gemini."""
        if response.status_code in (429, 403):
            return True

        try:
            data = response.json()
            error = data.get("error", {})
            status = error.get("status", "")
            message = error.get("message", "").lower()

            quota_signals = [
                "resource_exhausted",
                "quota",
                "rate_limit",
                "too many requests",
                "exceeded",
            ]

            if status == "RESOURCE_EXHAUSTED":
                return True

            if any(s in message for s in quota_signals):
                return True

        except Exception:
            pass

        return False

    def generate(self, prompt: str) -> str:
        """Tenta gerar resposta, rotacionando tokens se necessário."""

        # Tenta cada token disponível
        attempts = len(self.api_keys)

        for attempt in range(attempts):
            response = self._call(prompt)

            if response is not None:
                return response

            # Tenta próximo token
            if not self._rotate():
                break

        # Sem tokens disponíveis — fallback para Ollama
        print("Todos os tokens Gemini falharam, use: usar ollama")
        return "Limite de todos os tokens Gemini atingido. Digite 'usar ollama' para continuar."

    def _call(self, prompt: str) -> str | None:
        """Faz a chamada à API com o token atual. Retorna None se falhar por quota."""
        try:
            response = requests.post(
                self.url,
                headers={"Content-Type": "application/json"},
                params={"key": self.current_key},
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ]
                },
                timeout=30
            )

            if self._is_quota_error(response):
                print(f"Token {self.current_index + 1} atingiu o limite de quota")
                return None

            if response.status_code != 200:
                print(f"Gemini erro HTTP {response.status_code}: {response.text[:200]}")
                return None

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.Timeout:
            print(f"Token {self.current_index + 1} timeout")
            return None

        except Exception as e:
            print(f"Gemini erro inesperado: {e}")
            return None

    def ask(self, prompt: str) -> str:
        return self.generate(prompt)

    def status(self) -> str:
        return (
            f"Gemini | Token {self.current_index + 1}/{len(self.api_keys)} ativo"
        )