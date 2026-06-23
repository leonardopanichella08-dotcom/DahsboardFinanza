from fastapi import Header, HTTPException
from app.core.config import settings


def get_api_key(x_api_key: str = Header(default="")) -> str:
    """
    Clients may pass their own Anthropic API key via X-Api-Key header,
    or the server falls back to the configured key from environment.
    """
    key = x_api_key or settings.ANTHROPIC_API_KEY
    if not key:
        raise HTTPException(status_code=401, detail="Anthropic API key not configured")
    return key
