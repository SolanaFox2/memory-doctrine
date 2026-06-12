"""
Tests for kpm_builder.snapshot — write FIRST (TDD red phase).
Run with:
  PYTHONPATH=tools/kpm-builder python3 -m pytest \
      tools/kpm-builder/tests/test_snapshot.py -q
"""
import hashlib
import pytest

from kpm_builder.snapshot import (
    Snapshot,
    SpanRef,
    make_span,
    passage_span,
    resolve_span,
    snapshot,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snap(text="hello world", url="http://example.com", fetched_at="2026-01-01",
          extractor="raw", access_level="full_text") -> Snapshot:
    return snapshot(url, fetcher=lambda u: text, fetched_at=fetched_at,
                    extractor=extractor, access_level=access_level)


# ---------------------------------------------------------------------------
# 1. Determinism — same inputs → identical sha256 and equal Snapshots
# ---------------------------------------------------------------------------

def test_determinism_sha256():
    s1 = _snap()
    s2 = _snap()
    assert s1.sha256 == s2.sha256


def test_determinism_equal_snapshots():
    s1 = _snap()
    s2 = _snap()
    assert s1 == s2


# ---------------------------------------------------------------------------
# 2. sha256 is sha256 of the TEXT (utf-8)
# ---------------------------------------------------------------------------

def test_sha256_is_of_text():
    text = "hello world"
    s = _snap(text=text)
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert s.sha256 == expected


def test_sha256_changes_with_text():
    s1 = _snap(text="hello world")
    s2 = _snap(text="goodbye world")
    assert s1.sha256 != s2.sha256


# ---------------------------------------------------------------------------
# 3. make_span + resolve_span round-trips
# ---------------------------------------------------------------------------

def test_make_span_resolve_round_trip():
    s = _snap(text="hello world")
    span = make_span(s, 0, 5)
    assert span.text == "hello"
    assert span.sha256 == s.sha256
    assert span.start == 0
    assert span.end == 5
    result = resolve_span(s, span)
    assert result == "hello"


def test_resolve_span_mid_text():
    s = _snap(text="abcdefghij")
    span = make_span(s, 3, 7)
    assert resolve_span(s, span) == "defg"


# ---------------------------------------------------------------------------
# 4. make_span out-of-range raises ValueError
# ---------------------------------------------------------------------------

def test_make_span_end_exceeds_length():
    s = _snap(text="hello")
    with pytest.raises(ValueError):
        make_span(s, 0, 10)


def test_make_span_start_equals_end():
    s = _snap(text="hello")
    with pytest.raises(ValueError):
        make_span(s, 2, 2)


def test_make_span_start_greater_than_end():
    s = _snap(text="hello")
    with pytest.raises(ValueError):
        make_span(s, 3, 1)


def test_make_span_negative_start():
    s = _snap(text="hello")
    with pytest.raises(ValueError):
        make_span(s, -1, 3)


# ---------------------------------------------------------------------------
# 5. SpanRef from snapshot A resolved against snapshot B raises ValueError
# ---------------------------------------------------------------------------

def test_resolve_span_wrong_snapshot():
    s_a = _snap(text="hello world", url="http://a.com")
    s_b = _snap(text="different text", url="http://b.com")
    span = make_span(s_a, 0, 5)
    with pytest.raises(ValueError):
        resolve_span(s_b, span)


# ---------------------------------------------------------------------------
# 6. Tampered SpanRef (.text != snap.text[start:end]) raises ValueError
# ---------------------------------------------------------------------------

def test_resolve_span_tampered_text():
    s = _snap(text="hello world")
    span = make_span(s, 0, 5)
    # Manually tamper the span text
    tampered = SpanRef(sha256=span.sha256, start=span.start, end=span.end, text="XXXXX")
    with pytest.raises(ValueError):
        resolve_span(s, tampered)


# ---------------------------------------------------------------------------
# 7. Invalid access_level raises ValueError
# ---------------------------------------------------------------------------

def test_invalid_access_level():
    with pytest.raises(ValueError):
        snapshot("http://example.com", fetcher=lambda u: "text",
                 fetched_at="2026-01-01", access_level="invalid_level")


def test_valid_access_levels():
    for level in ("full_text", "abstract_only", "secondary"):
        s = snapshot("http://example.com", fetcher=lambda u: "text",
                     fetched_at="2026-01-01", access_level=level)
        assert s.access_level == level


# ---------------------------------------------------------------------------
# 8. Injected fetcher is the text source; a raising fetcher propagates
# ---------------------------------------------------------------------------

def test_fetcher_is_called_with_url():
    called_with = []

    def tracking_fetcher(u):
        called_with.append(u)
        return "tracked text"

    url = "http://test-url.com"
    s = snapshot(url, fetcher=tracking_fetcher, fetched_at="2026-01-01")
    assert called_with == [url]
    assert s.text == "tracked text"


def test_raising_fetcher_propagates():
    def bad_fetcher(u):
        raise RuntimeError("network is injected — no real network here")

    with pytest.raises(RuntimeError, match="network is injected"):
        snapshot("http://example.com", fetcher=bad_fetcher, fetched_at="2026-01-01")


def test_no_clock_used_directly():
    """The fetched_at is always the injected value — never auto-generated."""
    ts = "2099-12-31T23:59:59"
    s = _snap(fetched_at=ts)
    assert s.fetched_at == ts


# ---------------------------------------------------------------------------
# 9. Snapshot fields are stored correctly
# ---------------------------------------------------------------------------

def test_snapshot_fields():
    s = snapshot("http://example.com/paper",
                 fetcher=lambda u: "abstract text",
                 fetched_at="2026-06-04T12:00:00",
                 extractor="pdf_extract",
                 access_level="abstract_only")
    assert s.url == "http://example.com/paper"
    assert s.fetched_at == "2026-06-04T12:00:00"
    assert s.extractor == "pdf_extract"
    assert s.access_level == "abstract_only"
    assert s.text == "abstract text"
    assert s.sha256 == hashlib.sha256(b"abstract text").hexdigest()


# ---------------------------------------------------------------------------
# 10. passage_span — passage-scoped evidence spans (REVIEW.md KPM-H5)
# ---------------------------------------------------------------------------

class TestPassageSpan:
    DOC = "Intro paragraph. The trial showed a 23% reduction (p<0.01). Outro."
    PASSAGE = "The trial showed a 23% reduction (p<0.01)."

    def test_passage_found_span_is_passage_not_whole_doc(self):
        s = _snap(text=self.DOC)
        span = passage_span(s, self.PASSAGE)
        assert span.text == self.PASSAGE
        assert span.text != s.text

    def test_passage_found_offsets_are_real(self):
        s = _snap(text=self.DOC)
        span = passage_span(s, self.PASSAGE)
        assert s.text[span.start:span.end] == self.PASSAGE
        assert span.start == self.DOC.index(self.PASSAGE)
        assert span.end == span.start + len(self.PASSAGE)

    def test_passage_span_resolves_against_snapshot(self):
        s = _snap(text=self.DOC)
        span = passage_span(s, self.PASSAGE)
        assert resolve_span(s, span) == self.PASSAGE

    def test_none_passage_falls_back_to_whole_document(self):
        s = _snap(text=self.DOC)
        span = passage_span(s, None)
        assert (span.start, span.end, span.text) == (0, len(self.DOC), self.DOC)

    def test_empty_passage_falls_back_to_whole_document(self):
        s = _snap(text=self.DOC)
        span = passage_span(s, "")
        assert span.text == self.DOC

    def test_drifted_passage_falls_back_to_whole_document(self):
        s = _snap(text=self.DOC)
        span = passage_span(s, "this passage does not occur in the snapshot")
        assert (span.start, span.end, span.text) == (0, len(self.DOC), self.DOC)

    def test_empty_snapshot_text_yields_empty_span(self):
        s = _snap(text="")
        span = passage_span(s, None)
        assert (span.start, span.end, span.text) == (0, 0, "")
        assert span.sha256 == s.sha256


# ---------------------------------------------------------------------------
# 11. Snapshot is immutable (frozen dataclass)
# ---------------------------------------------------------------------------

def test_snapshot_is_frozen():
    s = _snap()
    with pytest.raises((AttributeError, TypeError)):
        s.url = "http://tampered.com"  # type: ignore[misc]
