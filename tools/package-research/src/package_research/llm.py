"""Thin Anthropic client wrapper for JSON-schema'd, validated LLM calls.

Design goal: **mockable**. Every LLM-backed stage (distill/score/verify)
depends only on a ``complete_json(prompt, schema) -> dict`` callable, not on
the Anthropic SDK directly. In production we pass :class:`LLMClient.complete_json`;
in tests we pass a fake callable that returns fixed JSON — so the stages run
with NO API key.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Optional, Protocol

# A stage only ever needs this shape. This is the seam tests inject at.
CompleteJSON = Callable[[str, dict], dict]


class CompletionProvider(Protocol):
    """Anything that can turn a prompt + JSON schema into a parsed dict."""

    def complete_json(self, prompt: str, schema: dict) -> dict: ...


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response.

    Tolerates fenced ```json blocks and leading/trailing prose.
    """
    text = text.strip()
    if text.startswith("```"):
        # Strip a leading fence line and any trailing fence.
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


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
        max_retries: int = 2,
        max_tokens: int = 4096,
    ) -> None:
        self.model = model
        self.max_retries = max_retries
        self.max_tokens = max_tokens
        if client is not None:
            self._client = client
        else:
            import anthropic  # lazy: only needed for real calls

            self._client = anthropic.Anthropic(api_key=api_key)

    def complete_json(self, prompt: str, schema: dict) -> dict:
        """Call the model and return parsed, schema-described JSON.

        The schema is embedded in the prompt to steer the model toward the
        required shape. Retries on transient parse/API failures.
        """
        system = (
            "You are a precise extraction engine. Respond with ONE JSON object "
            "and nothing else. It must conform to this JSON schema:\n" + json.dumps(schema, indent=2)
        )

        last_err: Optional[Exception] = None
        for _attempt in range(self.max_retries + 1):
            try:
                resp = self._client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = _response_text(resp)
                return _extract_json(text)
            except Exception as exc:  # noqa: BLE001 - retry any transient failure
                last_err = exc
        raise RuntimeError(f"LLM call failed after {self.max_retries + 1} attempts: {last_err}") from last_err


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
