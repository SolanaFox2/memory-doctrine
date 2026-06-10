"""
kpm_builder.label
-----------------
Honest completeness labeling — every core question gets a state, the package
carries why-it-stopped, abstention is a labeled outcome (not a hard failure),
and below a floor the tool returns a research log instead of a package that
lies about being one.

Design constraints:
- PURE — no LLM, no I/O, stdlib only
- corpus_relative=True is ENFORCED — can never be dropped from a CoverageRow
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from kpm_builder.schema import ConfidenceBucket


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CoverageState(Enum):
    ANSWERED    = "answered"
    PARTIAL     = "partial"
    ABSTAINED   = "abstained"
    NOT_REACHED = "not_reached"


class TerminationReason(Enum):
    CONVERGED         = "converged"
    CEILING_TRUNCATED = "ceiling_truncated"
    KILLED            = "killed"
    LITE              = "lite"


# ---------------------------------------------------------------------------
# Module-level thresholds (tune later)
# ---------------------------------------------------------------------------

ABSTAIN_MAX        = 0.5   # > this fraction abstained -> "scope_partially_researchable"
MIN_COVERAGE_FLOOR = 0.3   # answered fraction < this  -> NOT a KPM, return a research log


# ---------------------------------------------------------------------------
# question_state
# ---------------------------------------------------------------------------

def question_state(
    *,
    researched: bool,
    grounded: bool,
    survived_refuter: bool,
    n_quality_sources: int,
    has_dissensus: bool,
    min_sources: int = 2,
) -> CoverageState:
    """
    Assign a CoverageState to a single core question.

    Decision tree (in priority order):
    1. NOT_REACHED   — if not researched at all
    2. ABSTAINED     — if n_quality_sources < min_sources OR has_dissensus
    3. ANSWERED      — if grounded AND survived_refuter
    4. PARTIAL       — otherwise (researched, enough sources, no dissensus,
                       but failed grounding or refutation)
    """
    if not researched:
        return CoverageState.NOT_REACHED

    if n_quality_sources < min_sources or has_dissensus:
        return CoverageState.ABSTAINED

    if grounded and survived_refuter:
        return CoverageState.ANSWERED

    return CoverageState.PARTIAL


# ---------------------------------------------------------------------------
# CoverageRow
# ---------------------------------------------------------------------------

@dataclass
class CoverageRow:
    """
    One row in a coverage report — one core question, one state.

    corpus_relative MUST be True: confidence is always conditional on the
    corpus that was searched. This invariant is enforced in __post_init__
    so the label can never be silently dropped.
    """
    core_question:    str
    state:            CoverageState
    confidence_bucket: ConfidenceBucket | None = None
    corpus_relative:  bool = True

    def __post_init__(self) -> None:
        if not self.corpus_relative:
            raise ValueError(
                "corpus_relative must be True — confidence is always "
                "conditional on the searched corpus and this label cannot be dropped."
            )


# ---------------------------------------------------------------------------
# CoverageReport
# ---------------------------------------------------------------------------

@dataclass
class CoverageReport:
    """
    The full set of coverage rows plus the reason the pipeline stopped.
    """
    rows:               list[CoverageRow]
    termination_reason: TerminationReason

    def fraction(self, state: CoverageState) -> float:
        """Return the fraction of rows with *state*; 0.0 if the report is empty."""
        if not self.rows:
            return 0.0
        return sum(1 for r in self.rows if r.state == state) / len(self.rows)

    @property
    def answered_fraction(self) -> float:
        """ANSWERED rows / total rows (0.0 if empty)."""
        return self.fraction(CoverageState.ANSWERED)

    @property
    def abstained_fraction(self) -> float:
        """ABSTAINED rows / total rows (0.0 if empty)."""
        return self.fraction(CoverageState.ABSTAINED)


# ---------------------------------------------------------------------------
# BuildOutcome + decide
# ---------------------------------------------------------------------------

@dataclass
class BuildOutcome:
    """
    Final verdict: is the output a KPM, or just a research log?

    is_kpm=False means the caller should return a research log, not a KPM
    that lies about being complete.
    """
    is_kpm: bool
    label:  str   # "converged" | "ceiling_truncated" | "killed" | "lite"
                  # | "scope_partially_researchable" | "research_log_only"
    report: CoverageReport


def decide(report: CoverageReport) -> BuildOutcome:
    """
    Map a CoverageReport to a BuildOutcome.

    Priority:
    1. answered_fraction < MIN_COVERAGE_FLOOR
           → BuildOutcome(is_kpm=False, label="research_log_only")
    2. abstained_fraction > ABSTAIN_MAX
           → BuildOutcome(is_kpm=True,  label="scope_partially_researchable")
    3. otherwise
           → BuildOutcome(is_kpm=True,  label=report.termination_reason.value)
    """
    if report.answered_fraction < MIN_COVERAGE_FLOOR:
        return BuildOutcome(is_kpm=False, label="research_log_only", report=report)

    if report.abstained_fraction > ABSTAIN_MAX:
        return BuildOutcome(is_kpm=True, label="scope_partially_researchable", report=report)

    return BuildOutcome(
        is_kpm=True,
        label=report.termination_reason.value,
        report=report,
    )
