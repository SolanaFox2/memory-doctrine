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

import json
import os
from enum import Enum
from typing import Callable

# ── type alias ─────────────────────────────────────────────────────────────────

CompleteJSON = Callable[[str, dict], dict]

# ── model defaults ──────────────────────────────────────────────────────────────

_DEFAULT_MODEL: dict[str, str] = {
    "anthropic": "claude-sonnet-4-5",
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


def extract_json(text: str) -> dict:
    """Tolerant JSON extraction from the grounding prototype.

    Handles:
    - Bare JSON objects.
    - Objects wrapped in ``` or ```json fences.
    - Objects embedded in surrounding prose (falls back to first ``{...}``).
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


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


def _make_provider_by_name(family_name: str, *, model: str | None = None) -> CompleteJSON:
    """Internal dispatch by string name — raises ``ValueError`` for unknown families.

    Separated out so tests can reach the ValueError branch without constructing
    a real Family enum member.  Call ``make_provider(Family.X)`` in production.
    """
    if family_name == "anthropic":
        import anthropic  # type: ignore[import-untyped]  # lazy

        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        chosen_model = model or _DEFAULT_MODEL["anthropic"]

        def _anthropic_complete(prompt: str, schema: dict) -> dict:
            msg = client.messages.create(
                model=chosen_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return extract_json(msg.content[0].text.strip())

        return _anthropic_complete

    elif family_name == "deepseek":
        from openai import OpenAI  # type: ignore[import-untyped]  # lazy

        client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )
        chosen_model = model or _DEFAULT_MODEL["deepseek"]

        def _deepseek_complete(prompt: str, schema: dict) -> dict:
            resp = client.chat.completions.create(
                model=chosen_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=1024,
            )
            return extract_json(resp.choices[0].message.content)

        return _deepseek_complete

    elif family_name == "google":
        import google.generativeai as genai  # type: ignore[import-untyped]  # lazy

        genai.configure(api_key=os.environ["GOOGLE_GENAI_API_KEY"])
        chosen_model = model or _DEFAULT_MODEL["google"]
        _client = genai.GenerativeModel(chosen_model)

        def _google_complete(prompt: str, schema: dict) -> dict:
            resp = _client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    max_output_tokens=1024,
                ),
            )
            return extract_json(resp.text)

        return _google_complete

    else:
        raise ValueError(
            f"Unknown family {family_name!r}. "
            "Choose from: 'anthropic', 'deepseek', 'google'."
        )


# ── public factory ──────────────────────────────────────────────────────────────


def make_provider(family: Family, *, model: str | None = None) -> CompleteJSON:
    """Build a real ``CompleteJSON`` callable for *family*.

    SDK imports happen lazily inside this function so the module is importable
    without any LLM SDK installed.  **Never called in tests.**

    Parameters
    ----------
    family:
        The ``Family`` enum member selecting the provider.
    model:
        Override the default model name.  ``None`` uses the built-in default.

    Raises
    ------
    ValueError
        If *family* is not a recognised ``Family`` member (defensive guard).
    KeyError
        If the required env-key (e.g. ``ANTHROPIC_API_KEY``) is not set.
    """
    return _make_provider_by_name(family.value, model=model)
