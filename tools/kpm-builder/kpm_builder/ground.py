"""kpm_builder.ground — entailment grounder (engine module).

Promoted from the grounding prototype.  Key differences vs the prototype:
- Takes a ``Snapshot`` (for provenance) instead of a raw ``source_text`` string.
- Receives ONLY the claim + snapshot.text (no drafter reasoning) — isolation is
  the point.  The verifier must not see the drafter's conclusions.

Design note
-----------
The ``complete_json`` seam is injected so that all unit tests pass a *fake*
callable — no real LLM SDK is imported at module level.  Real providers are
constructed via ``make_provider()`` (lazy SDK imports).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from kpm_builder.snapshot import Snapshot

# ── type alias ────────────────────────────────────────────────────────────────

CompleteJSON = Callable[[str, dict], dict]

# ── response schema (from the grounding prototype) ────────────────────────────

RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["entails", "over_claims", "reject"],
            "description": (
                "'entails' = claim is fully and faithfully supported by the source; "
                "'over_claims' = claim asserts more generality, certainty, scope, "
                "quantity, or recency than the source warrants; "
                "'reject' = source contains no support for the claim at all."
            ),
        },
        "supported_paraphrase": {
            "type": "string",
            "description": (
                "A faithful restatement of what the source DOES support "
                "regarding the topic of the claim. Empty string if nothing relevant."
            ),
        },
        "dropped": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "For 'over_claims': list the specific unsupported elements "
                "(e.g. 'universalised scope', 'fabricated statistic'). "
                "Empty list otherwise."
            ),
        },
        "reason": {
            "type": "string",
            "description": "One-sentence justification for the verdict.",
        },
    },
    "required": ["verdict", "supported_paraphrase", "dropped", "reason"],
    "additionalProperties": False,
}

_VALID_VERDICTS = {"entails", "over_claims", "reject"}

# ── system prompt (from the grounding prototype) ──────────────────────────────

_SYSTEM_PROMPT = """\
You are an independent fact-verifier. Your task is to decide whether a
CLAIM is fully entailed by a SOURCE PASSAGE — meaning the claim asserts
no more generality, certainty, scope, quantity, or recency than the
source explicitly supports.

Rules:
1. Use ONLY the SOURCE PASSAGE as your evidence. Do not use outside knowledge.
2. Verdict 'entails': every assertion in the claim is directly supported.
3. Verdict 'over_claims': the claim adds scope, certainty, universality, or
   numbers not present in the source (even if partly related).
4. Verdict 'reject': the source contains no relevant support for the claim.
5. Produce valid JSON matching the provided schema. No markdown fences.
"""


def _build_prompt(claim: str, source_text: str) -> str:
    """Build the verifier prompt from the claim and the raw source text only."""
    return (
        f"{_SYSTEM_PROMPT}\n\n"
        f"SOURCE PASSAGE:\n{source_text}\n\n"
        f"CLAIM TO VERIFY:\n{claim}\n\n"
        "Respond with JSON only."
    )


# ── result dataclass ──────────────────────────────────────────────────────────

@dataclass
class GroundResult:
    verdict: str              # "entails" | "over_claims" | "reject"
    supported_paraphrase: str = ""
    dropped: list[str] = field(default_factory=list)
    reason: str = ""


# ── core function ─────────────────────────────────────────────────────────────

def ground(
    claim: str,
    snapshot: Snapshot,
    *,
    complete_json: CompleteJSON,
) -> GroundResult:
    """Verify whether *snapshot* entails *claim*.

    Builds a prompt from the claim and ``snapshot.text`` ONLY — no drafter
    rationale is passed (independent verifier isolation).

    The ``complete_json`` callable returns an already-parsed dict; this function
    maps it defensively to a ``GroundResult``.  Unknown or missing verdicts are
    coerced to ``"reject"`` (safe default).  A non-list ``dropped`` is coerced
    to ``[]``.

    Parameters
    ----------
    claim:
        The statement to verify against the source.
    snapshot:
        The content-addressed source record; only ``snapshot.text`` is used.
    complete_json:
        Injected callable ``(prompt, schema) -> dict``.  Never called with
        anything beyond the claim + source text.
    """
    prompt = _build_prompt(claim, snapshot.text)
    raw: dict = complete_json(prompt, RESPONSE_SCHEMA)

    verdict_raw = raw.get("verdict", "")
    verdict = verdict_raw if verdict_raw in _VALID_VERDICTS else "reject"

    dropped_raw = raw.get("dropped", [])
    if not isinstance(dropped_raw, list):
        dropped_raw = []

    return GroundResult(
        verdict=verdict,
        supported_paraphrase=str(raw.get("supported_paraphrase", "")),
        dropped=[str(d) for d in dropped_raw],
        reason=str(raw.get("reason", "")),
    )
