"""Tests for the score stage — LLM mocked, NO API key required."""

from package_research.distill import Idea
from package_research.score import (
    SCORE_SCHEMA,
    ScoredIdea,
    build_prompt,
    score,
    score_idea,
)


def _fake_complete_json(payload):
    """Return a (prompt, schema)->dict callable that records its calls."""
    calls = {"count": 0}

    def _inner(prompt, schema):
        calls["count"] += 1
        calls["prompt"] = prompt
        calls["schema"] = schema
        return payload

    _inner.calls = calls
    return _inner


def _idea(statement="Confidence is earned from evidence."):
    return Idea(
        statement=statement,
        supporting_source_files=["alpha.md"],
        supporting_snippets=["confidence is earned from evidence"],
    )


def test_score_parses_scored_idea_from_mocked_llm():
    fake = _fake_complete_json({"confidence": 0.82, "generativity": 4, "rationale": "Two snippets converge."})
    scored = score_idea(_idea(), fake)
    assert isinstance(scored, ScoredIdea)
    assert scored.confidence == 0.82
    assert scored.generativity == 4
    assert scored.rationale == "Two snippets converge."
    # Idea fields carried through unchanged.
    assert scored.statement == "Confidence is earned from evidence."
    assert scored.supporting_source_files == ["alpha.md"]
    assert scored.supporting_snippets == ["confidence is earned from evidence"]


def test_score_passes_schema_to_llm():
    fake = _fake_complete_json({"confidence": 0.5, "generativity": 3, "rationale": ""})
    score_idea(_idea(), fake)
    assert fake.calls["schema"] == SCORE_SCHEMA


def test_score_prompt_embeds_c1_rubric_and_idea():
    prompt = build_prompt(_idea("A real generator claim."))
    # Doctrine C1 rubric is embedded.
    assert "earned from evidence" in prompt
    assert "never from fluency" in prompt
    # The idea + its snippet are rendered into the prompt.
    assert "A real generator claim." in prompt
    assert "confidence is earned from evidence" in prompt


def test_score_clamps_confidence_out_of_bounds():
    high = _fake_complete_json({"confidence": 1.7, "generativity": 3, "rationale": ""})
    low = _fake_complete_json({"confidence": -0.4, "generativity": 3, "rationale": ""})
    assert score_idea(_idea(), high).confidence == 1.0
    assert score_idea(_idea(), low).confidence == 0.0


def test_score_clamps_generativity_out_of_bounds():
    big = _fake_complete_json({"confidence": 0.5, "generativity": 9, "rationale": ""})
    small = _fake_complete_json({"confidence": 0.5, "generativity": 0, "rationale": ""})
    assert score_idea(_idea(), big).generativity == 5
    assert score_idea(_idea(), small).generativity == 1


def test_score_bounds_always_valid_for_doctrine_lint():
    # Even garbage from the model yields lint-valid bounds.
    fake = _fake_complete_json({"confidence": "not-a-number", "generativity": "x", "rationale": None})
    scored = score_idea(_idea(), fake)
    assert 0.0 <= scored.confidence <= 1.0
    assert scored.generativity in (1, 2, 3, 4, 5)
    assert scored.rationale == ""


def test_score_iterates_all_ideas_in_order():
    fake = _fake_complete_json({"confidence": 0.6, "generativity": 2, "rationale": "ok"})
    ideas = [_idea("First."), _idea("Second."), _idea("Third.")]
    scored = score(ideas, fake)
    assert [s.statement for s in scored] == ["First.", "Second.", "Third."]
    assert fake.calls["count"] == 3
    assert all(isinstance(s, ScoredIdea) for s in scored)
