WS_DOMAIN = {
    "domain": "ws",
    "intents": {
        "ws_error": {
            "keywords": ["ws", "websocket", "jobws", "preparein", "job server", "jobserver"],
            "plan": [
                {"tool": "check_ws"},
                {"tool": "restart_ws"}
            ]
        }
    }
}
