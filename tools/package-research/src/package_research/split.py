"""Split stage — DETERMINISTIC (doctrine B4: index / store split).

Turns scored ideas into two cross-linked sets of in-memory note objects that
mirror the Memory Doctrine's on-disk schema:

* **axiom notes** — the *index*: thin, navigable claims carrying the scores and
  the ids of the evidence they cite.
* **evidence notes** — the *store*: one note per distinct source, holding the
  verbatim snippet(s). Multiple axioms that rest on the same source share a
  single evidence note (de-duplication by source) — this *is* the B4 split.

Nothing is written to disk here (that is the assemble stage, M3). Ids are
generated deterministically via stable slugs so the same input always yields the
same ids, and **every axiom's ``evidence`` id is guaranteed to resolve** to an
emitted evidence note (the doctrine lint requires this downstream).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .score import ScoredIdea

# Relation keys the doctrine schema expects on every axiom note (empty for now).
_RELATION_KEYS = (
    "derives-from",
    "supports",
    "generalizes",
    "contradicts",
    "applies-to-kpm",
)

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def _slugify(text: str, *, max_words: int = 8) -> str:
    """Lowercase, hyphenate, strip punctuation; keep the first ``max_words``.

    Deterministic: identical input always produces an identical slug.
    """
    cleaned = _SLUG_STRIP.sub("-", text.lower()).strip("-")
    if not cleaned:
        return "note"
    words = [w for w in cleaned.split("-") if w]
    return "-".join(words[:max_words]) or "note"


def _evidence_slug(source: str) -> str:
    """Stable evidence id derived from a source's full relative path (no suffix).

    Uses the whole relative path — not just the basename stem — so two sources
    that share a filename in different folders (``2025/notes.md`` vs
    ``2026/notes.md``) get distinct evidence ids (``2025-notes`` / ``2026-notes``)
    and never merge into one note. Flat single-folder sources are unaffected
    (``decay-benchmarks-2026.md`` → ``decay-benchmarks-2026``).
    """
    rel = Path(source).with_suffix("").as_posix() or source
    return _slugify(rel, max_words=12)


def _title_from_statement(statement: str) -> str:
    """A short human title: the statement's first clause, trimmed."""
    head = re.split(r"[.;:]", statement.strip(), maxsplit=1)[0].strip()
    return head or statement.strip()


@dataclass
class AxiomNote:
    """The index node: a thin claim carrying scores + cited evidence ids."""

    id: str
    type: str
    title: str
    statement: str
    confidence: float
    generativity: int
    status: str
    relations: Dict[str, List[str]]
    evidence: List[str]
    provenance: str
    rationale: str = ""


@dataclass
class EvidenceNote:
    """The store node: one per distinct source, holding the snippet(s)."""

    id: str
    type: str
    ref: str
    supports: List[str] = field(default_factory=list)
    snippets: List[str] = field(default_factory=list)

    @property
    def body(self) -> str:
        """The snippet(s) rendered as the note body."""
        return "\n\n".join(s.strip() for s in self.snippets if s.strip())


def _empty_relations() -> Dict[str, List[str]]:
    return {k: [] for k in _RELATION_KEYS}


def _ordered_union(values: List[str]) -> List[str]:
    seen: Dict[str, None] = {}
    for v in values:
        if v not in seen:
            seen[v] = None
    return list(seen)


def _unique_id(base: str, used: set) -> str:
    """Return a unique id from ``base``, disambiguating with -2, -3, ...

    Used for BOTH axiom and evidence ids. ``used`` is the set of ids already
    emitted; the returned id is added to it. Checking the *final* candidate
    against ``used`` (not a per-base counter) makes collisions impossible even in
    the pathological case where a natural slug already ends in ``-2`` — so two
    distinct sources never share a note even when their slugs collide
    (``a/b.md`` and ``a-b.md`` both slugify to ``a-b``).
    """
    candidate = base
    n = 1
    while candidate in used:
        n += 1
        candidate = f"{base}-{n}"
    used.add(candidate)
    return candidate


def uncited_sources(
    source_passages: Dict[str, List[str]],
    evidence_notes: List[EvidenceNote],
) -> Dict[str, List[str]]:
    """Return the sources that have content but no evidence note cites them.

    A file is "represented" if some emitted evidence note's ``ref`` shares its
    basename (agents cite bare filenames; ingest keys by relative path). Returns
    ``{source: [passage, ...]}`` only for sources with non-empty content — the
    material that would otherwise be silently dropped from the package.
    """
    cited = {Path(n.ref).name for n in evidence_notes}
    out: Dict[str, List[str]] = {}
    for src, passages in source_passages.items():
        if Path(src).name in cited:
            continue
        kept = [p for p in passages if p.strip()]
        if kept:
            out[src] = kept
    return out


def split(
    scored_ideas: List[ScoredIdea],
    source_passages: Optional[Dict[str, List[str]]] = None,
) -> Tuple[List[AxiomNote], List[EvidenceNote]]:
    """Build axiom (index) + evidence (store) notes from scored ideas.

    Returns ``(axiom_notes, evidence_notes)``. Evidence is de-duplicated by
    source so shared sources become one note. Every id in an axiom's
    ``evidence`` list is guaranteed to resolve to an emitted evidence note.

    ``source_passages`` (``{filename: [passage, ...]}``, from
    :func:`ingest.passages_by_source`) makes the store **rich**: when a cited
    source appears in the map, its evidence note body becomes the preserved
    source passages — not just the one line an axiom quoted — so the package
    keeps the details, not only the headlines. Sources absent from the map fall
    back to the cited snippets, so the function still works with no map at all.
    """
    evidence_by_id: Dict[str, EvidenceNote] = {}
    axiom_notes: List[AxiomNote] = []
    taken_axiom_ids: set = set()
    taken_ev_ids: set = set()
    source_to_ev_id: Dict[str, str] = {}  # same source -> same id (dedup)

    for idea in scored_ideas:
        axiom_id = _unique_id(_slugify(idea.statement), taken_axiom_ids)

        # Collect the distinct sources this idea rests on, in stable order.
        sources = _ordered_union(list(idea.supporting_source_files))

        cited_ev_ids: List[str] = []
        for source in sources:
            # One id per distinct source; colliding slugs get disambiguated, so
            # different sources never merge into one note.
            ev_id = source_to_ev_id.get(source)
            if ev_id is None:
                ev_id = _unique_id(_evidence_slug(source), taken_ev_ids)
                source_to_ev_id[source] = ev_id
            note = evidence_by_id.get(ev_id)
            if note is None:
                note = EvidenceNote(
                    id=ev_id,
                    type="evidence",
                    ref=source,
                    supports=[],
                    snippets=[],
                )
                evidence_by_id[ev_id] = note
            if axiom_id not in note.supports:
                note.supports.append(axiom_id)
            # Attach this idea's snippets to every source it cited.
            for snip in idea.supporting_snippets:
                if snip not in note.snippets:
                    note.snippets.append(snip)
            if ev_id not in cited_ev_ids:
                cited_ev_ids.append(ev_id)

        axiom_notes.append(
            AxiomNote(
                id=axiom_id,
                type="axiom",
                title=_title_from_statement(idea.statement),
                statement=idea.statement.strip(),
                confidence=idea.confidence,
                generativity=idea.generativity,
                status="candidate",
                relations=_empty_relations(),
                evidence=cited_ev_ids,
                provenance="package-research/distilled",
                rationale=idea.rationale,
            )
        )

    evidence_notes = list(evidence_by_id.values())
    if source_passages:
        _enrich_evidence_bodies(evidence_notes, source_passages)
    return axiom_notes, evidence_notes


def _enrich_evidence_bodies(evidence_notes: List[EvidenceNote], source_passages: Dict[str, List[str]]) -> None:
    """Replace each evidence note's cited-snippet body with the preserved source
    passages where we have them, so the package keeps the details (B4 store).

    Mutates ``evidence_notes`` in place. A note is matched to its passages by
    exact ``ref`` first, then by an *unambiguous*-basename fallback (an axiom may
    cite a bare filename while ingest keyed the source by a relative path);
    colliding basenames are skipped so distinct sources never cross-contaminate.
    """
    by_basename: Dict[str, str] = {}
    ambiguous: set = set()
    for key in source_passages:
        base = Path(key).name
        if base in by_basename and by_basename[base] != key:
            ambiguous.add(base)
        by_basename[base] = key

    for note in evidence_notes:
        preserved = source_passages.get(note.ref)
        if preserved is None:
            base = Path(note.ref).name
            if base not in ambiguous:
                mapped = by_basename.get(base)
                if mapped is not None:
                    preserved = source_passages.get(mapped)
        # Only swap in a non-empty body; otherwise keep the cited snippet.
        if preserved and any(p.strip() for p in preserved):
            note.snippets = list(preserved)
