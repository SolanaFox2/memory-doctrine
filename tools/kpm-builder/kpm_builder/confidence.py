"""
kpm_builder.confidence
-----------------------
Pure, deterministic confidence rubric.

Given auditable inputs (source tier, corroboration count, ground verdict,
contradiction flag) it returns a ConfidenceBucket ordinal.  No LLM, no I/O,
no randomness — stdlib only.

Rule execution order (later rules see the updated bucket):
  1. ground gate  : "reject" → UNVERIFIED immediately (returns early).
  2. tier cap     : bucket = TIER_CAP[tier].
  3. over_claims  : bucket = min(bucket, PARTIAL).
  4. corroboration: if bucket is SUPPORTED and n < 2, drop to PARTIAL.
  5. contradiction: downgrade one step.
"""
from __future__ import annotations

from kpm_builder.schema import ConfidenceBucket, SourceTier

# ---------------------------------------------------------------------------
# Ordering helpers (exposed so tests can assert the contract)
# ---------------------------------------------------------------------------

#: Numeric rank; higher = better bucket.
BUCKET_RANK: dict[ConfidenceBucket, int] = {
    ConfidenceBucket.SUPPORTED:   2,
    ConfidenceBucket.PARTIAL:     1,
    ConfidenceBucket.UNVERIFIED:  0,
}

_RANK_TO_BUCKET: dict[int, ConfidenceBucket] = {v: k for k, v in BUCKET_RANK.items()}


def _min_bucket(a: ConfidenceBucket, b: ConfidenceBucket) -> ConfidenceBucket:
    """Return the weaker (lower-ranked) of two buckets."""
    return _RANK_TO_BUCKET[min(BUCKET_RANK[a], BUCKET_RANK[b])]


def _downgrade(b: ConfidenceBucket) -> ConfidenceBucket:
    """Drop one step; UNVERIFIED is the floor."""
    new_rank = max(BUCKET_RANK[b] - 1, 0)
    return _RANK_TO_BUCKET[new_rank]


# ---------------------------------------------------------------------------
# Tier cap table (exposed as a module constant so tests can assert each entry)
# ---------------------------------------------------------------------------

S = ConfidenceBucket.SUPPORTED
P = ConfidenceBucket.PARTIAL
U = ConfidenceBucket.UNVERIFIED

#: Best possible bucket for each source tier.
TIER_CAP: dict[SourceTier, ConfidenceBucket] = {
    SourceTier.PEER_REVIEWED:   S,
    SourceTier.PREPRINT:        S,
    SourceTier.OFFICIAL_DOCS:   S,
    SourceTier.REPUTABLE_PRESS: P,
    SourceTier.BLOG:            P,
    SourceTier.UNKNOWN:         U,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def confidence(
    *,
    tier: SourceTier,
    n_independent_corroborations: int,
    ground_verdict: str,   # "entails" | "over_claims" | "reject"
    has_unresolved_contradiction: bool,
) -> ConfidenceBucket:
    """
    Compute an ordinal ConfidenceBucket from auditable, LLM-free inputs.

    Parameters
    ----------
    tier : SourceTier
        Quality tier of the primary source.
    n_independent_corroborations : int
        Number of *distinct* authors / institutions / funding sources that
        independently support the claim (not raw URL count).
    ground_verdict : str
        Outcome of the grounding check: "entails", "over_claims", or "reject".
    has_unresolved_contradiction : bool
        True if at least one open contradiction remains unresolved.

    Returns
    -------
    ConfidenceBucket
        SUPPORTED | PARTIAL | UNVERIFIED
    """
    # --- Rule 1: ground gate ---
    if ground_verdict == "reject":
        return U

    # --- Rule 2: tier cap ---
    bucket: ConfidenceBucket = TIER_CAP[tier]

    # --- Rule 3: over_claims cap ---
    if ground_verdict == "over_claims":
        bucket = _min_bucket(bucket, P)

    # --- Rule 4: corroboration threshold ---
    if bucket is S and n_independent_corroborations < 2:
        bucket = P

    # --- Rule 5: unresolved contradiction ---
    if has_unresolved_contradiction:
        bucket = _downgrade(bucket)

    return bucket
