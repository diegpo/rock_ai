RH_DOMAIN = {
    "domain": "rh",
    "intents": {
        "rh_error": {
            "keywords": ["rh", "meu rh", "meurh", "ponto", "folha", "holerite", "colaborador"],
            "plan": [
                {"tool": "read_logs_rh"},
                {"tool": "check_api"}
            ]
        }
    }
}
