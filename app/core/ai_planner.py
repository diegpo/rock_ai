from knowledge.rag_engine import RAGEngine
from core.logger import get_logger

logger = get_logger("ai_planner")


class AiPlanner:
    def __init__(self, llm):
        self.llm = llm
        self._rag = None

    @property
    def rag(self) -> RAGEngine:
        """Lazy init — carrega RAG só quando necessário."""
        if self._rag is None:
            self._rag = RAGEngine()
            if self._rag.is_ready() and self._rag.is_empty():
                logger.info("Indexando base de conhecimento Protheus...")
                total = self._rag.index_documents()
                logger.info(f"RAG: {total} chunks indexados")
        return self._rag

    def create_plan(self, user_input: str, context: dict = None, history=None) -> str:
        rag_context   = self.rag.query(user_input)
        history_block = history.to_prompt_block() if history and len(history) > 1 else ""

        sections = []

        if history_block:
            sections.append(f"HISTÓRICO DA CONVERSA:\n{history_block}")

        if rag_context:
            sections.append(f"BASE DE CONHECIMENTO DISPONÍVEL:\n{rag_context}")

        # Contexto técnico extraído (URLs, erros, etc.)
        ctx = context or {}
        tech_parts = []
        if ctx.get("url"):
            tech_parts.append(f"URL detectada: {ctx['url']}")
        if ctx.get("http_codes"):
            tech_parts.append(f"Códigos HTTP detectados: {', '.join(ctx['http_codes'])}")
        if ctx.get("errors"):
            tech_parts.append(f"Erros detectados: {', '.join(ctx['errors'])}")
        if tech_parts:
            sections.append("CONTEXTO TÉCNICO DETECTADO:\n" + "\n".join(tech_parts))

        sections.append(f"ENTRADA DO USUÁRIO:\n{user_input}")

        body = "\n\n".join(sections)

        prompt = f"""Você é um agente especialista em suporte técnico do sistema Cloud Protheus (TOTVS).
Seu nome é Rock AI.

{body}

INSTRUÇÕES:
- Use o histórico para manter continuidade da conversa.
- Use a base de conhecimento para responder com precisão quando disponível.
- Use o contexto técnico detectado (URL, erros) para personalizar a resposta.
- Se for um erro real, gere um plano de correção em JSON.
- Se for dúvida, explique com base nos documentos disponíveis.
- Se for mensagem normal ou saudação, responda normalmente.
- Nunca invente erros que não foram mencionados.

TIPOS DE RESPOSTA JSON:
- Chat/dúvida: {{"type": "chat", "response": "..."}}
- Plano de ação: {{"type": "action", "tools": ["tool1", "tool2"], "explanation": "..."}}
- Erro com solução: {{"type": "error_resolution", "error": "...", "steps": ["..."], "response": "..."}}

Responda SOMENTE em JSON válido."""

        return self.llm.generate(prompt)
