"""Tests for kpm_builder.ground — the engine's entailment grounder.

TDD: tests written before implementation. Uses only fake complete_json callables;
no real LLM or network calls.
"""

from __future__ import annotations
import pytest
from kpm_builder.snapshot import snapshot as make_snapshot
from kpm_builder.ground import GroundResult, ground


# ── fixtures ──────────────────────────────────────────────────────────────────

SOURCE_TEXT = "The system processed 42 requests in the trial period."
CLAIM = "The system is always fast."

# Build a small Snapshot using the factory with an injected fetcher — no network.
SNAP = make_snapshot(
    "https://example.com/paper",
    fetcher=lambda u: SOURCE_TEXT,
    fetched_at="2026-01-01",
)


def make_fake(response: dict):
    """Return a complete_json callable that always returns *response*."""
    def _fake(prompt: str, schema: dict) -> dict:
        return response
    return _fake


# ── verdict routing ────────────────────────────────────────────────────────────

def test_over_claims_verdict():
    fake = make_fake({
        "verdict": "over_claims",
        "supported_paraphrase": "The system processed 42 requests in the trial.",
        "dropped": ["universalised"],
        "reason": "Claim universalizes a bounded benchmark result.",
    })
    result = ground(CLAIM, SNAP, complete_json=fake)
    assert isinstance(result, GroundResult)
    assert result.verdict == "over_claims"
    assert result.dropped == ["universalised"]


def test_entails_verdict():
    fake = make_fake({
        "verdict": "entails",
        "supported_paraphrase": "x",
        "dropped": [],
        "reason": "Claim faithfully paraphrases the source.",
    })
    result = ground(CLAIM, SNAP, complete_json=fake)
    assert isinstance(result, GroundResult)
    assert result.verdict == "entails"
    assert result.supported_paraphrase == "x"
    assert result.dropped == []


def test_reject_verdict():
    fake = make_fake({
        "verdict": "reject",
        "supported_paraphrase": "",
        "dropped": [],
        "reason": "No relevant support.",
    })
    result = ground(CLAIM, SNAP, complete_json=fake)
    assert result.verdict == "reject"


# ── coercion / defensive parsing ──────────────────────────────────────────────

def test_empty_dict_coerced_to_reject():
    """Empty dict → verdict coerced to 'reject'."""
    fake = make_fake({})
    result = ground(CLAIM, SNAP, complete_json=fake)
    assert result.verdict == "reject"


def test_bogus_verdict_coerced_to_reject():
    """An unrecognised verdict string must be coerced to 'reject'."""
    fake = make_fake({"verdict": "bogus", "dropped": [], "reason": "n/a", "supported_paraphrase": ""})
    result = ground(CLAIM, SNAP, complete_json=fake)
    assert result.verdict == "reject"


def test_dropped_non_list_coerced_to_empty_list():
    """If 'dropped' is not a list (e.g. a string), it must be coerced to []."""
    fake = make_fake({
        "verdict": "over_claims",
        "supported_paraphrase": "",
        "dropped": "not a list",
        "reason": "something",
    })
    result = ground(CLAIM, SNAP, complete_json=fake)
    assert result.dropped == []


def test_missing_optional_fields_get_safe_defaults():
    """Partial response (only verdict) must not raise; missing fields get defaults."""
    fake = make_fake({"verdict": "entails"})
    result = ground(CLAIM, SNAP, complete_json=fake)
    assert result.verdict == "entails"
    assert isinstance(result.supported_paraphrase, str)
    assert isinstance(result.dropped, list)
    assert isinstance(result.reason, str)


# ── prompt content ─────────────────────────────────────────────────────────────

def test_prompt_contains_claim_and_snapshot_text():
    """The prompt must contain the claim AND the snapshot's text."""
    captured: list[str] = []

    def capturing_fake(prompt: str, schema: dict) -> dict:
        captured.append(prompt)
        return {
            "verdict": "entails",
            "supported_paraphrase": "",
            "dropped": [],
            "reason": "",
        }

    ground(CLAIM, SNAP, complete_json=capturing_fake)
    assert len(captured) == 1
    prompt = captured[0]
    assert CLAIM in prompt
    assert SOURCE_TEXT in prompt  # snapshot.text must appear


def test_prompt_does_not_contain_reasoning_field():
    """Prompt must NOT pass any drafter reasoning — only claim + source text."""
    captured: list[str] = []

    def capturing_fake(prompt: str, schema: dict) -> dict:
        captured.append(prompt)
        return {"verdict": "entails", "supported_paraphrase": "", "dropped": [], "reason": ""}

    ground(CLAIM, SNAP, complete_json=capturing_fake)
    prompt = captured[0]
    # "reasoning" is the word we're guarding against leaking in
    assert "reasoning" not in prompt.lower()
