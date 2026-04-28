from knowledge.rag_engine import RAGEngine


class AiPlanner:
    def __init__(self, llm):
        self.llm = llm
        self._rag = None

    @property
    def rag(self) -> RAGEngine:
        """Lazy init — só carrega RAG quando necessário."""
        if self._rag is None:
            self._rag = RAGEngine()
            if self._rag.is_empty():
                print("📚 Indexando base de conhecimento Protheus...")
                self._rag.index_documents()
        return self._rag

    def create_plan(self, user_input: str) -> str:
        context = self.rag.query(user_input)

        if context:
            prompt = f"""
Você é um agente especialista em suporte técnico do sistema Protheus (TOTVS).

BASE DE CONHECIMENTO DISPONÍVEL:
{context}

ENTRADA DO USUÁRIO:
{user_input}

INSTRUÇÕES:
- Use a base de conhecimento acima para responder com precisão.
- Se a entrada for um erro real, gere um plano de correção em JSON.
- Se for uma dúvida, explique com base nos documentos disponíveis.
- Se for uma mensagem normal, responda normalmente.

TIPOS DE RESPOSTA JSON:
- Chat/dúvida: {{"type": "chat", "response": "..."}}
- Plano de ação: {{"type": "action", "tools": ["tool1", "tool2"], "explanation": "..."}}
- Erro com solução: {{"type": "error_resolution", "error": "...", "steps": ["..."], "response": "..."}}

Responda SOMENTE em JSON válido.
"""
        else:
            prompt = f"""
Você é um agente especialista em suporte técnico do sistema Protheus (TOTVS).

ENTRADA:
{user_input}

INSTRUÇÕES:
- Identifique se é: erro de sistema, dúvida técnica, mensagem normal ou comando.
- Se NÃO for erro real, NÃO invente erro.
- Responda com base no seu conhecimento sobre Protheus/TOTVS.

TIPOS DE RESPOSTA JSON:
- Chat/dúvida: {{"type": "chat", "response": "..."}}
- Plano de ação: {{"type": "action", "tools": ["tool1"], "explanation": "..."}}
- Erro com solução: {{"type": "error_resolution", "error": "...", "steps": ["..."], "response": "..."}}

Responda SOMENTE em JSON válido.
"""

        return self.llm.generate(prompt)