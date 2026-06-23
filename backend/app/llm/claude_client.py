"""
Thin wrapper around the Anthropic Python SDK.
All LLM calls go through here for consistent error handling and JSON parsing.
"""
import json
import logging
from typing import Any

import anthropic
from anthropic import AsyncAnthropic

from app.llm.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client: AsyncAnthropic | None = None


def get_client(api_key: str) -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=api_key)
    return _client


async def call_claude(
    prompt: str,
    api_key: str,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 1024,
) -> dict[str, Any] | list[Any]:
    """
    Call Claude and parse the response as JSON.
    Returns the parsed object or raises ValueError on parse failure.
    """
    client = get_client(api_key)
    try:
        message = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = message.content[0].text.strip()

        # Strip markdown fences if Claude added them despite instructions
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0]

        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error("Claude returned non-JSON: %s", raw_text[:200])
        raise ValueError(f"LLM response was not valid JSON: {e}") from e
    except anthropic.APIError as e:
        logger.error("Anthropic API error: %s", e)
        raise
