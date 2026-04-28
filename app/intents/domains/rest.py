REST_DOMAIN = {
    "domain": "rest",
    "intents": {
        "rest_error": {
            "keywords": ["rest", "api", "endpoint", "licença", "license", "token", "428", "500"],
            "plan": [
                {"tool": "check_api"},
                {"tool": "run_tests"},
                {"tool": "restart_rest"}
            ]
        }
    }
}
