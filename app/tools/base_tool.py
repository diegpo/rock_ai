class BaseTool:
    name = "base_tool"

    def run(self, context=None):
        raise NotImplementedError