"""Tests for the verify stage — LLM mocked, NO API key required."""

from package_research.score import ScoredIdea
from package_research.verify import (
    VERIFY_SCHEMA,
    VerificationResult,
    build_prompt,
    has_citation,
    verify,
    verify_idea,
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


def _scored(
    statement="Retrieval is pattern completion.", snippets=("pattern completion",), confidence=0.8, generativity=4
):
    return ScoredIdea(
        statement=statement,
        supporting_source_files=["alpha.md"],
        supporting_snippets=list(snippets),
        confidence=confidence,
        generativity=generativity,
        rationale="snippet supports it",
    )


def test_verify_idea_survives_when_model_keeps_it():
    fake = _fake_complete_json({"survives": True, "reason": "snippet establishes it", "adjusted_confidence": 0.7})
    res = verify_idea(_scored(confidence=0.8), fake)
    assert isinstance(res, VerificationResult)
    assert res.survived is True
    assert res.has_citation is True
    # Down-scored to what the evidence licenses (<= prior).
    assert res.adjusted_confidence == 0.7


def test_verify_idea_refuted_when_model_rejects_it():
    fake = _fake_complete_json(
        {"survives": False, "reason": "snippet only restates the claim", "adjusted_confidence": 0.1}
    )
    res = verify_idea(_scored(), fake)
    assert res.survived is False
    assert res.has_citation is True


def test_verify_citation_presence_drops_idea_with_no_snippet():
    # No LLM call should be needed — citation-presence fails first.
    fake = _fake_complete_json({"survives": True, "reason": "x", "adjusted_confidence": 0.9})
    idea = _scored(snippets=())  # no supporting snippet
    res = verify_idea(idea, fake)
    assert res.has_citation is False
    assert res.survived is False
    assert fake.calls["count"] == 0  # LLM was never called


def test_verify_citation_presence_ignores_whitespace_only_snippet():
    idea = _scored(snippets=("   ", "\n"))
    assert has_citation(idea) is False


def test_verify_never_raises_confidence_above_prior():
    # Model tries to RAISE confidence; verify must cap at the prior.
    fake = _fake_complete_json({"survives": True, "reason": "ok", "adjusted_confidence": 0.99})
    res = verify_idea(_scored(confidence=0.6), fake)
    assert res.adjusted_confidence == 0.6


def test_verify_drops_refuted_and_uncited_keeps_survivors():
    survive = _fake_complete_json({"survives": True, "reason": "ok", "adjusted_confidence": 0.5})
    # Three ideas: one survives, one refuted (use a per-idea router).
    ideas = [
        _scored("Survivor claim.", snippets=("real snippet",), confidence=0.8),
        _scored("Refuted claim.", snippets=("weak snippet",), confidence=0.8),
        _scored("Uncited claim.", snippets=(), confidence=0.8),
    ]

    def router(prompt, schema):
        if "Refuted claim." in prompt:
            return {"survives": False, "reason": "no", "adjusted_confidence": 0.1}
        return {"survives": True, "reason": "yes", "adjusted_confidence": 0.5}

    survivors = verify(ideas, router)
    statements = [s.statement for s in survivors]
    assert statements == ["Survivor claim."]
    assert survivors[0].confidence == 0.5  # down-scored
    # Original fields preserved.
    assert survivors[0].generativity == 4
    assert survivors[0].supporting_snippets == ["real snippet"]
    # Unused: the lone survive-fake is here only to exercise the helper above.
    _ = survive


def test_verify_passes_schema_to_llm():
    fake = _fake_complete_json({"survives": True, "reason": "ok", "adjusted_confidence": 0.5})
    verify_idea(_scored(), fake)
    assert fake.calls["schema"] == VERIFY_SCHEMA


def test_verify_prompt_embeds_e4_rubric_and_idea():
    prompt = build_prompt(_scored("A refutable claim."))
    assert "refute by default" in prompt.lower()
    assert "citation presence" in prompt.lower()
    assert "A refutable claim." in prompt
    assert "pattern completion" in prompt


def test_verify_tolerates_non_dict_result():
    fake = _fake_complete_json(["not", "a", "dict"])
    res = verify_idea(_scored(confidence=0.8), fake)
    # Non-dict => survives falsy, dropped; no crash.
    assert res.survived is False


def test_verify_empty_input_returns_empty():
    fake = _fake_complete_json({"survives": True, "reason": "", "adjusted_confidence": 0.5})
    assert verify([], fake) == []
