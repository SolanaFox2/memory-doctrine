"""Tests for the split stage — DETERMINISTIC, no LLM, no API key."""

from package_research.score import ScoredIdea
from package_research.split import (
    AxiomNote,
    EvidenceNote,
    split,
    uncited_sources,
)


def _scored(statement, sources, snippets, *, confidence=0.7, generativity=3):
    return ScoredIdea(
        statement=statement,
        supporting_source_files=list(sources),
        supporting_snippets=list(snippets),
        confidence=confidence,
        generativity=generativity,
        rationale="because snippet",
    )


def test_split_produces_axiom_and_evidence_notes():
    axioms, evidence = split([_scored("Retrieval is pattern completion.", ["alpha.md"], ["pattern completion"])])
    assert len(axioms) == 1
    assert len(evidence) == 1
    assert isinstance(axioms[0], AxiomNote)
    assert isinstance(evidence[0], EvidenceNote)
    assert axioms[0].type == "axiom"
    assert evidence[0].type == "evidence"
    assert axioms[0].status == "candidate"


def test_split_ids_are_stable_slugs():
    axioms, evidence = split([_scored("Confidence is earned from evidence!", ["beta.txt"], ["earned"])])
    # Axiom slug derived deterministically from the statement.
    assert axioms[0].id == "confidence-is-earned-from-evidence"
    # Evidence slug derived from the source filename stem.
    assert evidence[0].id == "beta"


def test_split_dedupes_evidence_by_source():
    # Two distinct axioms both rest on the same source file.
    axioms, evidence = split(
        [
            _scored("Idea one.", ["shared.md"], ["snippet one"]),
            _scored("Idea two.", ["shared.md"], ["snippet two"]),
        ]
    )
    assert len(axioms) == 2
    # Only ONE evidence note for the shared source (the B4 index/store split).
    assert len(evidence) == 1
    shared = evidence[0]
    assert shared.id == "shared"
    # It records that it supports both axioms, and carries both snippets.
    assert set(shared.supports) == {a.id for a in axioms}
    assert "snippet one" in shared.snippets
    assert "snippet two" in shared.snippets


def test_split_every_axiom_evidence_id_resolves():
    axioms, evidence = split(
        [
            _scored("First claim.", ["a.md", "b.md"], ["s1"]),
            _scored("Second claim.", ["b.md", "c.txt"], ["s2"]),
        ]
    )
    evidence_ids = {e.id for e in evidence}
    # The doctrine lint requires every cited evidence id to resolve to a note.
    for ax in axioms:
        assert ax.evidence, f"{ax.id} has no evidence"
        for ev_id in ax.evidence:
            assert ev_id in evidence_ids, f"{ax.id} cites unresolved evidence {ev_id}"
    # b.md is shared, so only 3 distinct evidence notes (a, b, c).
    assert evidence_ids == {"a", "b", "c"}


def test_split_carries_scores_through():
    axioms, _ = split([_scored("Scored claim.", ["x.md"], ["x"], confidence=0.91, generativity=5)])
    assert axioms[0].confidence == 0.91
    assert axioms[0].generativity == 5
    assert axioms[0].rationale == "because snippet"


def test_split_relations_are_empty_doctrine_keys():
    axioms, _ = split([_scored("Claim.", ["x.md"], ["x"])])
    rel = axioms[0].relations
    assert set(rel) == {
        "derives-from",
        "supports",
        "generalizes",
        "contradicts",
        "applies-to-kpm",
    }
    assert all(v == [] for v in rel.values())


def test_split_disambiguates_colliding_axiom_slugs():
    # Two ideas whose statements slugify to the same base get distinct ids.
    axioms, _ = split(
        [
            _scored("Memory is associative.", ["a.md"], ["s"]),
            _scored("Memory is associative.", ["a.md"], ["s"]),
        ]
    )
    ids = [a.id for a in axioms]
    assert len(set(ids)) == 2
    assert ids[0] == "memory-is-associative"
    assert ids[1] == "memory-is-associative-2"


def test_split_is_deterministic_across_runs():
    ideas = [
        _scored("Claim A.", ["one.md"], ["sa"]),
        _scored("Claim B.", ["two.md"], ["sb"]),
    ]
    a1, e1 = split(ideas)
    a2, e2 = split(ideas)
    assert [a.id for a in a1] == [a.id for a in a2]
    assert [e.id for e in e1] == [e.id for e in e2]


def test_split_empty_input_returns_empty():
    axioms, evidence = split([])
    assert axioms == []
    assert evidence == []


def test_split_evidence_body_renders_snippets():
    _, evidence = split([_scored("Claim.", ["src.md"], ["first snippet", "second snippet"])])
    body = evidence[0].body
    assert "first snippet" in body
    assert "second snippet" in body


# --- rich store: source_passages enrichment (keep details, not just headlines) ---


def test_split_enriches_evidence_body_with_source_passages():
    """When given the source passages, the evidence body holds the full content,
    not only the one line the axiom quoted."""
    scored = [_scored("Memory is not long context.", ["decay.md"], ["not long context"])]
    passages = {
        "decay.md": [
            "## Findings\n\nLoCoMo, LongMemEval, and BEAM are the standard benchmarks.",
            "## Scores\n\nMem0 reports 91.6 on LoCoMo; AMA-Bench shows design beats scale.",
        ]
    }
    axioms, evidence = split(scored, passages)
    body = evidence[0].body
    # The benchmark names that the thin snippet dropped are now preserved.
    assert "LoCoMo" in body and "BEAM" in body and "AMA-Bench" in body


def test_split_without_passages_falls_back_to_cited_snippet():
    """No map -> original behaviour: body is the cited snippet (backward compat)."""
    scored = [_scored("Memory is not long context.", ["decay.md"], ["not long context"])]
    axioms, evidence = split(scored)
    assert evidence[0].body == "not long context"


def test_split_uses_snippet_when_source_absent_from_map():
    """A cited source missing from the map keeps its snippet (no crash, no loss)."""
    scored = [_scored("X is true.", ["present.md", "missing.md"], ["snip"])]
    passages = {"present.md": ["## Detail\n\nrich preserved content"]}
    axioms, evidence = split(scored, passages)
    by_ref = {n.ref: n.body for n in evidence}
    assert "rich preserved content" in by_ref["present.md"]
    assert by_ref["missing.md"] == "snip"  # fell back to the cited snippet


def test_split_does_not_cross_contaminate_same_basename():
    """Two cited sources sharing a basename must keep their OWN preserved
    content — never each other's (reviewer Important finding)."""
    scored = [
        _scored("Claim from 2025.", ["2025/notes.md"], ["snip25"]),
        _scored("Claim from 2026.", ["2026/notes.md"], ["snip26"]),
    ]
    passages = {
        "2025/notes.md": ["## A\n\nrich 2025 content"],
        "2026/notes.md": ["## A\n\nrich 2026 content"],
    }
    axioms, evidence = split(scored, passages)
    by_ref = {n.ref: n.body for n in evidence}
    assert "rich 2025 content" in by_ref["2025/notes.md"]
    assert "rich 2026 content" in by_ref["2026/notes.md"]
    assert "2026" not in by_ref["2025/notes.md"]  # no cross-contamination


def test_split_basename_fallback_when_unambiguous():
    """An axiom that cites a bare filename still gets the preserved content when
    the basename maps to exactly one ingested path."""
    scored = [_scored("Claim.", ["notes.md"], ["snip"])]
    passages = {"sub/notes.md": ["## D\n\npreserved nested content"]}
    axioms, evidence = split(scored, passages)
    assert "preserved nested content" in evidence[0].body


def test_split_distinct_sources_with_colliding_slug_get_distinct_notes():
    """`a/b.md` and `a-b.md` slugify to the same base (`a-b`); they must still
    become two distinct evidence notes, not silently merge (reviewer Critical)."""
    scored = [
        _scored("Claim one.", ["a/b.md"], ["snip-one"]),
        _scored("Claim two.", ["a-b.md"], ["snip-two"]),
    ]
    axioms, evidence = split(scored)
    refs = sorted(n.ref for n in evidence)
    ids = sorted(n.id for n in evidence)
    assert refs == ["a-b.md", "a/b.md"]  # both sources preserved as notes
    assert len(set(ids)) == 2  # ids disambiguated, not collided
    # Each axiom cites its own source's note (no cross-wiring).
    cited = {a.statement: a.evidence for a in axioms}
    assert cited["Claim one."] != cited["Claim two."]


def test_split_same_source_twice_still_dedupes_to_one_note():
    """Two axioms citing the SAME source share ONE evidence note (dedup intact)."""
    scored = [
        _scored("First claim.", ["s.md"], ["a"]),
        _scored("Second claim.", ["s.md"], ["b"]),
    ]
    axioms, evidence = split(scored)
    assert len([n for n in evidence if n.ref == "s.md"]) == 1


def test_split_id_disambiguator_is_collision_proof_against_dash_two_slug():
    """Even a source whose natural slug ends in '-2' cannot collide with the
    disambiguator's own '-2' suffix — ids stay unique (iron-clad)."""
    scored = [
        _scored("Claim A.", ["x/y.md"], ["a"]),  # slug -> x-y
        _scored("Claim B.", ["x-y.md"], ["b"]),  # slug -> x-y  => x-y-2
        _scored("Claim C.", ["x-y-2.md"], ["c"]),  # natural slug -> x-y-2 (would clash)
    ]
    axioms, evidence = split(scored)
    ids = [n.ref for n in evidence]
    assert len(ids) == 3  # three distinct notes
    assert len({n.id for n in evidence}) == 3  # three distinct ids, no merge


def test_uncited_sources_flags_files_no_axiom_cited():
    # One cited source, two uncited (one empty -> excluded).
    scored = [_scored("Cited claim.", ["a.md"], ["snip"])]
    _, evidence = split(scored)
    pbs = {
        "a.md": ["## A\n\ncited content"],
        "b.md": ["## B\n\nuncited but real content"],
        "c.md": ["   ", ""],  # only whitespace -> not counted
    }
    out = uncited_sources(pbs, evidence)
    assert set(out) == {"b.md"}
    assert "uncited but real content" in out["b.md"][0]


def test_uncited_sources_matches_by_basename():
    # Agent cited bare "a.md"; ingest keyed "sub/a.md" -> still counts as cited.
    scored = [_scored("Cited.", ["a.md"], ["s"])]
    _, evidence = split(scored)
    pbs = {"sub/a.md": ["content"], "other.md": ["x"]}
    out = uncited_sources(pbs, evidence)
    assert set(out) == {"other.md"}


def test_uncited_sources_ambiguous_basename_not_absorbed():
    # Two sources share basename "notes.md"; only 2025/notes.md was cited by
    # full path. The bare-basename ambiguity must not silently mark 2026/notes.md
    # as cited — it should be surfaced as uncited.
    scored = [_scored("Cited.", ["2025/notes.md"], ["s"])]
    _, evidence = split(scored)
    pbs = {"2025/notes.md": ["a"], "2026/notes.md": ["uncited content"]}
    out = uncited_sources(pbs, evidence)
    assert set(out) == {"2026/notes.md"}
    assert "uncited content" in out["2026/notes.md"][0]
