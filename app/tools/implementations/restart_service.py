import subprocess
from tools.base_tool import BaseTool


class RestartServiceTool(BaseTool):
    name = "restart_service"

    def __init__(self, service: str = "appserver"):
        self.service = service

    def run(self, context=None) -> dict:
        # Em produção, aqui você chamaria o comando real de restart
        # Ex: subprocess.run(["systemctl", "restart", self.service])
        # Por segurança, apenas simula o restart
        return {
            "success": True,
            "data": f"Serviço '{self.service}' reiniciado (simulado). "
                    "Em produção, configure o comando real em restart_service.py"
        }
