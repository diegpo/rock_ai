import json
from llm.provider import LLMProvider
from core.ai_planner import AiPlanner
from tools.tool_registry import ToolRegistry
from intents.matcher import IntentMatcher


class Orchestrator:
    def __init__(self):
        self.llm = LLMProvider()
        self.ai_planner = AiPlanner(self.llm)
        # ✅ CORRIGIDO: ToolRegistry e IntentMatcher agora são usados
        self.tools = ToolRegistry()
        self.matcher = IntentMatcher()

    def handle(self, user_input: str) -> str:
        text_lower = user_input.lower()

        # ─── Troca de provider ────────────────────────────
        if "usar gemini" in text_lower:
            return self.llm.switch("gemini")

        if "usar ollama" in text_lower:
            return self.llm.switch("ollama")

        if any(w in text_lower for w in ("usar qwen", "modo rápido", "modo rapido")):
            return self.llm.switch("qwen")

        # ─── Intent matching (domínios Protheus) ──────────
        intent = self.matcher.match(user_input)

        if intent["intent"] != "unknown" and intent.get("plan"):
            return self._execute_plan(intent)

        # ─── Fallback: LLM planner ────────────────────────
        result = self.ai_planner.create_plan(user_input)

        # Limpa markdown ```json
        clean = result.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(clean)

            if parsed.get("type") == "chat":
                return parsed.get("response", str(parsed))

            # Se for um plano de ação, tenta executar
            if parsed.get("type") == "action" and parsed.get("tools"):
                return self._run_tools(parsed["tools"])

            return str(parsed)

        except Exception:
            return clean

    def _execute_plan(self, intent: dict) -> str:
        """Executa plano de ferramentas baseado no intent."""
        domain = intent["domain"]
        intent_name = intent["intent"]
        plan = intent["plan"]

        results = []
        results.append(f"🎯 Domínio: **{domain}** | Intent: **{intent_name}**\n")

        tool_names = [step["tool"] for step in plan]
        results.append(self._run_tools(tool_names))

        return "\n".join(results)

    def _run_tools(self, tool_names: list) -> str:
        """✅ NOVO: Executa ferramentas pelo nome."""
        results = []

        for tool_name in tool_names:
            tool = self.tools.get(tool_name)

            if tool:
                try:
                    result = tool.run()
                    results.append(f"✅ **{tool_name}**: {result.get('data', 'OK')}")
                except Exception as e:
                    results.append(f"❌ **{tool_name}**: Erro — {e}")
            else:
                results.append(f"⚠️ Ferramenta '{tool_name}' não encontrada no registry")

        return "\n".join(results) if results else "Nenhuma ferramenta executada."
