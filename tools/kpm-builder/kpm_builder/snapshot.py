"""
kpm_builder.snapshot
--------------------
Content-addressed cache of the exact text a model reads.

Design constraints:
- NO clock calls (fetched_at is always injected by the caller)
- NO network calls (fetcher is always injected by the caller)
- NO LLM, NO API keys
- stdlib only: hashlib, dataclasses
- Fully deterministic: same inputs → same sha256
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Callable

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ACCESS_LEVELS: frozenset[str] = frozenset({
    "full_text",
    "abstract_only",
    "secondary",
})


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Snapshot:
    """Immutable, content-addressed record of the exact text the model reads."""
    url: str
    fetched_at: str        # ISO timestamp, INJECTED (never call the clock here)
    extractor: str         # name of the text-extraction method used
    access_level: str      # "full_text" | "abstract_only" | "secondary"
    sha256: str            # hex digest of `text` (utf-8)
    text: str              # the exact extracted text the model will read


def snapshot(
    url: str,
    *,
    fetcher: Callable[[str], str],
    fetched_at: str,
    extractor: str = "raw",
    access_level: str = "full_text",
) -> Snapshot:
    """
    Build a Snapshot from an injected fetcher and injected timestamp.

    Args:
        url:          The canonical URL of the source.
        fetcher:      Callable[[str], str] — url → extracted text.
                      All network/I/O is the caller's responsibility.
        fetched_at:   ISO timestamp string. Caller provides it; we never
                      call the clock here.
        extractor:    Name of the extraction method (default: "raw").
        access_level: One of VALID_ACCESS_LEVELS. ValueError if not.

    Returns:
        A frozen Snapshot with sha256 computed over the extracted text.
    """
    if access_level not in VALID_ACCESS_LEVELS:
        raise ValueError(
            f"Invalid access_level {access_level!r}. "
            f"Must be one of: {sorted(VALID_ACCESS_LEVELS)}"
        )

    text = fetcher(url)  # any exception propagates to the caller unchanged
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    return Snapshot(
        url=url,
        fetched_at=fetched_at,
        extractor=extractor,
        access_level=access_level,
        sha256=digest,
        text=text,
    )


# ---------------------------------------------------------------------------
# SpanRef
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SpanRef:
    """
    An immutable reference to a substring of a specific Snapshot.

    The text field carries the exact substring for drift-detection:
    if the underlying snapshot is ever re-fetched and the text has changed,
    resolve_span will surface the mismatch immediately.
    """
    sha256: str   # which snapshot this span belongs to
    start: int
    end: int
    text: str     # the exact substring (carried for drift-detection)


def make_span(snap: Snapshot, start: int, end: int) -> SpanRef:
    """
    Create a SpanRef into snap.text[start:end].

    Raises ValueError if:
    - start < 0
    - start >= end  (empty or inverted range)
    - end > len(snap.text)
    """
    n = len(snap.text)
    if start < 0 or start >= end or end > n:
        raise ValueError(
            f"Invalid span [{start}:{end}) for text of length {n}. "
            "Require 0 <= start < end <= len(text)."
        )
    return SpanRef(
        sha256=snap.sha256,
        start=start,
        end=end,
        text=snap.text[start:end],
    )


def passage_span(snap: Snapshot, passage: str | None) -> SpanRef:
    """
    Build the evidence SpanRef for a claim: its supporting passage, located
    in the snapshot text — or the whole document only as a fallback.

    Passage-scoping is doctrine-critical (REVIEW.md KPM-H5): shipping the
    whole document as a claim's span defeats "thin index, rich store" —
    every claim would cite the same document dump instead of the exact
    passage that entailed it.

    Resolution order:
    1. ``passage`` is non-empty and occurs verbatim in ``snap.text`` →
       SpanRef with real offsets (``snap.text[start:end] == passage``).
    2. ``passage`` is missing/empty, or has drifted and no longer occurs
       verbatim → whole-document SpanRef (the legacy fallback; the build
       stays mechanical instead of failing on one drifted passage).
    """
    if passage:
        start = snap.text.find(passage)
        if start != -1:
            return make_span(snap, start, start + len(passage))
    if not snap.text:
        # make_span forbids empty ranges; an empty snapshot still gets a
        # (vacuous) whole-document span so callers need no special case.
        return SpanRef(sha256=snap.sha256, start=0, end=0, text="")
    return make_span(snap, 0, len(snap.text))


def resolve_span(snap: Snapshot, span: SpanRef) -> str:
    """
    Resolve a SpanRef against a Snapshot, with provenance and drift checks.

    Raises ValueError if:
    - span.sha256 != snap.sha256  (span belongs to a different snapshot)
    - start or end are out of range for the current snap.text
    - snap.text[start:end] != span.text  (text has drifted)

    Returns the resolved substring on success.
    """
    if span.sha256 != snap.sha256:
        raise ValueError(
            f"SpanRef sha256 {span.sha256[:12]}… does not match "
            f"Snapshot sha256 {snap.sha256[:12]}…. "
            "This span belongs to a different snapshot."
        )

    n = len(snap.text)
    if span.start < 0 or span.end > n or span.start >= span.end:
        raise ValueError(
            f"Span [{span.start}:{span.end}) is out of range for "
            f"snapshot text of length {n}."
        )

    live_text = snap.text[span.start:span.end]
    if live_text != span.text:
        raise ValueError(
            f"Drift detected: span.text={span.text!r} but "
            f"snap.text[{span.start}:{span.end}]={live_text!r}."
        )

    return live_text
