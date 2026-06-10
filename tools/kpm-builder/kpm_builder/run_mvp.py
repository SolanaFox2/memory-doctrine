"""kpm_builder.run_mvp — LIVE demo of the end-to-end MVP pipeline.

Runs the same flow as the integration test but with a REAL DeepSeek grounder.
Requires DEEPSEEK_API_KEY in the environment.

Usage
-----
    DEEPSEEK_API_KEY=sk-... python3 -m kpm_builder.run_mvp [--out /tmp/kpm-out]

The script prints the BuildOutcome and the coverage table, then exits with
0 (is_kpm=True) or 1 (is_kpm=False / research_log_only).
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="run_mvp",
        description="Live MVP demo — requires DEEPSEEK_API_KEY.",
    )
    parser.add_argument(
        "--out",
        default="/tmp/kpm-mvp-out",
        help="Output directory for the assembled KPM package (default: /tmp/kpm-mvp-out).",
    )
    args = parser.parse_args()

    # ── real provider ──────────────────────────────────────────────────────────
    from kpm_builder.providers import Family, make_provider

    complete_json = make_provider(Family.DEEPSEEK)

    # ── fixture: ONE core question, ONE manual beat, TWO sources ──────────────
    from kpm_builder.gate import ScopeContract, Source
    from kpm_builder.orchestrate import build_mvp

    contract = ScopeContract(
        goal="Understand the evidence for health interventions.",
        in_scope="RCTs, clinical trials, supplement studies in peer-reviewed venues",
        out_of_scope="Opinion pieces, anecdotal reports, unrelated topics",
    )

    # Source A — an arxiv preprint (high quality)
    source_a = Source(
        url="https://arxiv.org/abs/1234.5678",
        text=(
            "In a randomised controlled trial of 120 adult participants, "
            "intervention group A showed a statistically significant 23% reduction "
            "in systolic blood pressure compared with the control group (p<0.01)."
        ),
        venue="arxiv.org",
    )

    # Source B — a blog post (lower quality, thin pilot data)
    source_b = Source(
        url="https://example-blog.com/post",
        text=(
            "Preliminary observations from our small cohort (n=12) suggest that "
            "the supplement may have some effect on cholesterol markers in sedentary adults."
        ),
        venue="medium.com blog",
    )

    # claim_A matches source_A precisely (should entail).
    claim_a = (
        "A randomised controlled trial showed a 23% reduction in systolic blood "
        "pressure in the intervention group versus control (p<0.01)."
    )

    # claim_B over-generalises source_B (should over_claims).
    claim_b = (
        "The supplement universally reduces cholesterol in all adults who take it."
    )

    run_date = datetime.date.today().isoformat()
    fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    out_dir = Path(args.out)

    print(f"\nkpm_builder MVP — live run (DeepSeek grounder)")
    print(f"  output_dir : {out_dir}")
    print(f"  run_date   : {run_date}")
    print()

    outcome = build_mvp(
        contract=contract,
        beat_question="What does the evidence say about health interventions?",
        sources=[source_a, source_b],
        claims=[claim_a, claim_b],
        complete_json=complete_json,
        out_dir=out_dir,
        fetched_at=fetched_at,
        run_date=run_date,
    )

    # ── print BuildOutcome ─────────────────────────────────────────────────────
    print("=== BuildOutcome ===")
    print(f"  is_kpm  : {outcome.is_kpm}")
    print(f"  label   : {outcome.label}")
    print()

    # ── print coverage table ───────────────────────────────────────────────────
    print("=== Coverage Report ===")
    print(f"  termination_reason : {outcome.report.termination_reason.value}")
    print()
    print(f"  {'Question':<55} {'State':<15} {'Bucket'}")
    print(f"  {'-'*55} {'-'*15} {'-'*10}")
    for row in outcome.report.rows:
        bucket_str = row.confidence_bucket.value if row.confidence_bucket else "-"
        print(f"  {row.core_question:<55} {row.state.value:<15} {bucket_str}")

    print()
    print(f"  answered  : {outcome.report.answered_fraction:.0%}")
    print(f"  abstained : {outcome.report.abstained_fraction:.0%}")
    print()

    # ── run validate ──────────────────────────────────────────────────────────
    from package_research.validate import validate

    vresult = validate(out_dir)
    lint_status = "OK" if vresult.lint_ok else "FAILED"
    print(f"  doctrine lint : {lint_status} ({len(vresult.lint_violations)} violations)")
    if not vresult.lint_ok:
        for v in vresult.lint_violations:
            print(f"    - {v}")

    return 0 if outcome.is_kpm else 1


if __name__ == "__main__":
    sys.exit(main())
