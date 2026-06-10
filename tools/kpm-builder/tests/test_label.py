"""
Tests for kpm_builder.label — honest completeness labeling.

TDD order: write tests first, watch them fail, then implement.
"""
import pytest
from kpm_builder.label import (
    CoverageState,
    CoverageRow,
    CoverageReport,
    BuildOutcome,
    TerminationReason,
    question_state,
    decide,
    ABSTAIN_MAX,
    MIN_COVERAGE_FLOOR,
)
from kpm_builder.schema import ConfidenceBucket


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_row(state: CoverageState, q: str = "q") -> CoverageRow:
    return CoverageRow(core_question=q, state=state)


def make_report(states: list[CoverageState],
                reason: TerminationReason = TerminationReason.CONVERGED) -> CoverageReport:
    rows = [make_row(s, f"q{i}") for i, s in enumerate(states)]
    return CoverageReport(rows=rows, termination_reason=reason)


# ---------------------------------------------------------------------------
# question_state tests
# ---------------------------------------------------------------------------

class TestQuestionState:
    def test_not_researched_gives_not_reached(self):
        state = question_state(
            researched=False,
            grounded=False,
            survived_refuter=False,
            n_quality_sources=5,
            has_dissensus=False,
        )
        assert state == CoverageState.NOT_REACHED

    def test_one_source_gives_abstained(self):
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=1,   # < min_sources=2
            has_dissensus=False,
        )
        assert state == CoverageState.ABSTAINED

    def test_zero_sources_gives_abstained(self):
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=0,
            has_dissensus=False,
        )
        assert state == CoverageState.ABSTAINED

    def test_has_dissensus_gives_abstained(self):
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=5,
            has_dissensus=True,
        )
        assert state == CoverageState.ABSTAINED

    def test_grounded_and_survived_gives_answered(self):
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=3,
            has_dissensus=False,
        )
        assert state == CoverageState.ANSWERED

    def test_grounded_but_not_survived_gives_partial(self):
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=False,
            n_quality_sources=3,
            has_dissensus=False,
        )
        assert state == CoverageState.PARTIAL

    def test_not_grounded_not_survived_gives_partial(self):
        state = question_state(
            researched=True,
            grounded=False,
            survived_refuter=False,
            n_quality_sources=3,
            has_dissensus=False,
        )
        assert state == CoverageState.PARTIAL

    def test_custom_min_sources(self):
        # With min_sources=4, n_quality_sources=3 should be ABSTAINED
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=3,
            has_dissensus=False,
            min_sources=4,
        )
        assert state == CoverageState.ABSTAINED

    def test_exact_min_sources_passes(self):
        # Exactly at min_sources threshold is sufficient (>= semantics)
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=2,
            has_dissensus=False,
            min_sources=2,
        )
        assert state == CoverageState.ANSWERED

    def test_not_researched_overrides_all(self):
        # Even with good sources, not_researched wins
        state = question_state(
            researched=False,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=10,
            has_dissensus=False,
        )
        assert state == CoverageState.NOT_REACHED

    def test_dissensus_overrides_good_sources(self):
        # dissensus + many sources => still ABSTAINED
        state = question_state(
            researched=True,
            grounded=True,
            survived_refuter=True,
            n_quality_sources=10,
            has_dissensus=True,
        )
        assert state == CoverageState.ABSTAINED


# ---------------------------------------------------------------------------
# CoverageRow corpus_relative enforcement
# ---------------------------------------------------------------------------

class TestCoverageRowCorpusRelative:
    def test_default_corpus_relative_true(self):
        row = make_row(CoverageState.ANSWERED)
        assert row.corpus_relative is True

    def test_corpus_relative_false_raises(self):
        with pytest.raises(ValueError, match="corpus_relative"):
            CoverageRow(
                core_question="q",
                state=CoverageState.ANSWERED,
                corpus_relative=False,
            )

    def test_corpus_relative_true_explicit_ok(self):
        row = CoverageRow(
            core_question="q",
            state=CoverageState.ANSWERED,
            corpus_relative=True,
        )
        assert row.corpus_relative is True

    def test_with_confidence_bucket(self):
        row = CoverageRow(
            core_question="q",
            state=CoverageState.ANSWERED,
            confidence_bucket=ConfidenceBucket.SUPPORTED,
        )
        assert row.confidence_bucket == ConfidenceBucket.SUPPORTED
        assert row.corpus_relative is True


# ---------------------------------------------------------------------------
# CoverageReport fraction / answered_fraction / abstained_fraction
# ---------------------------------------------------------------------------

class TestCoverageReportFractions:
    def test_empty_report_answered_fraction_is_zero(self):
        report = CoverageReport(rows=[], termination_reason=TerminationReason.CONVERGED)
        assert report.answered_fraction == 0.0

    def test_empty_report_abstained_fraction_is_zero(self):
        report = CoverageReport(rows=[], termination_reason=TerminationReason.CONVERGED)
        assert report.abstained_fraction == 0.0

    def test_empty_report_fraction_is_zero(self):
        report = CoverageReport(rows=[], termination_reason=TerminationReason.CONVERGED)
        assert report.fraction(CoverageState.ANSWERED) == 0.0

    def test_all_answered(self):
        report = make_report([CoverageState.ANSWERED] * 4)
        assert report.answered_fraction == 1.0
        assert report.abstained_fraction == 0.0

    def test_mixed_fractions(self):
        # 2 ANSWERED, 1 ABSTAINED, 1 PARTIAL, 1 NOT_REACHED  => 5 total
        states = [
            CoverageState.ANSWERED,
            CoverageState.ANSWERED,
            CoverageState.ABSTAINED,
            CoverageState.PARTIAL,
            CoverageState.NOT_REACHED,
        ]
        report = make_report(states)
        assert report.answered_fraction == pytest.approx(2 / 5)
        assert report.abstained_fraction == pytest.approx(1 / 5)
        assert report.fraction(CoverageState.PARTIAL) == pytest.approx(1 / 5)
        assert report.fraction(CoverageState.NOT_REACHED) == pytest.approx(1 / 5)

    def test_fraction_sums_to_one(self):
        states = [
            CoverageState.ANSWERED,
            CoverageState.ABSTAINED,
            CoverageState.PARTIAL,
            CoverageState.NOT_REACHED,
        ]
        report = make_report(states)
        total = sum(report.fraction(s) for s in CoverageState)
        assert total == pytest.approx(1.0)

    def test_single_row_answered(self):
        report = make_report([CoverageState.ANSWERED])
        assert report.answered_fraction == 1.0
        assert report.abstained_fraction == 0.0


# ---------------------------------------------------------------------------
# decide() BuildOutcome
# ---------------------------------------------------------------------------

class TestDecide:
    def test_converged_when_mostly_answered(self):
        # 4 ANSWERED, 1 PARTIAL => answered=0.8, abstained=0.0
        states = [CoverageState.ANSWERED] * 4 + [CoverageState.PARTIAL]
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is True
        assert outcome.label == "converged"
        assert outcome.report is report

    def test_ceiling_truncated_flows_through(self):
        # termination_reason flows to label when answered >= floor and abstained <= max
        states = [CoverageState.ANSWERED] * 4 + [CoverageState.PARTIAL]
        report = make_report(states, reason=TerminationReason.CEILING_TRUNCATED)
        outcome = decide(report)
        assert outcome.is_kpm is True
        assert outcome.label == "ceiling_truncated"

    def test_killed_flows_through(self):
        states = [CoverageState.ANSWERED] * 4 + [CoverageState.PARTIAL]
        report = make_report(states, reason=TerminationReason.KILLED)
        outcome = decide(report)
        assert outcome.is_kpm is True
        assert outcome.label == "killed"

    def test_lite_flows_through(self):
        states = [CoverageState.ANSWERED] * 4 + [CoverageState.PARTIAL]
        report = make_report(states, reason=TerminationReason.LITE)
        outcome = decide(report)
        assert outcome.is_kpm is True
        assert outcome.label == "lite"

    def test_scope_partially_researchable_when_abstained_exceeds_max(self):
        # ABSTAIN_MAX = 0.5 — need > 50% abstained, but >= 30% answered
        # 4 ANSWERED, 6 ABSTAINED => answered=0.4, abstained=0.6
        states = [CoverageState.ANSWERED] * 4 + [CoverageState.ABSTAINED] * 6
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is True
        assert outcome.label == "scope_partially_researchable"

    def test_research_log_only_when_below_floor(self):
        # MIN_COVERAGE_FLOOR = 0.3 — need < 30% answered
        # 2 ANSWERED, 8 NOT_REACHED => answered=0.2
        states = [CoverageState.ANSWERED] * 2 + [CoverageState.NOT_REACHED] * 8
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is False
        assert outcome.label == "research_log_only"
        assert outcome.report is report

    def test_research_log_only_takes_priority_over_abstain(self):
        # < floor answered AND > max abstained — floor check wins (is_kpm=False)
        # 1 ANSWERED, 9 ABSTAINED => answered=0.1, abstained=0.9
        states = [CoverageState.ANSWERED] * 1 + [CoverageState.ABSTAINED] * 9
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is False
        assert outcome.label == "research_log_only"

    def test_exact_floor_boundary_is_kpm(self):
        # answered = exactly MIN_COVERAGE_FLOOR (0.3) should NOT trigger research_log
        # (condition is answered_fraction < floor, so 0.3 is fine)
        # 3 ANSWERED, 7 PARTIAL => answered=0.3
        states = [CoverageState.ANSWERED] * 3 + [CoverageState.PARTIAL] * 7
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is True

    def test_just_below_floor_is_not_kpm(self):
        # 29 ANSWERED, 71 NOT_REACHED => answered≈0.29
        states = [CoverageState.ANSWERED] * 29 + [CoverageState.NOT_REACHED] * 71
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is False
        assert outcome.label == "research_log_only"

    def test_exactly_abstain_max_is_not_partially_researchable(self):
        # ABSTAIN_MAX = 0.5 — exactly 0.5 should NOT trigger (condition is > ABSTAIN_MAX)
        # 5 ANSWERED, 5 ABSTAINED => answered=0.5, abstained=0.5
        states = [CoverageState.ANSWERED] * 5 + [CoverageState.ABSTAINED] * 5
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is True
        assert outcome.label == "converged"

    def test_just_above_abstain_max_triggers_partially_researchable(self):
        # 10 ANSWERED, 11 ABSTAINED => abstained≈0.524 > 0.5
        states = [CoverageState.ANSWERED] * 10 + [CoverageState.ABSTAINED] * 11
        report = make_report(states, reason=TerminationReason.CONVERGED)
        outcome = decide(report)
        assert outcome.is_kpm is True
        assert outcome.label == "scope_partially_researchable"
