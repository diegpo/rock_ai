from tools.implementations.read_logs import ReadLogsTool
from tools.implementations.run_tests import RunTestsTool
from tools.implementations.check_url import CheckUrlTool
from tools.implementations.restart_service import RestartServiceTool
from tools.implementations.read_protheus_log import ReadProtheusLogTool
from tools.implementations.tss_tools import (
    TSSExtractContextTool,
    TSSCheckUrlTool,
    TSSRequestLogTool,
    TSSAnalyzeLogTool,
)


class ToolRegistry:
    def __init__(self):
        self.tools = {
            # Existentes
            "read_logs":     ReadLogsTool(),
            "run_tests":     RunTestsTool(),
            # Novos
            "check_url":     CheckUrlTool(),
            "check_api":     CheckUrlTool(),       # alias
            "restart_ws":    RestartServiceTool(service="jobws"),
            "restart_rest":  RestartServiceTool(service="restserver"),
            "check_ws":      ReadProtheusLogTool(service="ws"),
            "read_logs_rh":  ReadProtheusLogTool(service="rh"),
            #TSS
            "tss_extract_context": TSSExtractContextTool(),
            "tss_check_url":       TSSCheckUrlTool(),
            "tss_request_log":     TSSRequestLogTool(),
            "tss_analyze_log":     TSSAnalyzeLogTool(),
        }

    def get(self, name: str):
        return self.tools.get(name)

    def list_tools(self) -> list:
        return list(self.tools.keys())
