"""
kpm_builder.schema
------------------
Internal idea record — a richer superset of a knowledge-claim that carries
provenance and adversarial-review state.

Design constraints:
- INTERNAL ONLY (never the public schema)
- NO LLM, NO API keys, NO network calls
- stdlib only: dataclasses, enum
- Three-orderings rule: confidence and generativity are SEPARATE.
  A generativity scorer MUST NEVER see the confidence value.
  This is a falsifiable contract enforced by generativity_input().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from kpm_builder.snapshot import SpanRef


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SourceTier(Enum):
    """Ordered best → worst; the int value encodes rank (lower = better)."""
    PEER_REVIEWED  = 0
    PREPRINT       = 1
    OFFICIAL_DOCS  = 2
    REPUTABLE_PRESS = 3
    BLOG           = 4
    UNKNOWN        = 5


class ConfidenceBucket(Enum):
    """Ordinal confidence bucket (internal)."""
    SUPPORTED   = "supported"
    PARTIAL     = "partial"
    UNVERIFIED  = "unverified"


# ---------------------------------------------------------------------------
# ScoredIdea
# ---------------------------------------------------------------------------

@dataclass
class ScoredIdea:
    """
    Internal idea record with provenance + adversarial-review state.

    Fields
    ------
    statement     : The knowledge claim.
    source_ref    : Source identifier / URL.
    span          : The verbatim supporting span; None until grounded.
    source_tier   : Quality tier of the source.
    access_level  : "full_text" | "abstract_only" | "secondary"
    confidence    : Ordinal bucket (INTERNAL — not exposed to generativity scorer).
    generativity  : 1..5 (ValueError if outside range).
    contradicts   : IDs of claims this idea opposes.
    defeaters     : IDs of hypotheses that would defeat this idea.
    rationale     : Free-text justification.
    """
    statement: str
    source_ref: str
    span: SpanRef | None
    source_tier: SourceTier
    access_level: str
    confidence: ConfidenceBucket
    generativity: int
    contradicts: list[str] = field(default_factory=list)
    defeaters: list[str] = field(default_factory=list)
    rationale: str = ""

    def __post_init__(self) -> None:
        if not (1 <= self.generativity <= 5):
            raise ValueError(
                f"generativity must be in 1..5, got {self.generativity!r}"
            )


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _span_to_dict(span: SpanRef) -> dict[str, Any]:
    return {
        "sha256": span.sha256,
        "start": span.start,
        "end": span.end,
        "text": span.text,
    }


def _span_from_dict(d: dict[str, Any]) -> SpanRef:
    return SpanRef(
        sha256=d["sha256"],
        start=d["start"],
        end=d["end"],
        text=d["text"],
    )


def to_dict(idea: ScoredIdea) -> dict[str, Any]:
    """
    Serialise a ScoredIdea to a plain dict.

    - SourceTier  → serialised by .name  (e.g. "PEER_REVIEWED")
    - ConfidenceBucket → serialised by .value (e.g. "supported")
    - SpanRef → nested dict; None → None
    """
    return {
        "statement": idea.statement,
        "source_ref": idea.source_ref,
        "span": _span_to_dict(idea.span) if idea.span is not None else None,
        "source_tier": idea.source_tier.name,
        "access_level": idea.access_level,
        "confidence": idea.confidence.value,
        "generativity": idea.generativity,
        "contradicts": list(idea.contradicts),
        "defeaters": list(idea.defeaters),
        "rationale": idea.rationale,
    }


def from_dict(d: dict[str, Any]) -> ScoredIdea:
    """
    Deserialise a ScoredIdea from a plain dict. Exact inverse of to_dict;
    round-trips without loss.
    """
    raw_span = d.get("span")
    span = _span_from_dict(raw_span) if raw_span is not None else None

    return ScoredIdea(
        statement=d["statement"],
        source_ref=d["source_ref"],
        span=span,
        source_tier=SourceTier[d["source_tier"]],
        access_level=d["access_level"],
        confidence=ConfidenceBucket(d["confidence"]),
        generativity=d["generativity"],
        contradicts=list(d.get("contradicts", [])),
        defeaters=list(d.get("defeaters", [])),
        rationale=d.get("rationale", ""),
    )


# ---------------------------------------------------------------------------
# Three-orderings contract
# ---------------------------------------------------------------------------

def generativity_input(idea: ScoredIdea) -> dict[str, Any]:
    """
    The ONLY fields a generativity scorer is allowed to see.

    Three-orderings rule: this dict MUST NOT contain 'confidence'.
    Generativity is scored independently of confidence — they are separate
    orderings on the same idea.

    Includes: statement, source_tier (by name), access_level, span_text.
    """
    return {
        "statement": idea.statement,
        "source_tier": idea.source_tier.name,
        "access_level": idea.access_level,
        "span_text": idea.span.text if idea.span is not None else None,
    }
