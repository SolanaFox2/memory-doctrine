"""kpm_builder.strip — map internal ScoredIdea to the Organizer tail's shape.

Internal ``kpm_builder.schema.ScoredIdea`` carries provenance + adversarial
state that is INTERNAL ONLY and must never reach the public output:
  - span (SpanRef): internal content-addressed reference
  - source_tier (SourceTier): internal quality classification
  - access_level: internal access metadata
  - contradicts / defeaters: internal adversarial state

``strip()`` produces a list of ``package_research.score.ScoredIdea`` objects
— the type that the Organizer's split → assemble → validate tail consumes.

Confidence bucket → float mapping (doctrine-grounded):
  SUPPORTED   → 0.9
  PARTIAL     → 0.5
  UNVERIFIED  → 0.2
"""

from __future__ import annotations

from typing import List

from kpm_builder.schema import ConfidenceBucket
from kpm_builder.schema import ScoredIdea as InternalScoredIdea

# The Organizer's ScoredIdea (the public tail's type).
from package_research.score import ScoredIdea as OrganizerScoredIdea

# ── confidence bucket → float mapping ─────────────────────────────────────────

BUCKET_TO_FLOAT: dict[ConfidenceBucket, float] = {
    ConfidenceBucket.SUPPORTED:  0.9,
    ConfidenceBucket.PARTIAL:    0.5,
    ConfidenceBucket.UNVERIFIED: 0.2,
}


def strip(ideas: List[InternalScoredIdea]) -> List[OrganizerScoredIdea]:
    """Map a list of internal ScoredIdea to the Organizer tail's ScoredIdea.

    Internal-only fields (span, source_tier, access_level, contradicts,
    defeaters) are dropped.  The supporting snippet is recovered from
    ``span.text`` when present (otherwise empty list).

    Parameters
    ----------
    ideas:
        Internal ideas — all must be "shippable" (callers filter to only
        entailed / acceptable claims before calling strip).

    Returns
    -------
    List[OrganizerScoredIdea]
        Ready for ``split → assemble → validate``.
    """
    result: List[OrganizerScoredIdea] = []
    for idea in ideas:
        confidence_float = BUCKET_TO_FLOAT.get(idea.confidence, 0.2)

        # Recover the verbatim snippet from the span when available.
        snippets: List[str] = []
        if idea.span is not None and idea.span.text:
            snippets = [idea.span.text]

        # The source reference becomes both the source-file list and the key
        # the Organizer uses to de-duplicate evidence notes.
        source_files: List[str] = [idea.source_ref] if idea.source_ref else []

        organizer_idea = OrganizerScoredIdea(
            statement=idea.statement,
            supporting_source_files=source_files,
            supporting_snippets=snippets,
            confidence=confidence_float,
            generativity=idea.generativity,
            rationale=idea.rationale,
        )
        result.append(organizer_idea)

    return result
