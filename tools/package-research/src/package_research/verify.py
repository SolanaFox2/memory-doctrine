"""Verify stage — LLM adversarial (doctrine E4: refute by default + citation presence).

For each :class:`ScoredIdea` this stage runs two gates:

1. **Citation-presence** (deterministic). An idea must cite at least one real
   supporting snippet drawn from the sources. An idea with no supporting snippet
   fails immediately — confidence is earned from evidence actually present, never
   from fluency. This gate runs WITHOUT any LLM, so it always holds.

2. **Refute-by-default** (LLM). A ``complete_json`` call that tries to *break*
   the idea given only its snippets, returning
   ``{survives: bool, reason, adjusted_confidence}``. Ideas that do not survive
   are dropped; survivors are down-scored to the confidence the present evidence
   licenses (never raised above their prior confidence).

The LLM dependency is injected as a ``complete_json(prompt, schema) -> dict``
callable, so this stage is fully testable WITHOUT an API key: pass a fake
callable that returns fixed JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .llm import CompleteJSON
from .llm_core import UNTRUSTED_PREAMBLE, coerce_result_dict, delimit_untrusted
from .score import ScoredIdea

_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "verify.md"

# JSON schema handed to the model (and to complete_json) to constrain output.
VERIFY_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "survives": {"type": "boolean"},
        "reason": {"type": "string"},
        "adjusted_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["survives", "reason", "adjusted_confidence"],
}


@dataclass
class VerificationResult:
    """The outcome of verifying one idea: which gate it hit and why."""

    idea: ScoredIdea
    survived: bool
    has_citation: bool
    reason: str = ""
    adjusted_confidence: float = 0.0


def load_prompt() -> str:
    """Load the doctrine-grounded (E4) refute-by-default prompt text."""
    return _PROMPT_PATH.read_text(encoding="utf-8")


def has_citation(idea: ScoredIdea) -> bool:
    """Deterministic citation-presence check (doctrine E4 / C1).

    True iff the idea cites at least one non-empty supporting snippet. This is
    the floor: no snippet => no admission, regardless of what the model says.
    """
    return any(s.strip() for s in idea.supporting_snippets)


def _render_idea(idea: ScoredIdea) -> str:
    files = ", ".join(Path(f).name for f in idea.supporting_source_files) or "(none)"
    if idea.supporting_snippets:
        # Snippets are verbatim untrusted source text — delimited as data.
        snippets = delimit_untrusted(
            "\n".join(f"- {s.strip()}" for s in idea.supporting_snippets)
        )
    else:
        snippets = "(no supporting snippets present)"
    return (
        f"## Idea\n{idea.statement.strip()}\n\n"
        f"## Prior confidence\n{idea.confidence}\n\n"
        f"## Supporting source files\n{files}\n\n"
        f"## Supporting snippets\n{snippets}\n"
    )


def build_prompt(idea: ScoredIdea) -> str:
    """Assemble the full verify prompt: E4 rubric + the rendered idea."""
    rubric = load_prompt()
    return f"{rubric}\n\n{UNTRUSTED_PREAMBLE}\n\n---\n\n{_render_idea(idea)}"


def _clamp_confidence(value: object, fallback: float) -> float:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return fallback
    if c < 0.0:
        return 0.0
    if c > 1.0:
        return 1.0
    return c


def verify_idea(idea: ScoredIdea, complete_json: CompleteJSON) -> VerificationResult:
    """Verify a single idea against doctrine E4.

    Citation-presence is checked first and deterministically. Only if it passes
    do we spend an LLM call on the adversarial refutation. A survivor's
    confidence is down-scored to ``min(prior, adjusted)`` — verification can
    lower confidence but never raise it.
    """
    cited = has_citation(idea)
    if not cited:
        return VerificationResult(
            idea=idea,
            survived=False,
            has_citation=False,
            reason="no supporting snippet (citation-presence gate)",
            adjusted_confidence=0.0,
        )

    result = coerce_result_dict(
        complete_json(build_prompt(idea), VERIFY_SCHEMA), stage="verify", required_key="survives"
    )

    survives = bool(result.get("survives"))
    adjusted = _clamp_confidence(result.get("adjusted_confidence"), idea.confidence)
    # Verification may only down-score a survivor, never raise its confidence.
    adjusted = min(idea.confidence, adjusted)

    return VerificationResult(
        idea=idea,
        survived=survives,
        has_citation=True,
        reason=(result.get("reason") or "").strip(),
        adjusted_confidence=adjusted,
    )


def verify(scored_ideas: List[ScoredIdea], complete_json: CompleteJSON) -> List[ScoredIdea]:
    """Run the E4 adversarial + citation-presence gates over all scored ideas.

    Drops ideas that fail citation-presence or are refuted; returns the
    survivors with their confidence down-scored to what the present evidence
    licenses (order preserved).

    Args:
        scored_ideas: The scored ideas from the score stage.
        complete_json: A ``(prompt, schema) -> dict`` callable. In production
            pass ``LLMClient.complete_json``; in tests pass a fake that returns
            fixed JSON so no API key is required.
    """
    survivors: List[ScoredIdea] = []
    for idea in scored_ideas:
        res = verify_idea(idea, complete_json)
        if not (res.survived and res.has_citation):
            continue
        survivors.append(
            ScoredIdea(
                statement=idea.statement,
                supporting_source_files=list(idea.supporting_source_files),
                supporting_snippets=list(idea.supporting_snippets),
                confidence=res.adjusted_confidence,
                generativity=idea.generativity,
                rationale=idea.rationale,
            )
        )
    return survivors
