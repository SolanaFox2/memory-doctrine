"""Multi-provider LLM seam for KPM Builder — API path.

This module provides ``complete_json(prompt, schema) -> dict`` callables
generalized across model *families* so a verifier can run on a DIFFERENT
family than the drafter (cross-family independence).

Subscription-mode note
----------------------
In *subscription mode* (i.e. when the user runs the KPM Builder as a
Claude Code skill without Anthropic API keys), the judgment roles are
Claude **subagents** dispatched by the skill's orchestration layer —
they never touch this module.  This module is the **API path only**.

Usage
-----
::

    from kpm_builder.providers import Family, make_provider, independence_label

    drafter_fn = make_provider(Family.ANTHROPIC)
    verifier_fn = make_provider(Family.DEEPSEEK)

    label = independence_label(Family.ANTHROPIC, Family.DEEPSEEK)
    # → "cross-family"

    result: dict = drafter_fn("Draft this idea…", schema)
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Callable

from package_research.llm_core import (
    ProviderJSONError,
    RetriesExhaustedError,
    TruncationError,
    check_truncation,
    extract_json,
    with_retry,
)

__all__ = [
    "CompleteJSON",
    "Family",
    "ProviderJSONError",
    "RetriesExhaustedError",
    "TruncationError",
    "available_families",
    "extract_json",
    "independence_label",
    "make_provider",
]

# ── type alias ─────────────────────────────────────────────────────────────────

CompleteJSON = Callable[[str, dict], dict]

# Generous default — the relate `propose` call returns an array over ALL axioms
# and routinely blew the old 1024 cap (REVIEW.md KPM-H2).
DEFAULT_MAX_TOKENS = 8192
DEFAULT_TIMEOUT = 120.0

# ── model defaults ──────────────────────────────────────────────────────────────

_DEFAULT_MODEL: dict[str, str] = {
    "anthropic": "claude-sonnet-4-6",
    "deepseek": "deepseek-chat",
    "google": "gemini-2.0-flash",
}

# ── Family enum ─────────────────────────────────────────────────────────────────


class Family(Enum):
    """Supported LLM provider families."""

    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GOOGLE = "google"


# ── env-key registry ───────────────────────────────────────────────────────────

_ENV_KEY: dict[Family, str] = {
    Family.ANTHROPIC: "ANTHROPIC_API_KEY",
    Family.DEEPSEEK: "DEEPSEEK_API_KEY",
    Family.GOOGLE: "GOOGLE_GENAI_API_KEY",
}

# ── helpers ────────────────────────────────────────────────────────────────────


def _require_env(family_name: str) -> str:
    """API key for *family_name* from the environment, or a RuntimeError naming
    the exact missing env var (REVIEW.md L1 — never a bare KeyError)."""
    env_var = _ENV_KEY[Family(family_name)]
    value = os.environ.get(env_var, "").strip()
    if not value:
        raise RuntimeError(
            f"{env_var} is not set — required to build the {family_name!r} provider."
        )
    return value


# ``extract_json`` is re-exported from the shared seam
# (package_research.llm_core): raw_decode-based, multi-object tolerant, raises
# typed ProviderJSONError with a response snippet.


def available_families() -> list[Family]:
    """Return the families whose env key is currently set (non-empty)."""
    return [
        family
        for family in Family
        if os.environ.get(_ENV_KEY[family], "").strip()
    ]


def independence_label(drafter: Family, verifier: Family) -> str:
    """Return ``"cross-family"`` if drafter and verifier differ, else ``"same-family"``."""
    return "cross-family" if verifier != drafter else "same-family"


# ── internal helper (testable without SDK) ─────────────────────────────────────


def _make_provider_by_name(
    family_name: str,
    *,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = 3,
) -> CompleteJSON:
    """Internal dispatch by string name — raises ``ValueError`` for unknown families.

    Separated out so tests can reach the ValueError branch without constructing
    a real Family enum member.  Call ``make_provider(Family.X)`` in production.

    Every returned callable shares the seam's robustness contract: transient
    API errors retry with backoff+jitter, a token-cap cut raises
    :class:`TruncationError`, and unparseable output raises a typed
    :class:`ProviderJSONError` carrying a response snippet (REVIEW.md
    KPM-H2/KPM-H3).
    """
    if family_name == "anthropic":
        api_key = _require_env(family_name)
        import anthropic  # type: ignore[import-untyped]  # lazy

        client = anthropic.Anthropic(api_key=api_key, timeout=timeout)
        chosen_model = model or _DEFAULT_MODEL["anthropic"]

        def _anthropic_complete(prompt: str, schema: dict) -> dict:
            def _send() -> str:
                msg = client.messages.create(
                    model=chosen_model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = msg.content[0].text.strip()
                check_truncation(getattr(msg, "stop_reason", None), text)
                return text

            return extract_json(with_retry(_send, max_retries=max_retries))

        return _anthropic_complete

    elif family_name == "deepseek":
        api_key = _require_env(family_name)
        from openai import OpenAI  # type: ignore[import-untyped]  # lazy

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=timeout,
        )
        chosen_model = model or _DEFAULT_MODEL["deepseek"]

        def _deepseek_complete(prompt: str, schema: dict) -> dict:
            def _send() -> str:
                resp = client.chat.completions.create(
                    model=chosen_model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=max_tokens,
                )
                choice = resp.choices[0]
                text = choice.message.content or ""
                check_truncation(getattr(choice, "finish_reason", None), text)
                return text

            return extract_json(with_retry(_send, max_retries=max_retries))

        return _deepseek_complete

    elif family_name == "google":
        api_key = _require_env(family_name)
        import google.generativeai as genai  # type: ignore[import-untyped]  # lazy

        genai.configure(api_key=api_key)
        chosen_model = model or _DEFAULT_MODEL["google"]
        _client = genai.GenerativeModel(chosen_model)

        def _google_complete(prompt: str, schema: dict) -> dict:
            def _send() -> str:
                resp = _client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        max_output_tokens=max_tokens,
                    ),
                    request_options={"timeout": timeout},
                )
                text = resp.text
                candidates = getattr(resp, "candidates", None) or []
                if candidates:
                    # Stringified enum: "FinishReason.MAX_TOKENS" matches the marker.
                    check_truncation(getattr(candidates[0], "finish_reason", None), text)
                return text

            return extract_json(with_retry(_send, max_retries=max_retries))

        return _google_complete

    else:
        raise ValueError(
            f"Unknown family {family_name!r}. "
            "Choose from: 'anthropic', 'deepseek', 'google'."
        )


# ── public factory ──────────────────────────────────────────────────────────────


def make_provider(
    family: Family,
    *,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = 3,
) -> CompleteJSON:
    """Build a real ``CompleteJSON`` callable for *family*.

    SDK imports happen lazily inside this function so the module is importable
    without any LLM SDK installed.  **Never called in tests.**

    Parameters
    ----------
    family:
        The ``Family`` enum member selecting the provider.
    model:
        Override the default model name.  ``None`` uses the built-in default.
    max_tokens:
        Response token cap (default ``DEFAULT_MAX_TOKENS``); a response that
        hits it raises :class:`TruncationError` instead of silently parsing a
        partial object.
    timeout:
        Per-request timeout in seconds, so a hung call can't hang a build.
    max_retries:
        Backoff retries for transient API errors (429/5xx/connection).

    Raises
    ------
    ValueError
        If *family* is not a recognised ``Family`` member (defensive guard).
    RuntimeError
        If the required env-key (e.g. ``ANTHROPIC_API_KEY``) is not set —
        the message names the exact variable (REVIEW.md L1).
    """
    return _make_provider_by_name(
        family.value,
        model=model,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries,
    )
