"""kpm_builder.refute — adversarial refuter (engine module).

Tries to BREAK a claim using corpus evidence that is independent of the
claim's own supporting passage.  Using only the claim's own support to
"challenge" it would be circular; true adversarial review requires independent
evidence.

HONESTY NOTE
------------
A clean refutation over a *uniform* corpus does NOT prove the claim true.
Absence of a defeater in this corpus is not proof — the corpus could be
uniformly wrong, incomplete, or biased in the same direction as the claim.
The engine treats a *refuted* claim by downgrading its confidence; that
downgrade happens in the orchestrator, not here.  This module reports only
whether independent counter-evidence was found.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# ── type alias ─────────────────────────────────────────────────────────────────

CompleteJSON = Callable[[str, dict], dict]

# ── response schema ────────────────────────────────────────────────────────────

REFUTE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "refuted": {"type": "boolean"},
        "counter": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["refuted", "counter", "reason"],
    "additionalProperties": False,
}

# ── system prompt ──────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are an adversarial fact-checker.  Your task is to find evidence in the
PROVIDED PASSAGES that CONTRADICTS or materially undermines the CLAIM.

Rules:
1. Use ONLY the provided passages as your evidence.  Do not use outside knowledge.
2. If you find a passage that contradicts or significantly undermines the claim,
   set refuted=true and quote or paraphrase the specific counter-evidence in
   "counter".
3. If no passage in the list contradicts the claim, set refuted=false and leave
   "counter" empty.
4. "reason" must be a one-sentence justification.
5. Respond with valid JSON matching the provided schema.  No markdown fences.
"""


def _build_prompt(claim: str, independent_passages: list[str]) -> str:
    """Construct the adversarial prompt from the claim and independent passages only."""
    if independent_passages:
        numbered = "\n".join(
            f"[{i + 1}] {p}" for i, p in enumerate(independent_passages)
        )
    else:
        numbered = "(no independent passages available)"

    return (
        f"{_SYSTEM_PROMPT}\n\n"
        f"CLAIM:\n{claim}\n\n"
        f"INDEPENDENT PASSAGES (the claim's own source is NOT included):\n"
        f"{numbered}\n\n"
        "Respond with JSON only."
    )


# ── result dataclass ───────────────────────────────────────────────────────────

@dataclass
class RefuteResult:
    refuted: bool          # did the corpus yield evidence that breaks the claim?
    counter: str = ""      # the counter-evidence found (empty if not refuted)
    reason: str = ""


# ── core function ──────────────────────────────────────────────────────────────

def refute(
    claim: str,
    own_support: str,
    corpus: list[str],
    *,
    complete_json: CompleteJSON,
) -> RefuteResult:
    """Try to find independent corpus evidence that breaks *claim*.

    Parameters
    ----------
    claim:
        The statement being challenged.
    own_support:
        The passage that was used to *support* the claim.  It is EXCLUDED from
        the evidence the judge sees — showing the judge its own support would
        be circular.
    corpus:
        All available passages (may include ``own_support``).
    complete_json:
        Injected callable ``(prompt, schema) -> dict``.  Never receives
        ``own_support``.

    Returns
    -------
    RefuteResult
        ``refuted=True`` when an independent passage contradicts the claim;
        ``refuted=False`` otherwise (including when no independent passages
        exist — an empty evidence set cannot refute anything).
    """
    # 1. INDEPENDENCE: exclude the claim's own support
    independent = [p for p in corpus if p.strip() != own_support.strip()]

    # 2. Short-circuit: no independent evidence → cannot refute
    if not independent:
        return RefuteResult(
            refuted=False,
            counter="",
            reason="No independent passages available; cannot refute.",
        )

    # 3. Build and send the prompt
    prompt = _build_prompt(claim, independent)
    raw: dict = complete_json(prompt, REFUTE_SCHEMA)

    # 4. Map defensively to RefuteResult
    return RefuteResult(
        refuted=bool(raw.get("refuted", False)),
        counter=str(raw.get("counter", "")),
        reason=str(raw.get("reason", "")),
    )
