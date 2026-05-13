"""
ConversationHistory — mantém o histórico de mensagens por sessão.
Cada sessão é identificada por um session_id (gerado pelo frontend).
O histórico é usado pelo AiPlanner para dar contexto ao LLM.
"""

from collections import deque
from datetime import datetime


MAX_TURNS = 20          # máximo de turnos por sessão
MAX_SESSIONS = 200      # máximo de sessões simultâneas em memória


class ConversationHistory:
    """Histórico de uma única conversa."""

    def __init__(self, max_turns: int = MAX_TURNS):
        self._turns: deque = deque(maxlen=max_turns)
        self.created_at  = datetime.utcnow()
        self.updated_at  = datetime.utcnow()

    def add(self, role: str, content: str):
        """Adiciona uma mensagem. role = 'user' | 'assistant'."""
        self._turns.append({"role": role, "content": content})
        self.updated_at = datetime.utcnow()

    def to_prompt_block(self) -> str:
        """
        Formata o histórico como bloco de texto para incluir no prompt.
        Retorna string vazia se não há histórico.
        """
        if not self._turns:
            return ""

        lines = []
        for turn in self._turns:
            role  = "Usuário" if turn["role"] == "user" else "Rock AI"
            lines.append(f"{role}: {turn['content']}")

        return "\n".join(lines)

    def last_n(self, n: int = 5) -> list:
        """Retorna os últimos n turnos como lista de dicts."""
        turns = list(self._turns)
        return turns[-n:]

    def clear(self):
        self._turns.clear()

    def __len__(self):
        return len(self._turns)


class SessionStore:
    """
    Gerencia todas as sessões ativas em memória.
    Thread-safe para uso com Flask (GIL protege deque/dict simples).
    """

    def __init__(self, max_sessions: int = MAX_SESSIONS):
        self._sessions: dict[str, ConversationHistory] = {}
        self._max = max_sessions

    def get(self, session_id: str) -> ConversationHistory:
        """Retorna a sessão existente ou cria uma nova."""
        if session_id not in self._sessions:
            # Evita crescer ilimitado: remove a mais antiga se cheio
            if len(self._sessions) >= self._max:
                oldest = min(self._sessions, key=lambda k: self._sessions[k].updated_at)
                del self._sessions[oldest]

            self._sessions[session_id] = ConversationHistory()

        return self._sessions[session_id]

    def clear(self, session_id: str):
        """Limpa o histórico de uma sessão (novo chat)."""
        if session_id in self._sessions:
            self._sessions[session_id].clear()

    def delete(self, session_id: str):
        """Remove a sessão completamente."""
        self._sessions.pop(session_id, None)

    def active_count(self) -> int:
        return len(self._sessions)


# Instância global compartilhada pela aplicação
session_store = SessionStore()
