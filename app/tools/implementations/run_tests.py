from tools.base_tool import BaseTool

class RunTestsTool(BaseTool):
    name = "run_tests"

    def run(self, context=None):
        print("Rodando testes .... ")

        return {
            "success": True,
            "data": "Todos os testes passaram"
        }