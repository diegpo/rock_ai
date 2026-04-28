from tools.base_tool import BaseTool

class ReadLogsTool(BaseTool):
    name = "read_logs"

    def run(self, context=None):
        print("Lendo logs... ")

        return{
            "success": True,
            "data": "Erro 404 encontrado no sistema"
        }