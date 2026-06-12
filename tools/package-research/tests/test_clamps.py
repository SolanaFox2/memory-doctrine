"""Tests for the shared clamp pair (REVIEW.md M2/M3) — no LLM, no API key."""

from package_research.clamps import clamp_confidence, clamp_generativity


def test_clamp_generativity_accepts_numeric_strings():
    # The M2 regression: "4.0" must keep its value, not collapse to 1.
    assert clamp_generativity("4.0") == 4
    assert clamp_generativity("4") == 4
    assert clamp_generativity(4.6) == 5  # round, not truncate


def test_clamp_generativity_garbage_falls_back():
    assert clamp_generativity("junk") == 1
    assert clamp_generativity(None) == 1
    assert clamp_generativity([], fallback=3) == 3


def test_clamp_generativity_bounds():
    assert clamp_generativity(9) == 5
    assert clamp_generativity(0) == 1
    assert clamp_generativity(-2) == 1


def test_clamp_confidence_bounds_and_strings():
    assert clamp_confidence(1.7) == 1.0
    assert clamp_confidence(-0.3) == 0.0
    assert clamp_confidence("0.6") == 0.6


def test_clamp_confidence_garbage_falls_back():
    assert clamp_confidence("junk") == 0.0
    assert clamp_confidence(None) == 0.0
    # verify's documented fallback: the idea's prior confidence.
    assert clamp_confidence("junk", fallback=0.7) == 0.7


def test_stages_share_the_one_pair():
    # M3: no module may keep a private drifted copy.
    from package_research import cli, score, verify

    for mod in (cli, score, verify):
        assert not hasattr(mod, "_clamp_confidence")
        assert not hasattr(mod, "_clamp_generativity")
        assert mod.clamp_confidence is clamp_confidence
    assert cli.clamp_generativity is clamp_generativity
    assert score.clamp_generativity is clamp_generativity
