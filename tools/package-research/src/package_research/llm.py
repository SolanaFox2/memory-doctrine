"""Thin Anthropic client wrapper for JSON-schema'd, validated LLM calls.

Design goal: **mockable**. Every LLM-backed stage (distill/score/verify)
depends only on a ``complete_json(prompt, schema) -> dict`` callable, not on
the Anthropic SDK directly. In production we pass :class:`LLMClient.complete_json`;
in tests we pass a fake callable that returns fixed JSON — so the stages run
with NO API key.

Robustness (shared seam, see :mod:`package_research.llm_core`):

- Transient API errors (429/5xx/connection blips) retry with exponential
  backoff + jitter; deterministic failures don't burn retries.
- A response cut off at ``max_tokens`` raises :class:`~package_research.llm_core.TruncationError`
  instead of silently parsing a partial object.
- A malformed (non-JSON) response gets ONE corrective follow-up turn —
  the bad reply plus an instruction to emit only the JSON object — rather
  than re-sending the identical prompt.
"""

from __future__ import annotations

import json
from typing import Any, Optional, Protocol

from .llm_core import (
    CompleteJSON,
    LLMError,
    ProviderJSONError,
    RetriesExhaustedError,
    TruncationError,
    check_truncation,
    extract_json,
    with_retry,
)

__all__ = [
    "CompleteJSON",
    "CompletionProvider",
    "LLMClient",
    "LLMError",
    "ProviderJSONError",
    "RetriesExhaustedError",
    "TruncationError",
]

# Backwards-compatible alias; the canonical implementation lives in llm_core.
_extract_json = extract_json

_CORRECTIVE_FOLLOW_UP = (
    "Your previous reply was not a valid JSON object conforming to the schema. "
    "Respond again with ONLY the JSON object — no prose, no code fences."
)


class CompletionProvider(Protocol):
    """Anything that can turn a prompt + JSON schema into a parsed dict."""

    def complete_json(self, prompt: str, schema: dict) -> dict: ...


class LLMClient:
    """Production wrapper around the Anthropic SDK.

    Lazily imports ``anthropic`` so the module (and the deterministic ingest
    stage / mocked tests) imports cleanly without the SDK or an API key.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5",
        client: Any = None,
        max_retries: int = 3,
        max_tokens: int = 4096,
        timeout: float = 120.0,
        sleep: Any = None,
    ) -> None:
        self.model = model
        self.max_retries = max_retries
        self.max_tokens = max_tokens
        self._sleep = sleep  # injectable for tests; None -> time.sleep
        if client is not None:
            self._client = client
        else:
            import anthropic  # lazy: only needed for real calls

            self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout)

    def complete_json(self, prompt: str, schema: dict) -> dict:
        """Call the model and return parsed, schema-described JSON.

        Transient API errors retry with backoff. A truncated response raises
        :class:`TruncationError` (raise ``max_tokens`` or shrink the prompt).
        A malformed response triggers one corrective follow-up turn before
        failing with :class:`ProviderJSONError`.
        """
        system = (
            "You are a precise extraction engine. Respond with ONE JSON object "
            "and nothing else. It must conform to this JSON schema:\n" + json.dumps(schema, indent=2)
        )
        convo: list[dict] = [{"role": "user", "content": prompt}]

        try:
            return self._attempt(system, convo)
        except TruncationError:
            raise  # a corrective turn can't fix a token-cap cut
        except ProviderJSONError:
            bad_text = self._last_text or "(empty response)"
            convo = convo + [
                {"role": "assistant", "content": bad_text},
                {"role": "user", "content": _CORRECTIVE_FOLLOW_UP},
            ]
            return self._attempt(system, convo)

    # ── internals ───────────────────────────────────────────────────────────

    _last_text: str = ""

    def _attempt(self, system: str, messages: list[dict]) -> dict:
        """One parse attempt: API call (with transient-error retry) + extract."""
        retry_kwargs: dict = {"max_retries": self.max_retries}
        if self._sleep is not None:
            retry_kwargs["sleep"] = self._sleep
        resp = with_retry(
            lambda: self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages,
            ),
            **retry_kwargs,
        )
        text = _response_text(resp)
        self._last_text = text
        check_truncation(getattr(resp, "stop_reason", None), text)
        return extract_json(text)


def _response_text(resp: Any) -> str:
    """Extract concatenated text from an Anthropic Messages response."""
    content = getattr(resp, "content", None)
    if content is None and isinstance(resp, dict):
        content = resp.get("content")
    parts: list[str] = []
    for block in content or []:
        t = getattr(block, "text", None)
        if t is None and isinstance(block, dict):
            t = block.get("text")
        if t:
            parts.append(t)
    return "".join(parts)
