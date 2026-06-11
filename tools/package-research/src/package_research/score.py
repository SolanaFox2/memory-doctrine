"""Score stage — LLM-backed (doctrine C1: confidence is earned from evidence).

Takes each distilled :class:`Idea` and asks the model to judge two numbers from
the *evidence actually present* — never from how fluent the statement sounds:

* ``confidence`` — float in [0, 1], grounded in the supporting snippets.
* ``generativity`` — int in 1..5, how load-bearing the idea is.

plus a short ``rationale``. Returns :class:`ScoredIdea` objects.

Like distill, the LLM dependency is injected as a
``complete_json(prompt, schema) -> dict`` callable, so this stage is fully
testable WITHOUT an API key: pass a fake callable that returns fixed JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .distill import Idea
from .llm import CompleteJSON

_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "score.md"

# JSON schema handed to the model (and to complete_json) to constrain output.
SCORE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "generativity": {"type": "integer", "minimum": 1, "maximum": 5},
        "rationale": {"type": "string"},
    },
    "required": ["confidence", "generativity", "rationale"],
}


@dataclass
class ScoredIdea(Idea):
    """An :class:`Idea` with doctrine-C1 scores attached.

    ``confidence`` is clamped to [0, 1] and ``generativity`` to 1..5 so that
    downstream notes always satisfy the doctrine lint regardless of model drift.
    """

    confidence: float = 0.0
    generativity: int = 1
    rationale: str = ""


def load_prompt() -> str:
    """Load the doctrine-grounded (C1) score rubric text."""
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _render_idea(idea: Idea) -> str:
    files = ", ".join(Path(f).name for f in idea.supporting_source_files) or "(none)"
    if idea.supporting_snippets:
        snippets = "\n".join(f"- {s.strip()}" for s in idea.supporting_snippets)
    else:
        snippets = "(no supporting snippets present)"
    return (
        f"## Idea\n{idea.statement.strip()}\n\n"
        f"## Supporting source files\n{files}\n\n"
        f"## Supporting snippets\n{snippets}\n"
    )


def build_prompt(idea: Idea) -> str:
    """Assemble the full score prompt: C1 rubric + the rendered idea."""
    rubric = load_prompt()
    return f"{rubric}\n\n---\n\n{_render_idea(idea)}"


def _clamp_confidence(value: object) -> float:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 0.0
    if c < 0.0:
        return 0.0
    if c > 1.0:
        return 1.0
    return c


def _clamp_generativity(value: object) -> int:
    try:
        g = int(value)
    except (TypeError, ValueError):
        return 1
    if g < 1:
        return 1
    if g > 5:
        return 5
    return g


def score_idea(idea: Idea, complete_json: CompleteJSON) -> ScoredIdea:
    """Score a single idea against doctrine C1, returning a ScoredIdea."""
    prompt = build_prompt(idea)
    result = complete_json(prompt, SCORE_SCHEMA)
    if not isinstance(result, dict):
        result = {}
    return ScoredIdea(
        statement=idea.statement,
        supporting_source_files=list(idea.supporting_source_files),
        supporting_snippets=list(idea.supporting_snippets),
        confidence=_clamp_confidence(result.get("confidence")),
        generativity=_clamp_generativity(result.get("generativity")),
        rationale=(result.get("rationale") or "").strip(),
    )


def score(ideas: List[Idea], complete_json: CompleteJSON) -> List[ScoredIdea]:
    """Score every idea (one LLM call each), preserving order.

    Args:
        ideas: The deduped ideas from the distill stage.
        complete_json: A ``(prompt, schema) -> dict`` callable. In production
            pass ``LLMClient.complete_json``; in tests pass a fake that returns
            fixed JSON so no API key is required.
    """
    return [score_idea(idea, complete_json) for idea in ideas]
