TSS_DOMAIN = {
    "domain": "tss",
    "intents": {
        "tss_nfse_error": {
            "keywords": [
                "nfs", "nfse", "nfs-e", "nfs_e",
                "nota fiscal", "transmitir nota", "transmissao",
                "prefeitura", "tss",
                "internal server error",
            ],
            "plan": [
                {"tool": "tss_extract_context"},
                {"tool": "tss_check_url"},
                {"tool": "tss_request_log"},
            ]
        }
    }
}