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
from typing import Any, Dict, List

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
from kpm_builder.schema import ConfidenceBucket, ScoredIdea, SourceTier
from kpm_builder.snapshot import SpanRef, snapshot
from kpm_builder.strip import strip

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
        List of beat dicts (see module docstring for shape).
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
    """
    out_dir = Path(out_dir)

    coverage_rows: List[CoverageRow] = []
    internal_ideas: List[ScoredIdea] = []

    for beat in beats:
        question = beat["question"]
        claims = beat.get("claims", [])

        # Build per-claim pipeline (NO LLM — verdicts are inputs).
        grounded_claims = []       # ground_verdict == "entails"
        n_quality_sources = 0      # count of claims that passed (any verdict except reject)
        claim_buckets: List[ConfidenceBucket] = []

        for claim_dict in claims:
            statement = claim_dict["statement"]
            src_dict = claim_dict["source"]
            ground_verdict = claim_dict["ground_verdict"]
            n_corroborations = claim_dict.get("n_corroborations", 1)
            survived_refuter = claim_dict.get("survived_refuter", True)
            generativity = claim_dict.get("generativity", 3)

            source = Source(
                url=src_dict["url"],
                text=src_dict["text"],
                venue=src_dict.get("venue", ""),
            )

            # Snapshot — fetcher is just lambda u: source.text (text is already fetched).
            src_text = source.text
            snap = snapshot(
                source.url,
                fetcher=lambda u, t=src_text: t,
                fetched_at=fetched_at,
            )

            tier = classify_tier(source)

            bucket = confidence(
                tier=tier,
                n_independent_corroborations=n_corroborations,
                ground_verdict=ground_verdict,
                has_unresolved_contradiction=False,
            )

            claim_buckets.append(bucket)

            # Count quality sources: all non-reject verdicts are "kept"
            if ground_verdict != "reject":
                n_quality_sources += 1

            if ground_verdict == "entails":
                grounded_claims.append({
                    "statement": statement,
                    "source": source,
                    "snap": snap,
                    "tier": tier,
                    "bucket": bucket,
                    "survived_refuter": survived_refuter,
                    "generativity": generativity,
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
        for c in grounded_claims:
            snap = c["snap"]
            span = SpanRef(
                sha256=snap.sha256,
                start=0,
                end=len(snap.text),
                text=snap.text,
            )
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

    data = json.loads(raw)
    contract = data["contract"]
    beats = data["beats"]
    out_dir = Path(args.out)

    outcome = build_from_research(
        contract,
        beats,
        out_dir=out_dir,
        run_date=args.run_date,
        fetched_at=args.fetched_at,
    )

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
