DEFAULT_PROVIDER_WEIGHTS = {
    "openai": 1.0,
    "anthropic": 1.0,
    "google": 1.0,
    "llama": 0.8,
}


def provider_weight(provider: str) -> float:
    return DEFAULT_PROVIDER_WEIGHTS.get(provider, 1.0)
