"""Tests for the contradiction → resolve loop (SPEC-resolve.md v2)."""
from __future__ import annotations

from kpm_builder.apply_relations import apply_relations
from kpm_builder.cli import build_from_research
from kpm_builder.relate import Relation, RelateResult, RelationType, read_axioms
from kpm_builder.resolve import (
    Contradiction,
    Resolution,
    Verdict,
    _build_parser,
    detect_contradictions,
    extract_measures,
    measures_disagree,
    normalize_number,
    record_resolution,
    resolve,
    resolve_kpm,
)
from kpm_builder.schema import ConfidenceBucket


def _claim(stmt: str, url: str) -> dict:
    return {"statement": stmt, "source": {"url": url, "text": stmt, "venue": "ex"},
            "ground_verdict": "entails", "n_corroborations": 1, "generativity": 3}


def _resolve_kpm(tmp_path):
    beats = [
        {"question": "Q1", "claims": [
            _claim("Finality takes 12.8 minutes in protocol.", "https://ex.com/1"),
            _claim("Finality takes about 15 minutes for a block.", "https://ex.com/2")]},
        {"question": "Q2", "claims": [
            _claim("An Ethereum epoch is 32 slots.", "https://ex.com/3"),
            _claim("An Ethereum epoch lasts 6.4 minutes.", "https://ex.com/4")]},
        {"question": "Q3", "claims": [
            _claim("A validator effective balance starts at 32 eth.", "https://ex.com/5"),
            _claim("A validator effective balance caps at 2048 eth.", "https://ex.com/6")]},
    ]
    build_from_research({"goal": "G", "in_scope": "I", "out_of_scope": "O"}, beats,
                        out_dir=tmp_path, run_date="2026-06-05", fetched_at="2026-06-05T00:00:00Z")
    return tmp_path


# ── T1 numeric normalization + extraction ─────────────────────────────────────

def test_normalize_number_forms():
    assert normalize_number("12.8") == 12.8
    assert normalize_number("32") == 32.0
    assert normalize_number("2,048") == 2048.0          # thousands separator
    assert normalize_number("2/3") == 0.6667
    assert normalize_number("33%") == 0.33
    assert normalize_number("one-third") == 0.333
    assert normalize_number("two-thirds") == 0.667
    assert normalize_number("not-a-number") is None


def test_extract_measures_value_and_unit():
    m = extract_measures("Finalizing a checkpoint takes 12.8 minutes.")
    assert (m[0].value, m[0].unit) == (12.8, "minute")
    m = extract_measures("a user must deposit 32 ETH into the contract")
    assert (m[0].value, m[0].unit) == (32.0, "eth")
    m = extract_measures("An Ethereum epoch consists of 32 slots.")
    assert (m[0].value, m[0].unit) == (32.0, "slot")
    m = extract_measures("voting with one-third of the total stake")
    assert m[0].value == 0.333 and m[0].unit == "total"


def test_measures_disagree():
    finality_a = extract_measures("finalizing takes 12.8 minutes")[0]
    finality_b = extract_measures("a block takes about 15 minutes to finalize")[0]
    assert measures_disagree(finality_a, finality_b)             # same unit, different value

    slots = extract_measures("an epoch is 32 slots")[0]
    eth = extract_measures("deposit 32 eth")[0]
    assert not measures_disagree(slots, eth)                     # same number, different unit

    third = extract_measures("one-third of the stake")[0]
    twothirds = extract_measures("two-thirds of the stake")[0]
    assert not measures_disagree(third, twothirds)              # complementary (x, 1-x) — same fact

    same = extract_measures("0.667 of the stake")[0]
    assert not measures_disagree(twothirds, same)              # equal values, different form


def test_dataclasses():
    c = Contradiction(a_id="a1", b_id="a2", source="value")
    assert c.source == "value"
    r = Resolution(a_id="a1", b_id="a2", status=Verdict.DISPUTE)
    assert r.status is Verdict.DISPUTE and r.confidence is ConfidenceBucket.UNVERIFIED
    assert r.truth == "" and r.basis == []


# ── T2 detect ─────────────────────────────────────────────────────────────────

def _stmt(kpm, aid):
    return next(a.statement for a in read_axioms(kpm) if a.id == aid)


def test_detect_value_disagreements(tmp_path):
    kpm = _resolve_kpm(tmp_path)
    cands = detect_contradictions(kpm)
    # exactly two real candidates: finality (12.8 vs 15 min) and balance (32 vs 2048 eth)
    assert len(cands) == 2 and all(c.source == "value" for c in cands)
    joined = [" ".join((_stmt(kpm, c.a_id), _stmt(kpm, c.b_id))) for c in cands]
    assert any("12.8 minutes" in j and "15 minutes" in j for j in joined)   # finality pair
    assert any("32 eth" in j and "2048 eth" in j for j in joined)           # balance pair
    # NOT flagged: 32 slots vs 32 eth (different unit), and 12.8 vs 6.4 minutes
    # (share only the unit "minute" as a concept → excluded from gating).
    for j in joined:
        assert not ("32 slots" in j and "2048 eth" in j)
        assert not ("12.8 minutes" in j and "6.4 minutes" in j)


def test_detect_includes_relate_contradicts_edges(tmp_path):
    kpm = _resolve_kpm(tmp_path)
    ids = [a.id for a in read_axioms(kpm)]
    apply_relations(kpm, RelateResult(relations=[
        Relation(ids[2], ids[3], RelationType.CONTRADICTS, verified=True)]))
    cands = detect_contradictions(kpm)
    assert any(c.source == "relate" and {c.a_id, c.b_id} == {ids[2], ids[3]} for c in cands)


# ── T3 resolve (grounded, refute-framed) ──────────────────────────────────────

_STMTS = {"a": "Finality takes 12.8 minutes.", "b": "A block takes about 15 minutes to finalize."}
_EVID = {"ea": "it takes 12.8 minutes, two epochs, to finalise a checkpoint in-protocol.",
         "eb": "It takes about 15 minutes for an Ethereum block to finalize."}
_AXEV = {"a": ["ea"], "b": ["eb"]}
_CAND = Contradiction("a", "b", source="value", detail="PROPOSER SECRET RATIONALE")


def _verdict(d):
    return lambda prompt, schema: d


def test_resolve_reconciled_requires_entailing_truth():
    raw = {"status": "reconciled", "truth": "Finality is 12.8 minutes; ~15 is rounded.",
           "truth_passage_id": "ea", "explanation": "approximation", "basis": ["ea"]}
    # grounder confirms the truth is entailed by ea → reconciled stands
    r = resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=_verdict(raw),
                ground_fn=lambda claim, passage: "entails")
    assert r.status is Verdict.RECONCILED and r.truth_passage_id == "ea"
    # grounder says the truth over-claims its passage → downgrade to dispute
    r2 = resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=_verdict(raw),
                 ground_fn=lambda claim, passage: "over_claims")
    assert r2.status is Verdict.DISPUTE


def test_resolve_reconciled_without_passage_is_dispute():
    raw = {"status": "reconciled", "truth": "X", "explanation": "no citation", "basis": []}
    r = resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=_verdict(raw),
                ground_fn=lambda c, p: "entails")
    assert r.status is Verdict.DISPUTE          # no truth_passage_id → can't reconcile


def test_resolve_error_downgrades_when_axiom_is_faithful():
    raw = {"status": "error", "error_axiom": "b", "explanation": "b looks wrong", "basis": ["eb"]}
    # b faithfully entails its own source → it's a dispute, not an axiom error
    r = resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=_verdict(raw),
                ground_fn=lambda c, p: "entails")
    assert r.status is Verdict.DISPUTE
    # b over-claims its own source → error stands
    r2 = resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=_verdict(raw),
                 ground_fn=lambda c, p: "over_claims")
    assert r2.status is Verdict.ERROR


def test_resolve_malformed_defaults_to_dispute():
    r = resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=_verdict({}),
                ground_fn=lambda c, p: "entails")
    assert r.status is Verdict.DISPUTE


def test_resolve_distinct_skips_grounding():
    def no_ground(claim, passage):
        raise AssertionError("distinct must not ground a truth")

    raw = {"status": "distinct", "explanation": "finalization time vs epoch length — different things"}
    r = resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=_verdict(raw), ground_fn=no_ground)
    assert r.status is Verdict.DISTINCT and r.truth == "" and r.dissent is not None


def test_resolve_prompt_demands_single_passage_truth():
    captured = {}

    def fake(prompt, schema):
        captured["p"] = prompt
        return {"status": "dispute", "explanation": "x"}

    resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=fake, ground_fn=lambda c, p: "entails")
    # the scoping instruction is present (truth must not bundle cross-passage reasoning)
    assert "ONLY the one precise fact" in captured["p"] and "distinct" in captured["p"]


def test_resolve_prompt_isolated_from_proposer_rationale():
    captured = {}

    def fake(prompt, schema):
        captured["p"] = prompt
        return {"status": "dispute", "explanation": "x"}

    resolve(_CAND, _STMTS, _EVID, _AXEV, complete_json=fake, ground_fn=lambda c, p: "entails")
    p = captured["p"]
    assert "Finality takes 12.8 minutes." in p and "15 minutes to finalize." in p
    assert "PROPOSER SECRET RATIONALE" not in p      # isolation
    assert "12.8 minutes, two epochs" in p           # passages shown


# ── T4 record (clusters/ note, idempotent, lint-neutral) ──────────────────────

def test_record_resolution_writes_cluster_note(tmp_path):
    import yaml
    from package_research.validate import validate

    kpm = _resolve_kpm(tmp_path)
    ids = sorted(a.id for a in read_axioms(kpm))
    before = {f.name: f.read_bytes() for f in (kpm / "axioms").glob("*.md")}

    res = Resolution(ids[1], ids[0], Verdict.RECONCILED, truth="12.8 min is precise; 15 is rounded.",
                     truth_passage_id="e1", explanation="rounding", basis=["e1"],
                     confidence=ConfidenceBucket.PARTIAL)
    p = record_resolution(kpm, res, resolved="2026-06-05")

    assert p.parent.name == "clusters"
    fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---")[1])
    assert fm["type"] == "resolution" and fm["status"] == "reconciled"
    assert fm["axioms"] == [ids[0], ids[1]]                  # canonical sorted
    assert fm["truth_passage_id"] == "e1" and fm["basis"] == ["e1"]
    assert "verified" not in fm and "id" not in fm          # no lint-meaningful clashes

    # idempotent
    b1 = p.read_bytes()
    record_resolution(kpm, res, resolved="2026-06-05")
    assert p.read_bytes() == b1
    # pair order doesn't change the filename
    res2 = Resolution(ids[0], ids[1], Verdict.RECONCILED, truth="12.8 min is precise; 15 is rounded.",
                      truth_passage_id="e1", explanation="rounding", basis=["e1"],
                      confidence=ConfidenceBucket.PARTIAL)
    assert record_resolution(kpm, res2, resolved="2026-06-05") == p
    # lint still clean; axiom notes untouched
    assert validate(str(kpm)).lint_ok
    assert {f.name: f.read_bytes() for f in (kpm / "axioms").glob("*.md")} == before


# ── T5 orchestrate + CLI + integration ────────────────────────────────────────

def test_cli_parser_smoke():
    ns = _build_parser().parse_args(["--kpm", "d", "--resolved", "2026-06-05"])
    assert ns.kpm == "d" and ns.resolved == "2026-06-05"


def test_resolve_kpm_end_to_end(tmp_path):
    import re as _re

    from package_research.validate import validate

    kpm = _resolve_kpm(tmp_path)
    axioms_before = {f.name: f.read_bytes() for f in (kpm / "axioms").glob("*.md")}

    def fake(prompt, schema):
        if "independent fact-verifier" in prompt:                 # ground.py call
            return {"verdict": "entails", "supported_paraphrase": "", "dropped": [], "reason": ""}
        eid = _re.search(r"evidence (\S+):", prompt)              # resolve verdict call
        return {"status": "reconciled", "truth": "The precise figure is established by the source.",
                "truth_passage_id": eid.group(1) if eid else "", "explanation": "rounding",
                "basis": []}

    resolutions = resolve_kpm(kpm, complete_json=fake, resolved="2026-06-05")
    assert len(resolutions) == 2                                  # finality + balance candidates
    assert all(r.status is Verdict.RECONCILED for r in resolutions)
    assert list((kpm / "clusters").glob("*.md"))                 # resolution notes written
    assert validate(str(kpm)).lint_ok                            # package still lints clean
    # the whole loop never touched an axiom note
    assert {f.name: f.read_bytes() for f in (kpm / "axioms").glob("*.md")} == axioms_before
