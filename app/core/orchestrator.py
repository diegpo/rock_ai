from llm.provider import LLMProvider
from core.ai_planner import AiPlanner
from core.context_extractor import ContextExtractor
from core.conversation import session_store
from core.logger import get_logger
from tools.tool_registry import ToolRegistry
from intents.matcher import IntentMatcher
import json

logger = get_logger("orchestrator")


class Orchestrator:
    def __init__(self):
        self.llm       = LLMProvider()
        self.ai_planner = AiPlanner(self.llm)
        self.tools     = ToolRegistry()
        self.matcher   = IntentMatcher()
        self.extractor = ContextExtractor()

    def handle(self, user_input: str, session_id: str = "default") -> str:
        text_lower = user_input.lower()

        # ── Recupera histórico da sessão ──────────────────────────
        history = session_store.get(session_id)
        history.add("user", user_input)

        # ── Troca de provider ─────────────────────────────────────
        if "usar gemini" in text_lower:
            reply = self.llm.switch("gemini")
            history.add("assistant", reply)
            return reply

        if "usar ollama" in text_lower:
            reply = self.llm.switch("ollama")
            history.add("assistant", reply)
            return reply

        if any(w in text_lower for w in ("usar qwen", "modo rápido", "modo rapido")):
            reply = self.llm.switch("qwen")
            history.add("assistant", reply)
            return reply

        # ── Novo chat ─────────────────────────────────────────────
        if any(w in text_lower for w in ("novo chat", "limpar histórico", "limpar historico")):
            session_store.clear(session_id)
            reply = "Histórico limpo! Como posso ajudar?"
            history.add("assistant", reply)
            return reply

        # ── Extrai contexto da mensagem (URLs, logs, erros) ───────
        context = self.extractor.extract(user_input)

        # ── Intent matching (domínios Protheus) ───────────────────
        intent = self.matcher.match(user_input)

        if intent["intent"] != "unknown" and intent.get("plan"):
            reply = self._execute_plan(intent, context)
            history.add("assistant", reply)
            return reply

        # ── Fallback: LLM planner com histórico ───────────────────
        result = self.ai_planner.create_plan(
            user_input=user_input,
            context=context,
            history=history,
        )

        clean = result.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(clean)

            if parsed.get("type") == "chat":
                reply = parsed.get("response", str(parsed))
                history.add("assistant", reply)
                return reply

            if parsed.get("type") == "action" and parsed.get("tools"):
                reply = self._run_tools(parsed["tools"], context)
                history.add("assistant", reply)
                return reply

            # error_resolution — retorna o campo "response"
            if parsed.get("type") == "error_resolution":
                reply = parsed.get("response", str(parsed))
                history.add("assistant", reply)
                return reply

            reply = str(parsed)
            history.add("assistant", reply)
            return reply

        except Exception:
            history.add("assistant", clean)
            return clean

    def _execute_plan(self, intent: dict, context: dict) -> str:
        domain      = intent["domain"]
        intent_name = intent["intent"]
        plan        = intent["plan"]

        results = [f"🎯 Domínio: **{domain}** | Intent: **{intent_name}**\n"]
        tool_names = [step["tool"] for step in plan]
        results.append(self._run_tools(tool_names, context))

        return "\n".join(results)

    def _run_tools(self, tool_names: list, context: dict = None) -> str:
        """Executa ferramentas passando o contexto extraído da mensagem."""
        results = []
        ctx = context or {}

        for tool_name in tool_names:
            tool = self.tools.get(tool_name)
            if tool:
                try:
                    result = tool.run(context=ctx)
                    results.append(f"✅ **{tool_name}**: {result.get('data', 'OK')}")
                except Exception as e:
                    logger.error(f"Erro na ferramenta {tool_name}: {e}")
                    results.append(f"❌ **{tool_name}**: Erro — {e}")
            else:
                results.append(f"⚠️ Ferramenta '{tool_name}' não encontrada no registry")

        return "\n".join(results) if results else "Nenhuma ferramenta executada."

    def switch_ollama(self, url: str = None, model: str = None) -> str:
        return self.llm.switch("ollama", url=url, model=model)
