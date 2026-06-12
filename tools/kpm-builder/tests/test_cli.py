"""test_cli.py — TDD tests for kpm_builder.cli.build_from_research.

Written FIRST (red), then the implementation makes them green.

Two scenarios:
  A) KPM path  — beat 1 has 2 entails claims (arxiv) → ANSWERED.
                  beat 2 has 1 over_claims claim   → ABSTAINED (n<2).
                  answered_fraction = 0.5 >= 0.3   → is_kpm=True
                  * Only entails claims shipped as axioms.
                  * Written KPM passes doctrine_lint (lint_ok=True).

  B) Research log path — both beats have over_claims / reject claims only.
                          answered_fraction = 0.0 < 0.3 → is_kpm=False.
                          * out_dir/research_log.json exists.
                          * No axioms/ dir (or empty if created, but spec says DON'T write axioms).

Every CoverageRow in both scenarios must have corpus_relative=True.
"""

from __future__ import annotations

import json
import pathlib
import tempfile

import pytest

from kpm_builder.label import BuildOutcome, CoverageState
from kpm_builder.cli import build_from_research
from package_research.validate import validate


# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

FETCHED_AT = "2026-06-04T00:00:00Z"
RUN_DATE = "2026-06-04"

# Beat 1 — two entails claims (arxiv sources → PREPRINT tier cap = SUPPORTED,
# but n_corroborations=1 → drops to PARTIAL; however 2 quality sources means
# n_quality_sources=2 ≥ min_sources → ANSWERED via question_state).
BEAT_1 = {
    "question": "What does the evidence say about memory consolidation during sleep?",
    "claims": [
        {
            "statement": "Sleep spindles during NREM are necessary for hippocampal-neocortical transfer.",
            "source": {
                "url": "https://arxiv.org/abs/2001.00001",
                "text": (
                    "A series of polysomnographic studies demonstrates that sleep spindle "
                    "activity during NREM sleep is necessary for hippocampal-neocortical "
                    "transfer of memories. Spindle density correlates strongly with next-day "
                    "declarative memory performance (r=0.71, p<0.001)."
                ),
                "venue": "arxiv.org",
            },
            "ground_verdict": "entails",
            "n_corroborations": 1,
            "survived_refuter": True,
            "generativity": 4,
        },
        {
            "statement": "Declarative memory performance correlates with spindle density (r=0.71).",
            "source": {
                "url": "https://arxiv.org/abs/2001.00002",
                "text": (
                    "Our meta-analysis of 18 sleep studies confirms that spindle density "
                    "predicts declarative memory consolidation with a correlation of r=0.71 "
                    "across independent cohorts. This confirms the role of NREM in memory."
                ),
                "venue": "arxiv.org",
            },
            "ground_verdict": "entails",
            "n_corroborations": 2,
            "survived_refuter": True,
            "generativity": 3,
        },
    ],
}

# Beat 2 — single over_claims claim (n_quality_sources=1 < 2 → ABSTAINED).
BEAT_2 = {
    "question": "Does taking melatonin before bed universally improve sleep quality?",
    "claims": [
        {
            "statement": "Melatonin universally eliminates insomnia in all adult populations.",
            "source": {
                "url": "https://medium.com/sleep-hacks/melatonin",
                "text": (
                    "A small pilot study of 8 participants found that 3mg melatonin "
                    "improved sleep onset by 12 minutes on average in young adults "
                    "with mild insomnia."
                ),
                "venue": "medium.com",
            },
            "ground_verdict": "over_claims",
            "n_corroborations": 1,
            "survived_refuter": False,
            "generativity": 2,
        },
    ],
}

# Contract for the KPM scenario.
CONTRACT_KPM = {
    "goal": "Understand the neural mechanisms of memory consolidation.",
    "in_scope": "Sleep research, memory consolidation, neuroscience studies",
    "out_of_scope": "General wellness, unrelated health topics",
}

BEATS_KPM = [BEAT_1, BEAT_2]

# ---------------------------------------------------------------------------
# Research-log scenario — ALL claims over_claims or reject.
# ---------------------------------------------------------------------------

BEAT_A = {
    "question": "Is coffee a universal cure for fatigue?",
    "claims": [
        {
            "statement": "Coffee cures all forms of fatigue permanently.",
            "source": {
                "url": "https://medium.com/health-hacks/coffee",
                "text": "Some users report feeling less tired after drinking coffee.",
                "venue": "medium.com",
            },
            "ground_verdict": "over_claims",
            "n_corroborations": 1,
            "survived_refuter": False,
            "generativity": 1,
        },
    ],
}

BEAT_B = {
    "question": "Does standing up improve productivity by 200%?",
    "claims": [
        {
            "statement": "Standing desks double all workers' productivity.",
            "source": {
                "url": "https://example-blog.com/standing",
                "text": "We did not measure productivity in this observational note.",
                "venue": "",
            },
            "ground_verdict": "reject",
            "n_corroborations": 0,
            "survived_refuter": False,
            "generativity": 1,
        },
    ],
}

CONTRACT_LOG = {
    "goal": "Evaluate pseudoscientific health claims.",
    "in_scope": "Any health claim",
    "out_of_scope": "Nothing",
}

BEATS_LOG = [BEAT_A, BEAT_B]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_kpm(tmp_path: pathlib.Path):
    """Run build_from_research for the KPM scenario."""
    out_dir = tmp_path / "kpm_out"
    outcome = build_from_research(
        CONTRACT_KPM,
        BEATS_KPM,
        out_dir=out_dir,
        run_date=RUN_DATE,
        fetched_at=FETCHED_AT,
    )
    return outcome, out_dir


def _run_log(tmp_path: pathlib.Path):
    """Run build_from_research for the research-log scenario."""
    out_dir = tmp_path / "log_out"
    outcome = build_from_research(
        CONTRACT_LOG,
        BEATS_LOG,
        out_dir=out_dir,
        run_date=RUN_DATE,
        fetched_at=FETCHED_AT,
    )
    return outcome, out_dir


# ---------------------------------------------------------------------------
# KPM path tests
# ---------------------------------------------------------------------------


class TestKpmPath:
    """Scenario A — enough entails claims → is_kpm=True."""

    @pytest.fixture(scope="class")
    def kpm_result(self, tmp_path_factory):
        tmp = tmp_path_factory.mktemp("kpm")
        return _run_kpm(tmp)

    def test_is_kpm_true(self, kpm_result):
        outcome, _ = kpm_result
        assert isinstance(outcome, BuildOutcome)
        assert outcome.is_kpm is True, (
            f"Expected is_kpm=True for 1 ANSWERED beat, got label={outcome.label!r}"
        )

    def test_over_claims_not_shipped_as_axiom(self, kpm_result):
        """The over_claims claim (BEAT_2's only claim) must NOT appear as a shipped axiom."""
        _, out_dir = kpm_result
        axioms_dir = out_dir / "axioms"
        if not axioms_dir.exists():
            return  # no axioms written at all — fine, over_claims not shipped
        for axiom_file in axioms_dir.glob("*.md"):
            content = axiom_file.read_text()
            assert "universally eliminates insomnia" not in content, (
                f"over_claims statement was shipped as axiom in {axiom_file.name}"
            )

    def test_kpm_passes_validate(self, kpm_result):
        """The written KPM must pass doctrine_lint."""
        _, out_dir = kpm_result
        result = validate(out_dir)
        assert result.lint_ok, (
            "doctrine_lint FAILED:\n" + "\n".join(f"  - {v}" for v in result.lint_violations)
        )

    def test_every_row_corpus_relative(self, kpm_result):
        outcome, _ = kpm_result
        for row in outcome.report.rows:
            assert row.corpus_relative is True, (
                f"Row '{row.core_question}' has corpus_relative=False"
            )

    def test_entails_claims_shipped(self, kpm_result):
        """At least one axiom should be written (the entails claims from BEAT_1)."""
        _, out_dir = kpm_result
        axioms_dir = out_dir / "axioms"
        assert axioms_dir.exists(), "axioms/ dir not written for is_kpm=True"
        axiom_files = list(axioms_dir.glob("*.md"))
        assert len(axiom_files) >= 1, "No axiom files written despite entails claims"

    def test_no_research_log_on_kpm_path(self, kpm_result):
        """research_log.json should NOT exist when outcome is a KPM."""
        _, out_dir = kpm_result
        assert not (out_dir / "research_log.json").exists(), (
            "research_log.json was written even though outcome is a KPM"
        )


# ---------------------------------------------------------------------------
# Research-log path tests
# ---------------------------------------------------------------------------


class TestResearchLogPath:
    """Scenario B — no entails claims → is_kpm=False → research_log.json."""

    @pytest.fixture(scope="class")
    def log_result(self, tmp_path_factory):
        tmp = tmp_path_factory.mktemp("log")
        return _run_log(tmp)

    def test_is_kpm_false(self, log_result):
        outcome, _ = log_result
        assert isinstance(outcome, BuildOutcome)
        assert outcome.is_kpm is False, (
            f"Expected is_kpm=False for all over_claims/reject, got label={outcome.label!r}"
        )

    def test_research_log_json_exists(self, log_result):
        _, out_dir = log_result
        assert (out_dir / "research_log.json").exists(), (
            "research_log.json was not written for research_log_only outcome"
        )

    def test_no_axioms_dir_on_log_path(self, log_result):
        """When is_kpm=False, axioms/ dir must not exist (or be empty)."""
        _, out_dir = log_result
        axioms_dir = out_dir / "axioms"
        if axioms_dir.exists():
            axiom_files = list(axioms_dir.glob("*.md"))
            assert len(axiom_files) == 0, (
                f"axioms/ dir exists and has files despite research_log_only outcome: "
                f"{[f.name for f in axiom_files]}"
            )

    def test_research_log_json_has_contract(self, log_result):
        _, out_dir = log_result
        data = json.loads((out_dir / "research_log.json").read_text())
        assert "contract" in data, "research_log.json missing 'contract' key"

    def test_research_log_json_has_beats(self, log_result):
        _, out_dir = log_result
        data = json.loads((out_dir / "research_log.json").read_text())
        assert "beats" in data, "research_log.json missing 'beats' key"

    def test_research_log_json_has_coverage(self, log_result):
        _, out_dir = log_result
        data = json.loads((out_dir / "research_log.json").read_text())
        assert "coverage" in data, "research_log.json missing 'coverage' key"

    def test_every_row_corpus_relative(self, log_result):
        outcome, _ = log_result
        for row in outcome.report.rows:
            assert row.corpus_relative is True, (
                f"Row '{row.core_question}' has corpus_relative=False"
            )


# ---------------------------------------------------------------------------
# Passage-scoped evidence spans (REVIEW.md KPM-H5)
# ---------------------------------------------------------------------------

_PASSAGE = (
    "Sleep spindle activity during NREM sleep is necessary for "
    "hippocampal-neocortical transfer of memories."
)
# Marker that exists ONLY outside the supporting passage in the source text.
_OUTSIDE_MARKER = "GRANT-FUNDING-BOILERPLATE"

_BEAT_PASSAGE = {
    "question": "What does the evidence say about memory consolidation during sleep?",
    "claims": [
        {
            # Claim WITH a supporting passage → span must be passage-scoped.
            "statement": "Sleep spindles during NREM are necessary for hippocampal-neocortical transfer.",
            "source": {
                "url": "https://arxiv.org/abs/2001.00001",
                "text": (
                    _PASSAGE
                    + " "
                    + _OUTSIDE_MARKER
                    + ": this study was funded by grant XYZ-123."
                ),
                "venue": "arxiv.org",
            },
            "supporting_passage": _PASSAGE,
            "ground_verdict": "entails",
            "n_corroborations": 1,
            "survived_refuter": True,
            "generativity": 4,
        },
        {
            # Claim WITHOUT a passage → whole-document fallback must hold.
            "statement": "Spindle density predicts declarative memory consolidation (r=0.71).",
            "source": {
                "url": "https://arxiv.org/abs/2001.00002",
                "text": (
                    "Our meta-analysis of 18 sleep studies confirms that spindle "
                    "density predicts declarative memory consolidation with a "
                    "correlation of r=0.71 across independent cohorts."
                ),
                "venue": "arxiv.org",
            },
            "ground_verdict": "entails",
            "n_corroborations": 2,
            "survived_refuter": True,
            "generativity": 3,
        },
    ],
}


class TestPassageScopedSpans:
    """KPM-H5 — shipped evidence is the supporting passage, not a doc dump."""

    @pytest.fixture(scope="class")
    def passage_result(self, tmp_path_factory):
        tmp = tmp_path_factory.mktemp("passage")
        out_dir = tmp / "out"
        outcome = build_from_research(
            CONTRACT_KPM,
            [_BEAT_PASSAGE],
            out_dir=out_dir,
            run_date=RUN_DATE,
            fetched_at=FETCHED_AT,
        )
        return outcome, out_dir

    def _evidence_body_for(self, out_dir, fragment):
        """Concatenated text of evidence notes containing `fragment`."""
        bodies = [
            f.read_text()
            for f in (out_dir / "evidence").glob("*.md")
        ]
        return "\n".join(b for b in bodies if fragment in b)

    def test_is_kpm(self, passage_result):
        outcome, _ = passage_result
        assert outcome.is_kpm is True

    def test_evidence_span_is_the_passage(self, passage_result):
        """Evidence note for the passage claim carries the passage verbatim."""
        _, out_dir = passage_result
        body = self._evidence_body_for(out_dir, _PASSAGE)
        assert body, "Supporting passage not found in any evidence note."

    def test_evidence_span_excludes_rest_of_document(self, passage_result):
        """The non-passage part of the document must NOT ship as evidence."""
        _, out_dir = passage_result
        for f in (out_dir / "evidence").glob("*.md"):
            assert _OUTSIDE_MARKER not in f.read_text(), (
                f"Whole-document text leaked into {f.name} — the span was "
                "not scoped to the supporting_passage (KPM-H5)."
            )

    def test_no_passage_claim_falls_back_to_whole_document(self, passage_result):
        """The claim without a supporting_passage still ships its full source."""
        _, out_dir = passage_result
        body = self._evidence_body_for(out_dir, "meta-analysis of 18 sleep studies")
        assert "across independent cohorts" in body, (
            "Whole-document fallback broke for a claim with no supporting_passage."
        )

    def test_passage_scoped_kpm_passes_validate(self, passage_result):
        _, out_dir = passage_result
        result = validate(out_dir)
        assert result.lint_ok, (
            "doctrine_lint FAILED:\n" + "\n".join(f"  - {v}" for v in result.lint_violations)
        )


# ---------------------------------------------------------------------------
# n_corroborations honored (REVIEW.md KPM-M7 / EFF-5)
# ---------------------------------------------------------------------------


class TestCorroborationHonored:
    """The input's n_corroborations is honored — never overwritten with 1."""

    def _single_claim_beat(self, n_corroborations):
        return {
            "question": "Does spindle density predict memory consolidation?",
            "claims": [
                {
                    "statement": "Spindle density predicts memory consolidation.",
                    "source": {
                        "url": "https://arxiv.org/abs/2001.00099",
                        "text": "Spindle density predicts memory consolidation across cohorts.",
                        "venue": "arxiv.org",
                    },
                    "ground_verdict": "entails",
                    "n_corroborations": n_corroborations,
                    "survived_refuter": True,
                    "generativity": 3,
                },
            ],
        }

    def _row_bucket(self, tmp_path, n_corroborations):
        from kpm_builder.schema import ConfidenceBucket  # local: assertion type
        outcome = build_from_research(
            CONTRACT_KPM,
            [self._single_claim_beat(n_corroborations)],
            out_dir=tmp_path / f"corr_{n_corroborations}",
            run_date=RUN_DATE,
            fetched_at=FETCHED_AT,
        )
        return outcome.report.rows[0].confidence_bucket, ConfidenceBucket

    def test_two_corroborations_reach_supported(self, tmp_path):
        bucket, ConfidenceBucket = self._row_bucket(tmp_path, 2)
        assert bucket == ConfidenceBucket.SUPPORTED, (
            f"n_corroborations=2 on a PREPRINT entails claim must reach "
            f"SUPPORTED; got {bucket}."
        )

    def test_one_corroboration_stays_partial(self, tmp_path):
        bucket, ConfidenceBucket = self._row_bucket(tmp_path, 1)
        assert bucket == ConfidenceBucket.PARTIAL, (
            f"A single-source claim must not reach SUPPORTED; got {bucket}."
        )


# ---------------------------------------------------------------------------
# JSON round-trip test
# ---------------------------------------------------------------------------


class TestJsonRoundTrip:
    """A JSON string → parse → build_from_research round-trips cleanly."""

    def test_json_string_roundtrip(self, tmp_path):
        """Parse from a JSON string and call build_from_research — should not raise."""
        payload = {
            "contract": CONTRACT_KPM,
            "beats": BEATS_KPM,
        }
        # Serialise → parse (the round-trip)
        raw = json.dumps(payload)
        loaded = json.loads(raw)

        out_dir = tmp_path / "rt_out"
        outcome = build_from_research(
            loaded["contract"],
            loaded["beats"],
            out_dir=out_dir,
            run_date=RUN_DATE,
            fetched_at=FETCHED_AT,
        )
        assert isinstance(outcome, BuildOutcome)
