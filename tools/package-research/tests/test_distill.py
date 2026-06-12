"""Tests for the distill stage — LLM mocked, NO API key required."""

import pytest

from package_research.config import Config
from package_research.distill import (
    DISTILL_SCHEMA,
    Idea,
    build_prompt,
    distill,
)
from package_research.ingest import Candidate, ingest


def _fake_complete_json(payload):
    """Return a (prompt, schema)->dict callable that records its call."""
    calls = {}

    def _inner(prompt, schema):
        calls["prompt"] = prompt
        calls["schema"] = schema
        return payload

    _inner.calls = calls
    return _inner


def test_distill_parses_ideas_from_mocked_llm(notes_dir):
    cands = ingest(Config(input_dir=notes_dir))
    fake = _fake_complete_json(
        {
            "ideas": [
                {
                    "statement": "Retrieval is energy-descent pattern completion.",
                    "supporting_source_files": ["alpha.md"],
                    "supporting_snippets": ["energy-descent pattern completion"],
                },
                {
                    "statement": "Confidence is earned by evidence.",
                    "supporting_source_files": ["beta.txt"],
                    "supporting_snippets": ["Confidence is earned by evidence"],
                },
            ]
        }
    )
    ideas = distill(cands, fake)
    assert len(ideas) == 2
    assert all(isinstance(i, Idea) for i in ideas)
    assert ideas[0].supporting_source_files == ["alpha.md"]
    assert ideas[0].supporting_snippets


def test_distill_passes_schema_to_llm(notes_dir):
    cands = ingest(Config(input_dir=notes_dir))
    fake = _fake_complete_json({"ideas": []})
    distill(cands, fake)
    assert fake.calls["schema"] == DISTILL_SCHEMA


def test_distill_prompt_embeds_doctrine_and_candidates(notes_dir):
    cands = ingest(Config(input_dir=notes_dir))
    prompt = build_prompt(cands)
    # Doctrine E1 rubric is embedded.
    assert "generators, not the notes" in prompt
    assert "One idea per node" in prompt
    # Candidate source attribution is rendered into the prompt.
    assert "source_file: alpha.md" in prompt


def test_distill_dedupes_identical_statements():
    cands = [
        Candidate(text="x", source_file="a.md", char_span=(0, 1)),
    ]
    fake = _fake_complete_json(
        {
            "ideas": [
                {
                    "statement": "Confidence is earned.",
                    "supporting_source_files": ["a.md"],
                    "supporting_snippets": ["earned"],
                },
                {
                    "statement": "confidence is earned.",  # dup (case/space)
                    "supporting_source_files": ["b.md"],
                    "supporting_snippets": ["earned by evidence"],
                },
            ]
        }
    )
    ideas = distill(cands, fake)
    assert len(ideas) == 1
    # Support is unioned across the merged duplicates.
    assert set(ideas[0].supporting_source_files) == {"a.md", "b.md"}
    assert len(ideas[0].supporting_snippets) == 2


def test_distill_drops_empty_statements():
    cands = [Candidate(text="x", source_file="a.md", char_span=(0, 1))]
    fake = _fake_complete_json(
        {
            "ideas": [
                {"statement": "   ", "supporting_source_files": [], "supporting_snippets": []},
                {
                    "statement": "A real generator.",
                    "supporting_source_files": ["a.md"],
                    "supporting_snippets": ["x"],
                },
            ]
        }
    )
    ideas = distill(cands, fake)
    assert [i.statement for i in ideas] == ["A real generator."]


def test_distill_empty_candidates_returns_empty_without_calling_llm():
    def _boom(prompt, schema):  # must NOT be called
        raise AssertionError("LLM should not be invoked for empty candidates")

    assert distill([], _boom) == []


def test_render_candidates_keeps_full_relative_path():
    """Provenance must use the full relative path, not just the basename, so
    nested notes are cited precisely (parity with skill mode)."""
    cands = [Candidate(text="x", source_file="sub/gamma.md", char_span=(0, 1))]
    prompt = build_prompt(cands)
    assert "sub/gamma.md" in prompt


def test_distill_batches_large_candidate_sets():
    """100 candidates at batch_size=40 -> 3 calls, ideas unioned across batches."""
    cands = [Candidate(text=f"t{i}", source_file=f"n{i}.md", char_span=(0, 2)) for i in range(100)]
    calls = []

    def fake(prompt, schema):
        calls.append(prompt)
        n = len(calls)
        return {
            "ideas": [
                {
                    "statement": f"Idea from batch {n}.",
                    "supporting_source_files": [f"n{n}.md"],
                    "supporting_snippets": [f"s{n}"],
                },
                {  # identical statement in every batch: support must union
                    "statement": "Shared idea.",
                    "supporting_source_files": [f"n{n}.md"],
                    "supporting_snippets": [],
                },
            ]
        }

    ideas = distill(cands, fake, batch_size=40)
    assert len(calls) == 3
    # Each batch's candidates appear only in its own prompt.
    assert "n0.md" in calls[0] and "n0.md" not in calls[1]
    assert "n40.md" in calls[1] and "n99.md" in calls[2]
    shared = next(i for i in ideas if i.statement == "Shared idea.")
    assert shared.supporting_source_files == ["n1.md", "n2.md", "n3.md"]
    assert len(ideas) == 4  # 3 per-batch ideas + 1 merged shared idea


def test_distill_single_batch_when_under_batch_size():
    cands = [Candidate(text="x", source_file="a.md", char_span=(0, 1))]
    calls = []

    def fake(prompt, schema):
        calls.append(prompt)
        return {"ideas": []}

    distill(cands, fake, batch_size=40)
    assert len(calls) == 1


def test_distill_rejects_nonpositive_batch_size():
    cands = [Candidate(text="x", source_file="a.md", char_span=(0, 1))]
    with pytest.raises(ValueError):
        distill(cands, lambda p, s: {"ideas": []}, batch_size=0)
