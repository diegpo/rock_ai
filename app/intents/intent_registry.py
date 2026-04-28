INTENTS = {
    "backend.ws_error": {
        "keywords": ["ws", "jobws", "preparein"],
        "plan": [
            {"tool": "check_ws"},
            {"tool": "restart_ws"}
        ]
    },

    "backend.rest_error": {
        "keywords": ["rest", "api", "endpoint", "licenças"],
        "plan": [
            {"tool": "check_api"},
            {"tool": "run_test_api"},
            {"tool": "test_license"}
        ]
    },

    "app_rh_error": {
        "keywords": ["rh", "meu_rh"],
        "plan": [
            {"tool": "read_logs_rh"},
            {"tool": "fix_rh"},
            {"tool": "check_ini"},
            {"tool": "check_rest"}
        ]
    }
}