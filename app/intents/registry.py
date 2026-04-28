from intents.domains.ws import WS_DOMAIN
from intents.domains.rest import REST_DOMAIN
from intents.domains.rh import RH_DOMAIN
from intents.domains.tss import TSS_DOMAIN

DOMAINS = [
    WS_DOMAIN,
    REST_DOMAIN,
    RH_DOMAIN,
    TSS_DOMAIN,
]

def get_all_intents():
    intents = {}
    for domain in DOMAINS:
        for intent_name, intent_data in domain["intents"].items():
            intents[intent_name] = {
                **intent_data,
                "domain": domain["domain"]
            }
    return intents
