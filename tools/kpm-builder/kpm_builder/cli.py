"""kpm_builder.cli — mechanical finalize: takes grounded research JSON,
produces a KPM on disk (or a research_log.json for thin results).

NO LLM is called here. Grounding verdicts are inputs.

Public API
----------
build_from_research(contract, beats, *, out_dir, run_date, fetched_at) -> BuildOutcome

CLI
---
python -m kpm_builder.cli build --input <path-or--> --out <dir> [--run-date YYYY-MM-DD] [--fetched-at ...]

Design constraints:
- No LLM, no network, no randomness.
- All grounding verdicts are INPUTS (the skill has already done the judgment).
- Assembly mirrors orchestrate.build_mvp's strip → split → assemble → validate tail.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

from kpm_builder.confidence import confidence, _min_bucket
from kpm_builder.gate import Source, classify_tier
from kpm_builder.label import (
    BuildOutcome,
    CoverageReport,
    CoverageRow,
    TerminationReason,
    decide,
    question_state,
)
from kpm_builder.schema import ConfidenceBucket, GroundVerdict, ScoredIdea, SourceTier
from kpm_builder.snapshot import passage_span, snapshot
from kpm_builder.strip import apply_belief_status, strip

# Organizer tail
from package_research.assemble import assemble
from package_research.split import split as organizer_split
from package_research.validate import validate

# ---------------------------------------------------------------------------
# Defaults (deterministic — do NOT call clock here)
# ---------------------------------------------------------------------------

_DEFAULT_FETCHED_AT = "2026-01-01T00:00:00Z"
_DEFAULT_RUN_DATE = "2026-01-01"


# ---------------------------------------------------------------------------
# Input validation (REVIEW.md M2) — a malformed beat fails up front with a
# named error instead of a bare KeyError mid-build; the echoed research log
# therefore only ever carries shape-checked input.
# ---------------------------------------------------------------------------

class ResearchInputError(ValueError):
    """The research JSON handed to build_from_research is malformed."""


class _SourceModel(BaseModel):
    url: str
    text: str
    venue: str = ""


class _ClaimModel(BaseModel):
    statement: str
    source: _SourceModel
    ground_verdict: Literal["entails", "over_claims", "reject"]
    supporting_passage: Optional[str] = None
    n_corroborations: int = 1
    survived_refuter: bool = True
    generativity: int = Field(default=3, ge=1, le=5)


class _BeatModel(BaseModel):
    question: str
    claims: List[_ClaimModel] = Field(default_factory=list)


def _validate_research_input(
    contract: Any, beats: Any
) -> List[_BeatModel]:
    """Shape-check the research input; raise ResearchInputError naming the spot."""
    if not isinstance(contract, dict):
        raise ResearchInputError(
            f"contract must be a JSON object, got {type(contract).__name__}"
        )
    if not isinstance(beats, list):
        raise ResearchInputError(
            f"beats must be a JSON array, got {type(beats).__name__}"
        )
    validated: List[_BeatModel] = []
    for i, beat in enumerate(beats):
        try:
            validated.append(_BeatModel.model_validate(beat))
        except ValidationError as exc:
            raise ResearchInputError(f"beats[{i}] is malformed: {exc}") from exc
    return validated


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def build_from_research(
    contract: Dict[str, Any],
    beats: List[Dict[str, Any]],
    *,
    out_dir: Path,
    run_date: str,
    fetched_at: str,
) -> BuildOutcome:
    """Assemble a KPM (or research log) from pre-grounded research.

    Parameters
    ----------
    contract:
        Dict with keys: ``goal``, ``in_scope``, ``out_of_scope``.
    beats:
        List of beat dicts.  Each claim dict carries ``statement``,
        ``source`` (``url``/``text``/``venue``), ``ground_verdict``, and
        optionally:

        - ``supporting_passage`` — the exact passage from ``source.text``
          that entailed the claim.  When present, the shipped evidence span
          is scoped to it (REVIEW.md KPM-H5: thin index, rich store); when
          absent, the span falls back to the whole document.
        - ``n_corroborations`` — number of distinct INDEPENDENT sources
          (distinct authors/venues, not raw URLs) that support the same
          statement, including this one.  Honored as-is (REVIEW.md KPM-M7 /
          EFF-5): ≥2 lets a top-tier entailed claim reach SUPPORTED;
          default 1 keeps single-source claims at PARTIAL.
    out_dir:
        Destination directory for the assembled package.
    run_date:
        ``YYYY-MM-DD`` for evidence ``verified`` field (injected).
    fetched_at:
        ISO timestamp for snapshots (injected).

    Returns
    -------
    BuildOutcome
        The decide() verdict: is_kpm, label, coverage report.
        If is_kpm=True  → KPM package written to out_dir.
        If is_kpm=False → research_log.json written to out_dir instead.

    Raises
    ------
    ResearchInputError
        If ``contract``/``beats`` don't match the input shape above
        (REVIEW.md M2) — validated up front, before anything is written.
    """
    out_dir = Path(out_dir)
    validated_beats = _validate_research_input(contract, beats)  # REVIEW.md M2

    coverage_rows: List[CoverageRow] = []
    internal_ideas: List[ScoredIdea] = []

    for beat in validated_beats:
        question = beat.question

        # Build per-claim pipeline (NO LLM — verdicts are inputs).
        # Only ENTAILED claims count as quality sources or feed the coverage
        # bucket (REVIEW.md M1) — a dropped over_claims/reject claim must
        # neither push a beat to ANSWERED nor drive its bucket.
        grounded_claims = []       # ground_verdict == "entails"
        n_quality_sources = 0      # entailed claims only
        claim_buckets: List[ConfidenceBucket] = []   # entailed claims only

        for claim in beat.claims:
            source = Source(
                url=claim.source.url,
                text=claim.source.text,
                venue=claim.source.venue,
            )

            # Snapshot — fetcher is just lambda u: source.text (text is already fetched).
            src_text = source.text
            snap = snapshot(
                source.url,
                fetcher=lambda u, t=src_text: t,
                fetched_at=fetched_at,
            )

            tier = classify_tier(source)

            if claim.ground_verdict != GroundVerdict.ENTAILS.value:
                continue  # surfaced via coverage state, never as a quality source

            bucket = confidence(
                tier=tier,
                n_independent_corroborations=claim.n_corroborations,
                ground_verdict=claim.ground_verdict,
                has_unresolved_contradiction=False,
            )

            n_quality_sources += 1
            claim_buckets.append(bucket)
            grounded_claims.append({
                "statement": claim.statement,
                "source": source,
                "snap": snap,
                "supporting_passage": claim.supporting_passage,
                "tier": tier,
                "bucket": bucket,
                "survived_refuter": claim.survived_refuter,
                "generativity": claim.generativity,
            })

        # Coverage state for this beat.
        grounded = len(grounded_claims) > 0
        survived_refuter_beat = (
            all(c["survived_refuter"] for c in grounded_claims)
            if grounded_claims else False
        )

        cov_state = question_state(
            researched=True,
            grounded=grounded,
            survived_refuter=survived_refuter_beat,
            n_quality_sources=n_quality_sources,
            has_dissensus=False,
        )

        # Weakest bucket across all claim buckets for this beat.
        agg_bucket: ConfidenceBucket | None = None
        if claim_buckets:
            agg_bucket = claim_buckets[0]
            for b in claim_buckets[1:]:
                agg_bucket = _min_bucket(agg_bucket, b)

        cov_row = CoverageRow(
            core_question=question,
            state=cov_state,
            confidence_bucket=agg_bucket,
            corpus_relative=True,
        )
        coverage_rows.append(cov_row)

        # Build internal ScoredIdea for SHIPPABLE (entails) claims only.
        # The span is scoped to the supporting passage when the input carried
        # one — never the whole document by default (REVIEW.md KPM-H5).
        for c in grounded_claims:
            snap = c["snap"]
            span = passage_span(snap, c["supporting_passage"])
            idea = ScoredIdea(
                statement=c["statement"],
                source_ref=c["source"].url,
                span=span,
                source_tier=c["tier"],
                access_level=snap.access_level,
                confidence=c["bucket"],
                generativity=c["generativity"],
            )
            internal_ideas.append(idea)

    report = CoverageReport(
        rows=coverage_rows,
        termination_reason=TerminationReason.CONVERGED,
    )
    outcome = decide(report)

    out_dir.mkdir(parents=True, exist_ok=True)

    if outcome.is_kpm:
        # Strip internal ideas → Organizer shape → split → assemble → validate
        organizer_ideas = strip(internal_ideas)
        axioms, evidence = organizer_split(organizer_ideas, source_passages=None)
        # Grounded claims earn their doctrine status from their bucket (EFF-2).
        apply_belief_status(axioms, internal_ideas)

        # Derive package name/description from contract.
        pkg_goal = contract.get("goal", "Knowledge Package")
        pkg_name = "@kpm/research-build"
        pkg_description = pkg_goal

        assemble(
            axioms,
            evidence,
            out_dir,
            run_date=run_date,
            name=pkg_name,
            description=pkg_description,
        )
    else:
        # Not enough coverage — write research_log.json instead of a lying KPM.
        def _coverage_row_to_dict(row: CoverageRow) -> dict:
            return {
                "core_question": row.core_question,
                "state": row.state.value,
                "confidence_bucket": row.confidence_bucket.value if row.confidence_bucket else None,
                "corpus_relative": row.corpus_relative,
            }

        research_log = {
            "contract": contract,
            "beats": beats,
            "coverage": {
                "termination_reason": report.termination_reason.value,
                "answered_fraction": report.answered_fraction,
                "rows": [_coverage_row_to_dict(r) for r in report.rows],
            },
        }
        (out_dir / "research_log.json").write_text(
            json.dumps(research_log, indent=2),
            encoding="utf-8",
        )

    return outcome


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m kpm_builder.cli",
        description="Mechanical KPM assembler — takes grounded research JSON, writes a package.",
    )
    sub = parser.add_subparsers(dest="command")

    build_cmd = sub.add_parser("build", help="Assemble a KPM from grounded research JSON.")
    build_cmd.add_argument(
        "--input", "-i",
        default="-",
        help="Path to input JSON file, or '-' for stdin (default: stdin).",
    )
    build_cmd.add_argument(
        "--out", "-o",
        required=True,
        help="Output directory for the assembled KPM package.",
    )
    build_cmd.add_argument(
        "--run-date",
        default=_DEFAULT_RUN_DATE,
        help=f"YYYY-MM-DD for evidence verified field (default: {_DEFAULT_RUN_DATE}).",
    )
    build_cmd.add_argument(
        "--fetched-at",
        default=_DEFAULT_FETCHED_AT,
        help=f"ISO timestamp for snapshots (default: {_DEFAULT_FETCHED_AT}).",
    )

    args = parser.parse_args()

    if args.command != "build":
        parser.print_help()
        sys.exit(1)

    # Read input JSON
    if args.input == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.input).read_text(encoding="utf-8")

    out_dir = Path(args.out)

    try:
        data = json.loads(raw)
        if not isinstance(data, dict) or "contract" not in data or "beats" not in data:
            raise ResearchInputError(
                'input must be a JSON object with "contract" and "beats" keys'
            )
        outcome = build_from_research(
            data["contract"],
            data["beats"],
            out_dir=out_dir,
            run_date=args.run_date,
            fetched_at=args.fetched_at,
        )
    except (ResearchInputError, json.JSONDecodeError) as exc:
        print(f"error: build: {exc}", file=sys.stderr)
        sys.exit(1)

    # Print results
    print(f"\nOutcome: {outcome.label} (is_kpm={outcome.is_kpm})")
    print(f"Output:  {out_dir}")
    print()
    print("Coverage:")
    print(f"  {'Question':<60}  {'State':<15}  {'Bucket'}")
    print(f"  {'-'*60}  {'-'*15}  {'-'*12}")
    for row in outcome.report.rows:
        q = row.core_question[:58] + ".." if len(row.core_question) > 60 else row.core_question
        bucket_str = row.confidence_bucket.value if row.confidence_bucket else "n/a"
        print(f"  {q:<60}  {row.state.value:<15}  {bucket_str}")
    print()
    if outcome.is_kpm:
        print(f"KPM package written to: {out_dir}/")
    else:
        print(f"Research log written to: {out_dir}/research_log.json")


if __name__ == "__main__":
    main()
