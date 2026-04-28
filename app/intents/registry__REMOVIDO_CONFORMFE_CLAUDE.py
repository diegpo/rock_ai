from intents.domais.ws import WS_DOMAIN
from intents.domais.rest import REST_DOMAIN
from intents.domais.rh import RH_DOMAIN

DOMAINS = [
        WS_DOMAIN,
        REST_DOMAIN,
        RH_DOMAIN
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