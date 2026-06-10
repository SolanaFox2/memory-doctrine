"""Tests for kpm_builder.refute — written BEFORE implementation (TDD).

All tests use a FAKE complete_json; no real LLM API is called.

The load-bearing invariant tested here: the refuter must NEVER see the claim's
own supporting passage.  Independence is the whole point of the module.
"""

from __future__ import annotations

import pytest
from kpm_builder.refute import RefuteResult, refute


# ── helpers ────────────────────────────────────────────────────────────────────

def make_fake(response: dict):
    """Return a complete_json callable that always returns *response*."""
    def _fake(prompt: str, schema: dict) -> dict:
        return response
    return _fake


def capturing_fake(response: dict):
    """Return a complete_json callable that records the prompt it receives."""
    captured: list[str] = []

    def _fake(prompt: str, schema: dict) -> dict:
        captured.append(prompt)
        return response

    _fake.captured = captured  # type: ignore[attr-defined]
    return _fake


CLAIM = "Neural scaling laws hold universally across all architectures."
OWN_SUPPORT = "Scaling laws were shown to hold for transformer models in Kaplan et al. 2020."
CORPUS = [
    OWN_SUPPORT,
    "Recurrent architectures show diminishing returns after certain parameter counts.",
    "State-space models exhibit different scaling behaviour than transformers.",
]


# ── planted defeater ───────────────────────────────────────────────────────────

def test_planted_defeater_is_refuted():
    """A fake that returns refuted=True must produce RefuteResult(refuted=True)."""
    fake = make_fake({
        "refuted": True,
        "counter": "Recurrent architectures show diminishing returns.",
        "reason": "Claim universalises to all architectures; corpus contradicts this.",
    })
    result = refute(CLAIM, OWN_SUPPORT, CORPUS, complete_json=fake)
    assert isinstance(result, RefuteResult)
    assert result.refuted is True
    assert result.counter != ""


# ── clean corpus ───────────────────────────────────────────────────────────────

def test_clean_corpus_not_refuted():
    """A fake that returns refuted=False must produce RefuteResult(refuted=False)."""
    fake = make_fake({
        "refuted": False,
        "counter": "",
        "reason": "No contradiction found in the independent passages.",
    })
    result = refute(CLAIM, OWN_SUPPORT, CORPUS, complete_json=fake)
    assert result.refuted is False


# ── defensive: missing keys in response ───────────────────────────────────────

def test_empty_dict_response_defaults_to_not_refuted():
    """An empty dict from the judge must not raise; refuted defaults to False."""
    fake = make_fake({})
    result = refute(CLAIM, OWN_SUPPORT, CORPUS, complete_json=fake)
    assert isinstance(result, RefuteResult)
    assert result.refuted is False
    assert isinstance(result.counter, str)
    assert isinstance(result.reason, str)


# ── INDEPENDENCE: the load-bearing test ───────────────────────────────────────

def test_own_support_excluded_from_prompt():
    """The prompt passed to the judge must NOT contain own_support.

    The refuter's whole purpose is adversarial independence.  Showing the
    judge the claim's own supporting passage would make this circular.
    """
    fake = capturing_fake({
        "refuted": False,
        "counter": "",
        "reason": "nothing found",
    })
    refute(
        claim=CLAIM,
        own_support=OWN_SUPPORT,
        corpus=[
            OWN_SUPPORT,
            "other passage A",
            "other passage B",
        ],
        complete_json=fake,
    )
    assert fake.captured, "complete_json was never called"
    prompt = fake.captured[0]

    # Independent passages MUST be present
    assert "other passage A" in prompt
    assert "other passage B" in prompt

    # Own support must NOT appear anywhere in the prompt
    assert OWN_SUPPORT not in prompt


# ── corpus that is ONLY the own_support ───────────────────────────────────────

def test_corpus_only_own_support_short_circuits_or_calls_judge_with_no_passages():
    """When independent set is empty, refuted must be False (no evidence to cite).

    The implementation may either short-circuit without calling the judge, or
    call the judge with an empty passage list.  Either is valid; what must NOT
    happen is a crash or a spurious refuted=True.
    """
    call_count = [0]

    def counting_fake(prompt: str, schema: dict) -> dict:
        call_count[0] += 1
        # Return refuted=True to catch the case where the judge is called
        # erroneously with the own_support visible — this test asserts the
        # result is still False regardless.
        return {"refuted": True, "counter": "should not happen", "reason": "n/a"}

    result = refute(
        claim=CLAIM,
        own_support=OWN_SUPPORT,
        corpus=[OWN_SUPPORT],   # only the own_support, no independent passages
        complete_json=counting_fake,
    )
    assert result.refuted is False
