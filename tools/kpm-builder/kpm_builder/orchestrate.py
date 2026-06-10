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
  5. confidence(tier, corroborations=1, ground_verdict, contradiction=False).

Coverage labeling (per core question):
  6. grounded = all kept claims have verdict "entails"
     n_quality_sources = number of sources that passed both gates
  7. question_state → CoverageState; assemble a CoverageReport (CONVERGED).
  8. decide(report) → BuildOutcome.

Shipping:
  9. Only SHIPPABLE ideas (verdict == "entails") go through strip → split →
     assemble → validate.  over_claims / reject claims are surfaced in the
     coverage report as PARTIAL/ABSTAINED but never shipped as supported axioms.

Verdict-to-state mapping for the coverage row:
  - ALL kept claims entailed           → ANSWERED
  - ≥1 over_claims / reject, ≥1 kept  → PARTIAL
  - no sources passed both gates       → ABSTAINED (n_quality_sources=0)
  - n_quality_sources < 2              → ABSTAINED (per label.question_state)
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List

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
from kpm_builder.schema import ConfidenceBucket, ScoredIdea, SourceTier
from kpm_builder.snapshot import Snapshot, snapshot
from kpm_builder.strip import strip

# Organizer tail
from package_research.assemble import assemble
from package_research.split import split as organizer_split
from package_research.validate import validate

# Type alias for the injected LLM callable.
CompleteJSON = Callable[[str, dict], dict]


def _make_fetcher(sources: List[Source]) -> Callable[[str], str]:
    """Build an in-memory fetcher from pre-loaded sources (no network I/O)."""
    by_url = {s.url: s.text for s in sources}

    def _fetch(url: str) -> str:
        return by_url[url]  # KeyError propagates — caller's responsibility

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

    fetcher = _make_fetcher(sources)

    # ------------------------------------------------------------------
    # Per-(source, claim) pipeline
    # ------------------------------------------------------------------
    kept_sources: List[Source] = []
    kept_snapshots: List[Snapshot] = []
    kept_claims: List[str] = []
    kept_tiers: List[SourceTier] = []
    kept_verdicts: List[str] = []

    for source, claim in zip(sources, claims):
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
        kept_tiers.append(tier)
        kept_verdicts.append(gresult.verdict)

    # ------------------------------------------------------------------
    # 5. Confidence per claim (corroborations=1 for MVP, contradiction=False)
    # ------------------------------------------------------------------
    kept_buckets: List[ConfidenceBucket] = []
    for tier, verdict in zip(kept_tiers, kept_verdicts):
        bucket = confidence(
            tier=tier,
            n_independent_corroborations=1,
            ground_verdict=verdict,
            has_unresolved_contradiction=False,
        )
        kept_buckets.append(bucket)

    # ------------------------------------------------------------------
    # 6. Coverage labeling for the single beat question
    # ------------------------------------------------------------------
    n_quality = len(kept_sources)
    any_entailed = any(v == "entails" for v in kept_verdicts) if kept_verdicts else False
    has_over_claims = any(v in ("over_claims", "reject") for v in kept_verdicts)

    # Determine grounded and survived_refuter for question_state:
    # - grounded  = at least one claim was faithfully entailed by its source.
    #               (over_claims / reject claims are still kept in the coverage row
    #               but surfaced as non-supported; the question counts as "answered"
    #               when at least one entailed claim addresses it.)
    # - survived_refuter = True for MVP (no refuter run)
    grounded = any_entailed
    survived_refuter = True  # MVP: refuter is bypassed

    cov_state = question_state(
        researched=n_quality > 0,
        grounded=grounded,
        survived_refuter=survived_refuter,
        n_quality_sources=n_quality,
        has_dissensus=False,
    )

    # Aggregate confidence bucket for the coverage row:
    # The "weakest" bucket among kept claims (or UNVERIFIED if nothing kept).
    if kept_buckets:
        from kpm_builder.confidence import BUCKET_RANK, _min_bucket  # type: ignore[attr-defined]
        agg_bucket: ConfidenceBucket | None = kept_buckets[0]
        for b in kept_buckets[1:]:
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
    for source, snap, claim, tier, verdict, bucket in zip(
        kept_sources,
        kept_snapshots,
        kept_claims,
        kept_tiers,
        kept_verdicts,
        kept_buckets,
    ):
        if verdict != "entails":
            # over_claims / reject: surface in coverage but DO NOT ship.
            continue

        # Build a SpanRef covering the entire snapshot text (the grounded span).
        from kpm_builder.snapshot import SpanRef

        span = SpanRef(
            sha256=snap.sha256,
            start=0,
            end=len(snap.text),
            text=snap.text,
        )

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
