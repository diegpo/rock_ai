import requests
from tools.base_tool import BaseTool


class CheckUrlTool(BaseTool):
    name = "check_url"

    def run(self, context=None) -> dict:
        url = (context or {}).get("url", "http://localhost:8080")
        try:
            r = requests.get(url, timeout=5)
            return {
                "success": True,
                "data": f"URL {url} respondeu com status {r.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": f"URL {url} inacessível: {e}"
            }
