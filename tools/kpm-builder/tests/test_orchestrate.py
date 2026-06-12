"""test_orchestrate.py — build_mvp behaviors fixed by REVIEW.md KPM-H5 and
KPM-M7 / EFF-5.

KPM-M7 / EFF-5 (corroboration): build_mvp used to hardcode
n_independent_corroborations=1, making SUPPORTED unreachable in the live
path.  It must now count DISTINCT independent sources (by domain) whose
grounding verdict entails the same statement:
  - a claim entailed by 2+ independent domains CAN reach SUPPORTED;
  - a single-source claim CANNOT;
  - two URLs on the SAME domain are not independent (still PARTIAL).

KPM-H5 (passage-scoping): the shipped evidence span must be the supporting
passage that entailed the claim — not the whole document — with the
whole-document fallback kept for claims without a passage.
"""

from __future__ import annotations

import pathlib

import pytest

from kpm_builder.gate import ScopeContract, Source
from kpm_builder.orchestrate import build_mvp
from kpm_builder.schema import ConfidenceBucket
from package_research.validate import validate


# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

CONTRACT = ScopeContract(
    goal="Understand the evidence for health interventions.",
    in_scope="RCTs, clinical trials, supplement studies",
    out_of_scope="Opinion pieces, unrelated topics",
)

BEAT_QUESTION = "What does the evidence say about health interventions?"

CLAIM = (
    "A randomised controlled trial showed a 23% reduction in systolic blood "
    "pressure in the intervention group versus control (p<0.01)."
)

PASSAGE = (
    "intervention group A showed a statistically significant 23% reduction "
    "in systolic blood pressure compared with the control group (p<0.01)."
)

# The marker only appears OUTSIDE the supporting passage — if it leaks into
# the shipped evidence, the span was the whole document, not the passage.
OUTSIDE_MARKER = "UNRELATED-TRAILING-SECTION"

DOC_TEXT = (
    "In a randomised controlled trial of 120 adult participants, "
    + PASSAGE
    + " "
    + OUTSIDE_MARKER
    + ": funding disclosures and acknowledgements follow."
)


def _entails_everything(prompt: str, schema: dict) -> dict:
    """Fake complete_json: every source is relevant, every claim entails."""
    if "relevant" in schema.get("properties", {}):
        return {"relevant": True, "reason": "Fake: always relevant."}
    if "CLAIM TO VERIFY:" in prompt:
        return {
            "verdict": "entails",
            "supported_paraphrase": CLAIM,
            "dropped": [],
            "reason": "Fake: entailed.",
        }
    return {}


def _build(tmp_path: pathlib.Path, sources, claims, passages=None):
    out_dir = tmp_path / "kpm_out"
    outcome = build_mvp(
        contract=CONTRACT,
        beat_question=BEAT_QUESTION,
        sources=sources,
        claims=claims,
        complete_json=_entails_everything,
        out_dir=out_dir,
        fetched_at="2026-06-12T00:00:00Z",
        run_date="2026-06-12",
        supporting_passages=passages,
    )
    return outcome, out_dir


# ---------------------------------------------------------------------------
# KPM-M7 / EFF-5 — corroboration counting in the live path
# ---------------------------------------------------------------------------

class TestCorroborationCount:
    def test_two_independent_domains_reach_supported(self, tmp_path):
        """The same claim entailed by 2 distinct domains → SUPPORTED."""
        sources = [
            Source(url="https://arxiv.org/abs/1234.5678", text=DOC_TEXT, venue="arxiv.org"),
            Source(url="https://doi.org/10.1000/trial-replication", text=DOC_TEXT, venue="journal"),
        ]
        outcome, _ = _build(tmp_path, sources, [CLAIM, CLAIM])
        row = outcome.report.rows[0]
        assert row.confidence_bucket == ConfidenceBucket.SUPPORTED, (
            f"2 independent entailing domains should reach SUPPORTED; "
            f"got {row.confidence_bucket}."
        )

    def test_single_source_claim_cannot_reach_supported(self, tmp_path):
        """One entailing source → n=1 → confidence rule 4 drops to PARTIAL."""
        sources = [
            Source(url="https://arxiv.org/abs/1234.5678", text=DOC_TEXT, venue="arxiv.org"),
        ]
        outcome, _ = _build(tmp_path, sources, [CLAIM])
        row = outcome.report.rows[0]
        assert row.confidence_bucket == ConfidenceBucket.PARTIAL, (
            f"A single-source claim must not reach SUPPORTED; "
            f"got {row.confidence_bucket}."
        )

    def test_same_domain_urls_are_not_independent(self, tmp_path):
        """Two URLs on the SAME domain count as one corroboration → PARTIAL."""
        sources = [
            Source(url="https://arxiv.org/abs/1234.5678", text=DOC_TEXT, venue="arxiv.org"),
            Source(url="https://arxiv.org/abs/9999.0001", text=DOC_TEXT, venue="arxiv.org"),
        ]
        outcome, _ = _build(tmp_path, sources, [CLAIM, CLAIM])
        row = outcome.report.rows[0]
        assert row.confidence_bucket == ConfidenceBucket.PARTIAL, (
            f"Same-domain sources are not independent corroboration; "
            f"got {row.confidence_bucket}."
        )


# ---------------------------------------------------------------------------
# KPM-H5 — passage-scoped evidence spans
# ---------------------------------------------------------------------------

class TestPassageScopedEvidence:
    def test_evidence_is_passage_not_whole_document(self, tmp_path):
        sources = [
            Source(url="https://arxiv.org/abs/1234.5678", text=DOC_TEXT, venue="arxiv.org"),
        ]
        _, out_dir = _build(tmp_path, sources, [CLAIM], passages=[PASSAGE])

        evidence_files = list((out_dir / "evidence").glob("*.md"))
        assert evidence_files, "No evidence notes written."
        body = "\n".join(f.read_text() for f in evidence_files)
        assert PASSAGE in body, "Supporting passage missing from shipped evidence."
        assert OUTSIDE_MARKER not in body, (
            "Whole-document text leaked into the evidence note — "
            "the span was not scoped to the supporting passage (KPM-H5)."
        )

    def test_no_passage_falls_back_to_whole_document(self, tmp_path):
        sources = [
            Source(url="https://arxiv.org/abs/1234.5678", text=DOC_TEXT, venue="arxiv.org"),
        ]
        _, out_dir = _build(tmp_path, sources, [CLAIM], passages=None)

        evidence_files = list((out_dir / "evidence").glob("*.md"))
        assert evidence_files, "No evidence notes written."
        body = "\n".join(f.read_text() for f in evidence_files)
        assert OUTSIDE_MARKER in body, (
            "Whole-document fallback broke: with no passage, the evidence "
            "span must still cover the full snapshot."
        )

    def test_passage_scoped_kpm_passes_validate(self, tmp_path):
        sources = [
            Source(url="https://arxiv.org/abs/1234.5678", text=DOC_TEXT, venue="arxiv.org"),
            Source(url="https://doi.org/10.1000/trial-replication", text=DOC_TEXT, venue="journal"),
        ]
        outcome, out_dir = _build(
            tmp_path, sources, [CLAIM, CLAIM], passages=[PASSAGE, PASSAGE]
        )
        assert outcome.is_kpm is True
        result = validate(out_dir)
        assert result.lint_ok, (
            "doctrine_lint FAILED:\n"
            + "\n".join(f"  - {v}" for v in result.lint_violations)
        )

    def test_mismatched_passages_length_raises(self, tmp_path):
        sources = [
            Source(url="https://arxiv.org/abs/1234.5678", text=DOC_TEXT, venue="arxiv.org"),
        ]
        with pytest.raises(ValueError, match="supporting_passages"):
            _build(tmp_path, sources, [CLAIM], passages=[PASSAGE, PASSAGE])
