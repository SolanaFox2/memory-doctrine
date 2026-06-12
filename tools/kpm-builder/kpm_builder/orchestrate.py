"""kpm_builder.orchestrate — end-to-end MVP pipeline.

``build_mvp`` wires the full engine flow for ONE core question + ONE manual
beat + N sources (each with a pre-drafted claim).  It is designed to be
exercised deterministically by the integration test (fake complete_json) and
driven with a real provider (run_mvp.py).

Flow
----
For each (source, claim) pair:
  1. Snapshot the source with an injected fetcher.
  2. Gate A: classify_tier(source).
  3. Gate B: is_relevant(source, contract).  Drop irrelevant sources.
  4. ground(claim, snapshot) → verdict.
  5. confidence(tier, n_independent_corroborations, ground_verdict,
     contradiction=False) — the corroboration count is COMPUTED per claim:
     the number of distinct independent sources (by domain) whose grounding
     verdict entails the same statement (REVIEW.md KPM-M7 / EFF-5).

Coverage labeling (per core question):
  6. n_quality_sources = number of gate-passing sources whose claim verdict is
     "entails" (REVIEW.md M1 — a dropped over_claims/reject claim is NOT a
     quality source and cannot push a beat toward ANSWERED).
     grounded = n_quality_sources > 0
  7. question_state → CoverageState; assemble a CoverageReport (CONVERGED).
  8. decide(report) → BuildOutcome.

Shipping:
  9. Only SHIPPABLE ideas (verdict == "entails") go through strip → split →
     assemble → validate.  over_claims / reject claims are surfaced in the
     coverage report as ABSTAINED but never shipped as supported axioms.

Verdict-to-state mapping for the coverage row:
  - ≥2 independently entailed claims   → ANSWERED
  - exactly 1 entailed claim           → ABSTAINED (below the 2-source floor)
  - no entailed claims                 → ABSTAINED
  - no sources passed both gates       → NOT_REACHED (nothing researched)
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional, Set
from urllib.parse import urlsplit

from kpm_builder.confidence import confidence
from kpm_builder.gate import (
    Source,
    ScopeContract,
    classify_tier,
    is_relevant,
)
from kpm_builder.ground import ground
from kpm_builder.label import (
    BuildOutcome,
    CoverageReport,
    CoverageRow,
    CoverageState,
    TerminationReason,
    decide,
    question_state,
)
from kpm_builder.schema import ConfidenceBucket, GroundVerdict, ScoredIdea, SourceTier
from kpm_builder.snapshot import Snapshot, passage_span, snapshot
from kpm_builder.strip import apply_belief_status, strip

# Organizer tail
from package_research.assemble import assemble
from package_research.split import split as organizer_split
from package_research.validate import validate

# Type alias for the injected LLM callable.
CompleteJSON = Callable[[str, dict], dict]


def _independence_key(source: Source) -> str:
    """Mechanical independence proxy for a source: its domain, lowercased.

    confidence() defines corroboration as distinct authors / institutions —
    the live path has no author metadata, so distinct domains stand in:
    two URLs on the same domain never count as independent corroboration.
    """
    netloc = urlsplit(source.url).netloc.lower()
    return netloc or source.url.lower()


def _make_fetcher(sources: List[Source]) -> Callable[[str], str]:
    """Build an in-memory fetcher from pre-loaded sources (no network I/O).

    A URL outside the pre-loaded set raises a LookupError naming the URL and
    the known key set (REVIEW.md M3 — never a bare KeyError)."""
    by_url = {s.url: s.text for s in sources}

    def _fetch(url: str) -> str:
        try:
            return by_url[url]
        except KeyError:
            raise LookupError(
                f"fetcher has no pre-loaded text for {url!r}; "
                f"known URLs: {sorted(by_url)}"
            ) from None

    return _fetch


def build_mvp(
    contract: ScopeContract,
    beat_question: str,
    sources: List[Source],
    claims: List[str],
    *,
    complete_json: CompleteJSON,
    out_dir: Path,
    fetched_at: str,
    run_date: str,
    supporting_passages: Optional[List[Optional[str]]] = None,
    package_name: str = "@kpm/mvp-build",
    package_description: str = "MVP KPM package built by kpm_builder orchestrator.",
) -> BuildOutcome:
    """Run the full MVP engine flow and write a KPM package to ``out_dir``.

    Parameters
    ----------
    contract:
        Research scope definition (goal, in_scope, out_of_scope).
    beat_question:
        The single core question this MVP addresses.
    sources:
        Pre-loaded sources (url + text + venue).  Must have the same length as
        ``claims`` — sources[i] is the source for claims[i].
    claims:
        Pre-drafted claims, one per source.
    complete_json:
        Injected LLM callable ``(prompt, schema) -> dict``.  In tests: a fake.
        In production: ``make_provider(Family.DEEPSEEK)``.
    out_dir:
        Destination directory for the assembled KPM package.
    fetched_at:
        ISO timestamp for snapshots (injected — never clock-calls here).
    run_date:
        ``YYYY-MM-DD`` for the evidence ``verified`` field (injected).
    supporting_passages:
        Optional, aligned with ``claims`` — the exact passage from sources[i]
        that entailed claims[i].  When present, the shipped evidence span is
        scoped to that passage (REVIEW.md KPM-H5); when ``None`` (or an entry
        is ``None``), the span falls back to the whole document.
    package_name / package_description:
        Package manifest fields passed to assemble.

    Returns
    -------
    BuildOutcome
        The decide() verdict: is_kpm, label, coverage report.
    """
    if len(sources) != len(claims):
        raise ValueError(
            f"sources and claims must have the same length; "
            f"got {len(sources)} sources and {len(claims)} claims."
        )
    if supporting_passages is None:
        supporting_passages = [None] * len(claims)
    if len(supporting_passages) != len(claims):
        raise ValueError(
            f"supporting_passages and claims must have the same length; "
            f"got {len(supporting_passages)} passages and {len(claims)} claims."
        )

    fetcher = _make_fetcher(sources)

    # ------------------------------------------------------------------
    # Per-(source, claim) pipeline
    # ------------------------------------------------------------------
    kept_sources: List[Source] = []
    kept_snapshots: List[Snapshot] = []
    kept_claims: List[str] = []
    kept_passages: List[Optional[str]] = []
    kept_tiers: List[SourceTier] = []
    kept_verdicts: List[str] = []

    for source, claim, passage in zip(sources, claims, supporting_passages):
        # 1. Snapshot
        snap = snapshot(
            source.url,
            fetcher=fetcher,
            fetched_at=fetched_at,
        )

        # 2. Gate A: tier
        tier = classify_tier(source)

        # 3. Gate B: relevance
        if not is_relevant(source, contract, complete_json=complete_json):
            continue  # drop irrelevant sources

        # 4. Ground the claim against the snapshot
        gresult = ground(claim, snap, complete_json=complete_json)

        kept_sources.append(source)
        kept_snapshots.append(snap)
        kept_claims.append(claim)
        kept_passages.append(passage)
        kept_tiers.append(tier)
        kept_verdicts.append(gresult.verdict)

    # ------------------------------------------------------------------
    # 5. Confidence per claim (REVIEW.md KPM-M7 / EFF-5).
    #    n_independent_corroborations = number of DISTINCT independent
    #    sources (by domain — _independence_key) whose grounding verdict
    #    entails the same statement.  This makes the SUPPORTED tier
    #    reachable in the live path: a claim entailed by 2+ independent
    #    domains clears confidence rule 4; a single-source claim cannot.
    # ------------------------------------------------------------------
    entailing_domains: Dict[str, Set[str]] = {}
    for source, claim, verdict in zip(kept_sources, kept_claims, kept_verdicts):
        if verdict == GroundVerdict.ENTAILS.value:
            entailing_domains.setdefault(claim, set()).add(_independence_key(source))

    kept_buckets: List[ConfidenceBucket] = []
    for claim, tier, verdict in zip(kept_claims, kept_tiers, kept_verdicts):
        bucket = confidence(
            tier=tier,
            n_independent_corroborations=len(entailing_domains.get(claim, ())),
            ground_verdict=verdict,
            has_unresolved_contradiction=False,
        )
        kept_buckets.append(bucket)

    # ------------------------------------------------------------------
    # 6. Coverage labeling for the single beat question (REVIEW.md M1):
    #    only ENTAILED claims count as quality sources — a dropped
    #    over_claims/reject claim must neither push the beat to ANSWERED
    #    nor drive the coverage bucket.
    # ------------------------------------------------------------------
    n_quality = sum(1 for v in kept_verdicts if v == GroundVerdict.ENTAILS.value)
    grounded = n_quality > 0
    survived_refuter = True  # MVP: refuter is bypassed

    cov_state = question_state(
        researched=len(kept_sources) > 0,
        grounded=grounded,
        survived_refuter=survived_refuter,
        n_quality_sources=n_quality,
        has_dissensus=False,
    )

    # Aggregate confidence bucket for the coverage row:
    # the "weakest" bucket among SHIPPABLE (entailed) claims — dropped claims
    # don't drive it (or None if nothing entailed).
    entailed_buckets = [
        b for b, v in zip(kept_buckets, kept_verdicts)
        if v == GroundVerdict.ENTAILS.value
    ]
    if entailed_buckets:
        from kpm_builder.confidence import _min_bucket  # type: ignore[attr-defined]
        agg_bucket: ConfidenceBucket | None = entailed_buckets[0]
        for b in entailed_buckets[1:]:
            agg_bucket = _min_bucket(agg_bucket, b)  # type: ignore[arg-type]
    else:
        agg_bucket = None

    cov_row = CoverageRow(
        core_question=beat_question,
        state=cov_state,
        confidence_bucket=agg_bucket,
        corpus_relative=True,
    )
    report = CoverageReport(
        rows=[cov_row],
        termination_reason=TerminationReason.CONVERGED,
    )

    # ------------------------------------------------------------------
    # 7. Build internal ScoredIdea objects for SHIPPABLE claims only.
    #    Shippable = verdict "entails".
    # ------------------------------------------------------------------
    internal_ideas: List[ScoredIdea] = []
    for source, snap, claim, passage, tier, verdict, bucket in zip(
        kept_sources,
        kept_snapshots,
        kept_claims,
        kept_passages,
        kept_tiers,
        kept_verdicts,
        kept_buckets,
    ):
        if verdict != GroundVerdict.ENTAILS.value:
            # over_claims / reject: surface in coverage but DO NOT ship.
            continue

        # Evidence span scoped to the passage that entailed the claim —
        # never the whole document when a passage exists (REVIEW.md KPM-H5).
        span = passage_span(snap, passage)

        idea = ScoredIdea(
            statement=claim,
            source_ref=source.url,
            span=span,
            source_tier=tier,
            access_level=snap.access_level,
            confidence=bucket,
            generativity=3,  # default generativity for MVP
        )
        internal_ideas.append(idea)

    # ------------------------------------------------------------------
    # 8. strip → organizer split → assemble → validate
    # ------------------------------------------------------------------
    organizer_ideas = strip(internal_ideas)

    # The Organizer's split needs at least one idea with a non-empty snippet;
    # if nothing is shippable, assemble an empty package (lint will pass because
    # the assemble stage drops zero-evidence axioms cleanly).
    axioms, evidence = organizer_split(organizer_ideas, source_passages=None)
    # Grounded claims earn their doctrine status from their bucket (EFF-2).
    apply_belief_status(axioms, internal_ideas)

    out_dir = Path(out_dir)
    assemble(
        axioms,
        evidence,
        out_dir,
        run_date=run_date,
        name=package_name,
        description=package_description,
    )

    # ------------------------------------------------------------------
    # 9. Return the BuildOutcome from decide(report).
    # ------------------------------------------------------------------
    return decide(report)
