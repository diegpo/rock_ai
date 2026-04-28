"""
Domínios de intenção específicos para o Protheus.
Organizado por módulo/serviço.
"""

# ─── AppServer / JobServer ─────────────────────────────────────────
APPSERVER_DOMAIN = {
    "domain": "appserver",
    "intents": {
        "appserver_down": {
            "keywords": ["appserver", "app server", "servidor caiu", "servidor fora"],
            "plan": [
                {"tool": "check_url"},
                {"tool": "read_protheus_log"},
                {"tool": "restart_service", "params": {"service": "appserver"}}
            ]
        },
        "jobserver_error": {
            "keywords": ["jobws", "jobserver", "job server", "preparein", "schedule"],
            "plan": [
                {"tool": "read_protheus_log"},
                {"tool": "check_url"},
                {"tool": "restart_service", "params": {"service": "jobserver"}}
            ]
        }
    }
}

# ─── REST / WebService ────────────────────────────────────────────
REST_DOMAIN = {
    "domain": "rest",
    "intents": {
        "rest_error": {
            "keywords": ["rest", "api", "endpoint", "401", "403", "500", "licenças rest"],
            "plan": [
                {"tool": "check_url"},
                {"tool": "run_tests"},
            ]
        },
        "ws_error": {
            "keywords": ["ws", "webservice", "wsdl", "soap"],
            "plan": [
                {"tool": "check_ws"},
                {"tool": "read_protheus_log"}
            ]
        }
    }
}

# ─── Módulo RH / Meu RH ──────────────────────────────────────────
RH_DOMAIN = {
    "domain": "rh",
    "intents": {
        "rh_error": {
            "keywords": ["rh", "meu rh", "folha", "holerite", "ponto", "srh"],
            "plan": [
                {"tool": "read_logs_rh"},
                {"tool": "read_protheus_log"},
            ]
        }
    }
}

# ─── DBAccess / Banco ────────────────────────────────────────────
DB_DOMAIN = {
    "domain": "database",
    "intents": {
        "db_error": {
            "keywords": ["dbaccess", "db access", "banco", "sqlserver", "oracle", "conexão banco", "lock"],
            "plan": [
                {"tool": "read_protheus_log"},
            ]
        }
    }
}

# ─── Licenças ────────────────────────────────────────────────────
LICENSE_DOMAIN = {
    "domain": "license",
    "intents": {
        "license_error": {
            "keywords": ["licença", "license", "licencias", "sem licença", "token expirado"],
            "plan": [
                {"tool": "check_url"},
                {"tool": "read_logs"},
            ]
        }
    }
}
