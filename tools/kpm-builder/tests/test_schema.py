"""
Tests for kpm_builder.schema — written FIRST (TDD red phase).
Run with:
  PYTHONPATH=tools/kpm-builder python3 -m pytest \
      tools/kpm-builder/tests/test_schema.py -q
"""
import pytest

from kpm_builder.snapshot import Snapshot, SpanRef, make_span, snapshot
from kpm_builder.schema import (
    ScoredIdea,
    SourceTier,
    ConfidenceBucket,
    from_dict,
    generativity_input,
    to_dict,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snap(text: str = "The quick brown fox jumps over the lazy dog") -> Snapshot:
    return snapshot(
        "http://example.com/paper",
        fetcher=lambda u: text,
        fetched_at="2026-06-04T00:00:00",
        extractor="raw",
        access_level="full_text",
    )


def _idea(*, span: SpanRef | None = None, generativity: int = 3) -> ScoredIdea:
    return ScoredIdea(
        statement="Neural scaling laws predict continued capability gains.",
        source_ref="http://example.com/paper",
        span=span,
        source_tier=SourceTier.PEER_REVIEWED,
        access_level="full_text",
        confidence=ConfidenceBucket.SUPPORTED,
        generativity=generativity,
        contradicts=["scaling_skepticism_claim"],
        defeaters=["compute_wall_hypothesis"],
        rationale="Strong empirical evidence across modalities.",
    )


# ---------------------------------------------------------------------------
# 1. SourceTier ordering — int values encode rank (best=0)
# ---------------------------------------------------------------------------

def test_source_tier_ordering():
    assert SourceTier.PEER_REVIEWED.value < SourceTier.PREPRINT.value
    assert SourceTier.PREPRINT.value < SourceTier.OFFICIAL_DOCS.value
    assert SourceTier.OFFICIAL_DOCS.value < SourceTier.REPUTABLE_PRESS.value
    assert SourceTier.REPUTABLE_PRESS.value < SourceTier.BLOG.value
    assert SourceTier.BLOG.value < SourceTier.UNKNOWN.value


def test_source_tier_best_is_zero():
    assert SourceTier.PEER_REVIEWED.value == 0


# ---------------------------------------------------------------------------
# 2. generativity validation
# ---------------------------------------------------------------------------

def test_generativity_valid_boundaries():
    lo = _idea(generativity=1)
    hi = _idea(generativity=5)
    assert lo.generativity == 1
    assert hi.generativity == 5


def test_generativity_zero_raises():
    with pytest.raises(ValueError):
        _idea(generativity=0)


def test_generativity_six_raises():
    with pytest.raises(ValueError):
        _idea(generativity=6)


def test_generativity_negative_raises():
    with pytest.raises(ValueError):
        _idea(generativity=-1)


def test_generativity_in_range_accepted():
    for v in (1, 2, 3, 4, 5):
        idea = _idea(generativity=v)
        assert idea.generativity == v


# ---------------------------------------------------------------------------
# 3. to_dict / from_dict round-trip — fully populated (with real SpanRef)
# ---------------------------------------------------------------------------

def test_round_trip_full():
    snap = _snap()
    span = make_span(snap, 4, 9)   # "quick"
    idea = _idea(span=span)

    d = to_dict(idea)
    restored = from_dict(d)

    assert restored == idea


def test_round_trip_span_none():
    idea = _idea(span=None)
    d = to_dict(idea)
    restored = from_dict(d)
    assert restored == idea
    assert restored.span is None


def test_round_trip_preserves_all_fields():
    snap = _snap()
    span = make_span(snap, 0, 3)   # "The"
    idea = _idea(span=span, generativity=4)

    restored = from_dict(to_dict(idea))

    assert restored.statement == idea.statement
    assert restored.source_ref == idea.source_ref
    assert restored.span == idea.span
    assert restored.source_tier == idea.source_tier
    assert restored.access_level == idea.access_level
    assert restored.confidence == idea.confidence
    assert restored.generativity == idea.generativity
    assert restored.contradicts == idea.contradicts
    assert restored.defeaters == idea.defeaters
    assert restored.rationale == idea.rationale


# ---------------------------------------------------------------------------
# 4. Enum serialisation
# ---------------------------------------------------------------------------

def test_source_tier_serialises_by_name():
    idea = _idea()
    d = to_dict(idea)
    assert d["source_tier"] == "PEER_REVIEWED"


def test_source_tier_deserialises_by_name():
    idea = _idea()
    d = to_dict(idea)
    restored = from_dict(d)
    assert restored.source_tier is SourceTier.PEER_REVIEWED


def test_confidence_bucket_serialises_by_value():
    idea = _idea()
    d = to_dict(idea)
    assert d["confidence"] == "supported"


def test_confidence_bucket_deserialises_by_value():
    idea = _idea()
    d = to_dict(idea)
    restored = from_dict(d)
    assert restored.confidence is ConfidenceBucket.SUPPORTED


def test_all_source_tiers_round_trip():
    for tier in SourceTier:
        idea = ScoredIdea(
            statement="x",
            source_ref="http://x.com",
            span=None,
            source_tier=tier,
            access_level="abstract_only",
            confidence=ConfidenceBucket.UNVERIFIED,
            generativity=2,
        )
        restored = from_dict(to_dict(idea))
        assert restored.source_tier is tier


def test_all_confidence_buckets_round_trip():
    for bucket in ConfidenceBucket:
        idea = ScoredIdea(
            statement="x",
            source_ref="http://x.com",
            span=None,
            source_tier=SourceTier.BLOG,
            access_level="secondary",
            confidence=bucket,
            generativity=2,
        )
        restored = from_dict(to_dict(idea))
        assert restored.confidence is bucket


# ---------------------------------------------------------------------------
# 5. SpanRef serialises to / from dict
# ---------------------------------------------------------------------------

def test_span_ref_serialises_to_dict():
    snap = _snap()
    span = make_span(snap, 4, 9)
    idea = _idea(span=span)
    d = to_dict(idea)
    assert isinstance(d["span"], dict)
    assert "sha256" in d["span"]
    assert d["span"]["start"] == 4
    assert d["span"]["end"] == 9
    assert d["span"]["text"] == "quick"


def test_span_ref_none_serialises_as_none():
    idea = _idea(span=None)
    d = to_dict(idea)
    assert d["span"] is None


# ---------------------------------------------------------------------------
# 6. The three-orderings invariant — generativity_input MUST NOT contain 'confidence'
# ---------------------------------------------------------------------------

def test_generativity_input_excludes_confidence():
    snap = _snap()
    span = make_span(snap, 4, 9)
    idea = _idea(span=span)
    gi = generativity_input(idea)
    assert "confidence" not in gi, (
        "three-orderings rule violated: generativity scorer must never see confidence"
    )


def test_generativity_input_contains_statement():
    idea = _idea()
    gi = generativity_input(idea)
    assert "statement" in gi
    assert gi["statement"] == idea.statement


def test_generativity_input_contains_source_tier():
    idea = _idea()
    gi = generativity_input(idea)
    assert "source_tier" in gi


def test_generativity_input_contains_access_level():
    idea = _idea()
    gi = generativity_input(idea)
    assert "access_level" in gi


def test_generativity_input_span_text_when_span_present():
    snap = _snap()
    span = make_span(snap, 4, 9)  # "quick"
    idea = _idea(span=span)
    gi = generativity_input(idea)
    assert "span_text" in gi
    assert gi["span_text"] == "quick"


def test_generativity_input_span_text_none_when_span_absent():
    idea = _idea(span=None)
    gi = generativity_input(idea)
    assert "span_text" in gi
    assert gi["span_text"] is None
