"""Config tests — env parsing must fail loudly, naming the variable (REVIEW.md L3)."""

import pytest
from package_research.config import Config


def test_from_env_bad_int_names_the_env_var(monkeypatch):
    monkeypatch.setenv("PR_MAX_SOURCES", "lots")
    with pytest.raises(ValueError, match="PR_MAX_SOURCES.*'lots'"):
        Config.from_env(input_dir="notes")


def test_from_env_bad_max_tokens_names_the_env_var(monkeypatch):
    monkeypatch.delenv("PR_MAX_SOURCES", raising=False)
    monkeypatch.setenv("PR_MAX_TOKENS", "4k")
    with pytest.raises(ValueError, match="PR_MAX_TOKENS"):
        Config.from_env(input_dir="notes")


def test_from_env_good_ints_parse(monkeypatch):
    monkeypatch.setenv("PR_MAX_SOURCES", "7")
    monkeypatch.setenv("PR_MAX_TOKENS", "512")
    monkeypatch.delenv("PR_DISTILL_BATCH_SIZE", raising=False)
    cfg = Config.from_env(input_dir="notes")
    assert cfg.max_sources == 7
    assert cfg.max_tokens == 512


def test_dead_default_score_fields_are_gone():
    # REVIEW.md L6: default_confidence/default_generativity were unused config.
    assert "default_confidence" not in Config.model_fields
    assert "default_generativity" not in Config.model_fields
