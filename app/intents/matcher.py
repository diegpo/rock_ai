from intents.registry import DOMAINS

class IntentMatcher:
    def match(self, text: str) -> dict:
        text = text.lower()
        for domain in DOMAINS:
            for intent_name, intent in domain["intents"].items():
                for keyword in intent.get("keywords", []):
                    if keyword.lower() in text:
                        return {
                            "domain": domain["domain"],
                            "intent": intent_name,
                            "plan":   intent.get("plan", [])
                        }
        return {"domain": "unknown", "intent": "unknown", "plan": []}
