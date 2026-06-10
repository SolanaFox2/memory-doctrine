"""Tests for kpm_builder.providers — multi-provider LLM seam.

TDD: tests written before implementation.  No real LLM/network calls.
"""

from __future__ import annotations

import os
import pytest

from kpm_builder.providers import (
    Family,
    available_families,
    extract_json,
    independence_label,
    make_provider,
)


# ── Family enum ────────────────────────────────────────────────────────────────


class TestFamily:
    def test_anthropic_value(self):
        assert Family.ANTHROPIC.value == "anthropic"

    def test_deepseek_value(self):
        assert Family.DEEPSEEK.value == "deepseek"

    def test_google_value(self):
        assert Family.GOOGLE.value == "google"

    def test_all_three_members(self):
        names = {m.value for m in Family}
        assert names == {"anthropic", "deepseek", "google"}


# ── extract_json ───────────────────────────────────────────────────────────────


class TestExtractJson:
    def test_bare_json_object(self):
        result = extract_json('{"verdict": "entails", "score": 1}')
        assert result == {"verdict": "entails", "score": 1}

    def test_json_fenced(self):
        text = '```json\n{"verdict": "reject"}\n```'
        result = extract_json(text)
        assert result == {"verdict": "reject"}

    def test_backtick_fenced_no_lang(self):
        text = '```\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_embedded_in_prose(self):
        text = 'Here is the result:\n{"status": "ok", "count": 42}\nThat is all.'
        result = extract_json(text)
        assert result == {"status": "ok", "count": 42}

    def test_whitespace_padded(self):
        result = extract_json('   {"a": 1}   ')
        assert result == {"a": 1}

    def test_invalid_raises(self):
        with pytest.raises(Exception):
            extract_json("this is not json at all")


# ── available_families ─────────────────────────────────────────────────────────


_ALL_KEYS = ["ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "GOOGLE_GENAI_API_KEY"]


def _clean_env():
    """Return a copy of os.environ with all provider keys removed."""
    return {k: v for k, v in os.environ.items() if k not in _ALL_KEYS}


class TestAvailableFamilies:
    def test_only_deepseek_key_set(self, monkeypatch):
        for key in _ALL_KEYS:
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-fake")
        result = available_families()
        assert result == [Family.DEEPSEEK]

    def test_no_keys_set(self, monkeypatch):
        for key in _ALL_KEYS:
            monkeypatch.delenv(key, raising=False)
        result = available_families()
        assert result == []

    def test_all_keys_set(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-ds-fake")
        monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "gk-fake")
        result = available_families()
        # Should contain all three; order matches Family enum declaration
        assert set(result) == {Family.ANTHROPIC, Family.DEEPSEEK, Family.GOOGLE}
        assert len(result) == 3

    def test_empty_string_key_not_counted(self, monkeypatch):
        for key in _ALL_KEYS:
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        result = available_families()
        assert Family.ANTHROPIC not in result


# ── independence_label ─────────────────────────────────────────────────────────


class TestIndependenceLabel:
    def test_cross_family(self):
        assert independence_label(Family.ANTHROPIC, Family.DEEPSEEK) == "cross-family"

    def test_cross_family_reverse(self):
        assert independence_label(Family.DEEPSEEK, Family.ANTHROPIC) == "cross-family"

    def test_cross_family_google_vs_anthropic(self):
        assert independence_label(Family.GOOGLE, Family.ANTHROPIC) == "cross-family"

    def test_same_family_anthropic(self):
        assert independence_label(Family.ANTHROPIC, Family.ANTHROPIC) == "same-family"

    def test_same_family_deepseek(self):
        assert independence_label(Family.DEEPSEEK, Family.DEEPSEEK) == "same-family"

    def test_same_family_google(self):
        assert independence_label(Family.GOOGLE, Family.GOOGLE) == "same-family"


# ── make_provider ──────────────────────────────────────────────────────────────


class TestMakeProvider:
    def test_unknown_family_string_raises_value_error(self):
        """Passing a bad string should raise; test via the enum path."""
        # We can't pass a raw string to make_provider (it takes Family), but we
        # verify internal guard by reaching an invalid branch.
        # The cleanest approach: patch Family to add a bogus member,
        # or call with a bad value cast.  Instead, just test that the function
        # signature accepts Family and raises ValueError for an unexpected enum
        # value by subclassing.  Simplest: test the error message branch
        # directly by monkeypatching _ENV_KEY to skip the family.
        import kpm_builder.providers as prov

        saved = prov._ENV_KEY.copy()
        try:
            # Remove all entries so the match-else branch is reachable via a
            # fake Family value that doesn't appear in the dispatch table.
            # Easiest: just call with a valid Family while SDK is absent and
            # assert callable, or assert the ValueError path is present.
            # We test the ValueError path by temporarily injecting a fake member.
            import enum

            class _FakeFamily(enum.Enum):
                BOGUS = "bogus"

            with pytest.raises(ValueError, match="Unknown family"):
                prov._make_provider_by_name("bogus")
        finally:
            prov._ENV_KEY.clear()
            prov._ENV_KEY.update(saved)

    def test_make_provider_returns_callable(self, monkeypatch):
        """make_provider should return a callable without actually hitting an API.

        We can only verify this when the SDK for the family is installed.
        DeepSeek uses openai SDK which is likely available; guard with a skip.
        We set a fake env key so the client constructor doesn't crash on missing key.
        """
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-fake-for-test")
        try:
            fn = make_provider(Family.DEEPSEEK)
            assert callable(fn)
        except ImportError:
            pytest.skip("openai SDK not installed — skipping make_provider construction test")
