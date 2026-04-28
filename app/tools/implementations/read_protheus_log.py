import os
from tools.base_tool import BaseTool


LOG_PATHS = {
    "ws":        "/protheus/logs/console_ws.log",
    "rh":        "/protheus/logs/console_rh.log",
    "appserver": "/protheus/logs/console.log",
    "rest": "/outsourcing/totvs/protheus/bin/appserver/console.log"
}


class ReadProtheusLogTool(BaseTool):
    name = "read_protheus_log"

    def __init__(self, service: str = "appserver"):
        self.service = service

    def run(self, context=None) -> dict:
        path = LOG_PATHS.get(self.service, LOG_PATHS["appserver"])

        if not os.path.exists(path):
            return {
                "success": False,
                "data": f"Log não encontrado: {path}. "
                        "Ajuste o caminho em read_protheus_log.py"
            }

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # Retorna as últimas 50 linhas
            tail = "".join(lines[-50:])
            return {"success": True, "data": tail}

        except Exception as e:
            return {"success": False, "data": f"Erro ao ler log: {e}"}
