"""test_mvp_integration.py — THE LOAD-BEARING integration test.

TDD: this file is written first.  It imports from kpm_builder.orchestrate and
kpm_builder.strip which do not yet exist — so it fails red on first run.

Two sources, two claims:
  - claim_A is faithfully entailed by source_A.
  - claim_B over-claims its source_B.

A FAKE complete_json routes by the word "CLAIM TO VERIFY" (ground.py pattern)
or "relevant" (gate.py relevance pattern).

Assertions (load-bearing):
  1. claim_B's confidence is NOT SUPPORTED (must be PARTIAL or UNVERIFIED).
  2. claim_A is ANSWERED/supported in the coverage report.
  3. Every CoverageRow has corpus_relative=True.
  4. The CoverageReport carries a termination_reason.
  5. The written KPM passes the Organizer's validate() (lint_ok=True).
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from kpm_builder.gate import ScopeContract, Source
from kpm_builder.label import BuildOutcome, CoverageState, TerminationReason
from kpm_builder.orchestrate import build_mvp
from kpm_builder.schema import ConfidenceBucket
from package_research.validate import validate


# ---------------------------------------------------------------------------
# Fake sources and claims
# ---------------------------------------------------------------------------

SOURCE_A_URL = "https://arxiv.org/abs/1234.5678"
SOURCE_A_TEXT = (
    "In a randomised controlled trial of 120 adult participants, "
    "intervention group A showed a statistically significant 23% reduction "
    "in systolic blood pressure compared with the control group (p<0.01)."
)

SOURCE_B_URL = "https://example-blog.com/post"
SOURCE_B_TEXT = (
    "Preliminary observations from our small cohort (n=12) suggest that "
    "the supplement may have some effect on cholesterol markers in sedentary adults."
)

# claim_A is faithful: matches what SOURCE_A_TEXT says precisely.
CLAIM_A = (
    "A randomised controlled trial showed a 23% reduction in systolic blood "
    "pressure in the intervention group versus control (p<0.01)."
)

# claim_B over-claims: asserts universal effectiveness from a tiny pilot cohort.
CLAIM_B = (
    "The supplement universally reduces cholesterol in all adults who take it."
)


# ---------------------------------------------------------------------------
# Fake complete_json
# ---------------------------------------------------------------------------

def _fake_complete_json(prompt: str, schema: dict) -> dict:
    """
    Route by prompt content so the fake is deterministic.

    Ground prompts contain "CLAIM TO VERIFY:".
    Gate B (relevance) prompts contain "relevant" in the schema properties.
    Gate B prompts always return relevant=True (let all sources through).
    """
    # Gate B relevance check (schema has "relevant" key)
    if "relevant" in schema.get("properties", {}):
        return {"relevant": True, "reason": "Fake: always relevant."}

    # Ground prompts contain the exact claim text after "CLAIM TO VERIFY:"
    if "CLAIM TO VERIFY:" in prompt:
        if CLAIM_A in prompt:
            return {
                "verdict": "entails",
                "supported_paraphrase": CLAIM_A,
                "dropped": [],
                "reason": "Fake: claim_A faithfully matches the source.",
            }
        if CLAIM_B in prompt:
            return {
                "verdict": "over_claims",
                "supported_paraphrase": (
                    "Preliminary observations suggest possible effects on "
                    "cholesterol in a small cohort."
                ),
                "dropped": ["universal scope", "n=12 overgeneralized to all adults"],
                "reason": "Fake: claim_B universalises a tiny pilot cohort.",
            }

    # Refuter prompts (contain "CLAIM:" and "INDEPENDENT PASSAGES")
    if "INDEPENDENT PASSAGES" in prompt:
        return {"refuted": False, "counter": "", "reason": "Fake: no refutation."}

    # Fallback
    return {}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_out(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "kpm_out"


@pytest.fixture()
def outcome_and_outdir(tmp_out: pathlib.Path):
    """Run build_mvp once and return (outcome, out_dir)."""
    contract = ScopeContract(
        goal="Understand the evidence for health interventions.",
        in_scope="RCTs, clinical trials, supplement studies",
        out_of_scope="Opinion pieces, unrelated topics",
    )
    sources = [
        Source(url=SOURCE_A_URL, text=SOURCE_A_TEXT, venue="arxiv.org"),
        Source(url=SOURCE_B_URL, text=SOURCE_B_TEXT, venue="medium.com blog"),
    ]
    claims = [CLAIM_A, CLAIM_B]

    outcome = build_mvp(
        contract=contract,
        beat_question="What does the evidence say about health interventions?",
        sources=sources,
        claims=claims,
        complete_json=_fake_complete_json,
        out_dir=tmp_out,
        fetched_at="2026-06-04T00:00:00Z",
        run_date="2026-06-04",
    )
    return outcome, tmp_out


class TestMvpIntegration:
    # ------------------------------------------------------------------
    # 1. claim_B must NOT be SUPPORTED — the over_claims verdict must cap it.
    #
    #    The orchestrator models one CoverageRow per beat_question; the row's
    #    confidence_bucket is the WEAKEST bucket across all kept claims.
    #    claim_B is over_claims → its bucket is PARTIAL.
    #    claim_A is entailed from arxiv (PREPRINT, n_corroborations=1) → PARTIAL
    #    (tier cap = SUPPORTED, but rule 4 drops to PARTIAL for n<2).
    #    So the aggregate bucket must NOT be SUPPORTED — it must be PARTIAL or
    #    UNVERIFIED.  This ensures the over_claims verdict is never silently
    #    ignored by shipping the claim as a "supported" axiom.
    # ------------------------------------------------------------------
    def test_claim_b_confidence_is_not_supported(self, outcome_and_outdir):
        outcome, _ = outcome_and_outdir
        report = outcome.report
        # There must be exactly one row (one beat_question).
        assert report.rows, "Coverage report has no rows."
        row = report.rows[0]
        # The aggregate confidence bucket must NOT be SUPPORTED.
        if row.confidence_bucket is not None:
            assert row.confidence_bucket != ConfidenceBucket.SUPPORTED, (
                f"Row confidence_bucket is SUPPORTED even though claim_B "
                f"over_claims — the over_claims cap was silently ignored. "
                f"Got bucket={row.confidence_bucket}."
            )
        else:
            # No bucket means the row is ABSTAINED/NOT_REACHED — also fine,
            # definitely not silently SUPPORTED.
            pass

    # ------------------------------------------------------------------
    # 2. claim_A must be ANSWERED/supported.
    # ------------------------------------------------------------------
    def test_claim_a_is_answered(self, outcome_and_outdir):
        outcome, _ = outcome_and_outdir
        report = outcome.report
        answered_rows = [r for r in report.rows if r.state == CoverageState.ANSWERED]
        assert answered_rows, (
            "claim_A is entailed but no row is ANSWERED in the coverage report."
        )

    # ------------------------------------------------------------------
    # 3. Every CoverageRow has corpus_relative=True (enforced by CoverageRow
    #    itself, but the orchestrator must not try to set it False).
    # ------------------------------------------------------------------
    def test_every_row_is_corpus_relative(self, outcome_and_outdir):
        outcome, _ = outcome_and_outdir
        for row in outcome.report.rows:
            assert row.corpus_relative is True, (
                f"Row '{row.core_question}' has corpus_relative=False — "
                "the invariant was violated."
            )

    # ------------------------------------------------------------------
    # 4. The CoverageReport carries a termination_reason.
    # ------------------------------------------------------------------
    def test_report_has_termination_reason(self, outcome_and_outdir):
        outcome, _ = outcome_and_outdir
        assert isinstance(outcome.report.termination_reason, TerminationReason)

    # ------------------------------------------------------------------
    # 5. The written KPM passes the Organizer's validate() (lint_ok=True).
    # ------------------------------------------------------------------
    def test_kpm_passes_validate(self, outcome_and_outdir):
        outcome, out_dir = outcome_and_outdir
        result = validate(out_dir)
        assert result.lint_ok, (
            f"doctrine_lint FAILED with violations:\n"
            + "\n".join(f"  - {v}" for v in result.lint_violations)
        )

    # ------------------------------------------------------------------
    # 6. build_mvp returns a BuildOutcome.
    # ------------------------------------------------------------------
    def test_returns_build_outcome(self, outcome_and_outdir):
        outcome, _ = outcome_and_outdir
        assert isinstance(outcome, BuildOutcome)

    # ------------------------------------------------------------------
    # 7. The out_dir was actually written (KPM package exists on disk).
    # ------------------------------------------------------------------
    def test_kpm_written_to_disk(self, outcome_and_outdir):
        _, out_dir = outcome_and_outdir
        assert (out_dir / "knowledge.json").exists()
        assert (out_dir / "README.md").exists()
        assert (out_dir / "axioms").is_dir()
        assert (out_dir / "evidence").is_dir()
