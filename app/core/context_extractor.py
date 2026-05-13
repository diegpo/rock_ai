"""
ContextExtractor — extrai parâmetros estruturados de uma mensagem livre.
Usado pelo Orchestrator para passar contexto rico às ferramentas.
"""

import re


class ContextExtractor:

    # ── Padrões de URL ────────────────────────────────────────────
    _URL_RE = re.compile(
        r"https?://[^\s\"'<>]+"
        r"|(?:localhost|[\w\-]+\.[\w\-]+(?:\.[\w\-]+)*)(?::\d+)?(?:/\S*)?",
        re.IGNORECASE,
    )

    # ── Padrões de caminho de arquivo/log ─────────────────────────
    _PATH_RE = re.compile(
        r"(?:[A-Za-z]:\\|/)[^\s\"'<>,;]+\.(?:log|txt|out|err)",
        re.IGNORECASE,
    )

    # ── Códigos de erro HTTP ──────────────────────────────────────
    _HTTP_CODE_RE = re.compile(r"\b(4\d{2}|5\d{2})\b")

    # ── Erros Protheus típicos ────────────────────────────────────
    _PROTHEUS_ERROR_RE = re.compile(
        r"\b(ERRO_\w+|NFS[\w\-]*|REST[\w\-]*|JOBWS[\w\-]*|TSS[\w\-]*)\b",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> dict:
        """
        Retorna um dict com tudo o que foi encontrado na mensagem.
        Sempre retorna um dict seguro (sem KeyError no tool.run).
        """
        urls       = self._URL_RE.findall(text)
        log_paths  = self._PATH_RE.findall(text)
        http_codes = self._HTTP_CODE_RE.findall(text)
        errors     = self._PROTHEUS_ERROR_RE.findall(text)

        # URL principal (primeira encontrada)
        primary_url = urls[0] if urls else ""

        # Garante schema na URL
        if primary_url and not primary_url.startswith("http"):
            primary_url = "http://" + primary_url

        return {
            "url":        primary_url,
            "urls":       urls,
            "log":        text,          # texto completo — para TSSAnalyzeLogTool
            "log_path":   log_paths[0] if log_paths else "",
            "http_codes": http_codes,
            "errors":     errors,
            "raw":        text,
        }
