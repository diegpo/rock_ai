import os
from dotenv import load_dotenv

load_dotenv()


class LLMProvider:
    def __init__(self):
        # Tenta iniciar com Gemini, cai para Ollama se não tiver chave
        gemini_keys = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))

        if gemini_keys.strip():
            try:
                from llm.gemini import GeminiLLM
                self.llm = GeminiLLM()
                self.current = "gemini"
                print("Provider padrão: Gemini")
            except Exception as e:
                print(f"Falha ao iniciar Gemini: {e} — usando Ollama")
                from llm.ollama import OllamaProvider
                self.llm = OllamaProvider()
                self.current = "ollama"
        else:
            from llm.ollama import OllamaProvider
            self.llm = OllamaProvider()
            self.current = "ollama"
            print("Provider padrão: Ollama (sem chave Gemini no .env)")

    def switch(self, provider_name: str) -> str:
        provider_name = provider_name.lower()

        if provider_name == "gemini":
            try:
                from llm.gemini import GeminiLLM
                self.llm = GeminiLLM()
                self.current = "gemini"
                return f"Agora usando Gemini — {self.llm.status()}"
            except Exception as e:
                return f"Não foi possível iniciar Gemini: {e}"

        elif provider_name == "ollama":
            from llm.ollama import OllamaProvider
            self.llm = OllamaProvider()
            self.current = "ollama"
            model = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
            return f"Agora usando Ollama ({model})"

        elif provider_name in ("qwen", "rapido", "rápido"):
            from llm.ollama import OllamaProvider
            fast = os.getenv("OLLAMA_MODEL_FAST", "qwen2.5:0.5b")
            self.llm = OllamaProvider(model=fast)
            self.current = "qwen"
            return f"⚡ Agora usando {fast} (modo rápido)"

        return "Provider desconhecido. Use: gemini, ollama, qwen"

    def generate(self, prompt: str) -> str:
        try:
            response = self.llm.generate(prompt)
            return response

        except Exception as e:
            print(f"Erro no provider '{self.current}': {e}")

            # Fallback automático para Ollama se Gemini falhar completamente
            if self.current == "gemini":
                print("Fallback automático para Ollama...")
                self.switch("ollama")
                return self.llm.generate(prompt)

            return f"Erro: {e}"

    def ask(self, prompt: str) -> str:
        return self.generate(prompt)

    def current_model(self) -> str:
        if self.current == "gemini":
            try:
                return f"gemini (token {self.llm.current_index + 1}/{len(self.llm.api_keys)})"
            except Exception:
                return "gemini"
        return self.current