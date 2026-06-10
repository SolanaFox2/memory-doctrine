"""Tests for kpm_builder.graph_index (compiled graph substrate)."""
from __future__ import annotations

from pathlib import Path

from kpm_builder.apply_relations import apply_relations
from kpm_builder.cli import build_from_research
from kpm_builder.graph_index import (
    _build_parser,
    build_graph_index,
    compile_graph,
    load_graph,
    validate_graph_index,
)
from kpm_builder.relate import Relation, RelateResult, RelationType, read_axioms
from package_research.validate import validate


def _claim(stmt: str, url: str) -> dict:
    return {"statement": stmt, "source": {"url": url, "text": stmt, "venue": "ex"},
            "ground_verdict": "entails", "n_corroborations": 1, "generativity": 3}


def _kpm(tmp_path: Path) -> Path:
    beats = [
        {"question": "Q1", "claims": [
            _claim("An Ethereum epoch consists of thirty-two slots.", "https://ex.com/1"),
            _claim("An Ethereum epoch lasts about six minutes.", "https://ex.com/2")]},
        {"question": "Q2", "claims": [
            _claim("A checkpoint anchors the first slot of an epoch.", "https://ex.com/3"),
            _claim("A checkpoint becomes justified by a supermajority link.", "https://ex.com/4")]},
    ]
    build_from_research({"goal": "G", "in_scope": "I", "out_of_scope": "O"}, beats,
                        out_dir=tmp_path, run_date="2026-06-05", fetched_at="2026-06-05T00:00:00Z")
    return tmp_path


def test_build_index_has_axiom_concept_nodes_and_mentions(tmp_path):
    idx = build_graph_index(_kpm(tmp_path))
    kinds = [n["kind"] for n in idx["nodes"]]
    assert kinds.count("axiom") == 4
    concepts = {n["label"] for n in idx["nodes"] if n["kind"] == "concept"}
    assert "epoch" in concepts and "checkpoint" in concepts          # shared → concept nodes
    mentions = [e for e in idx["edges"] if e["kind"] == "mentions"]
    assert mentions and all(e["trust"] == "structural" for e in mentions)
    # epoch is shared by 3 axioms → df 3
    epoch = next(n for n in idx["nodes"] if n.get("label") == "epoch")
    assert epoch["df"] == 3 and epoch["idf"] > 0


def test_carries_verified_l3_edges_with_trust(tmp_path):
    kpm = _kpm(tmp_path)
    ids = [a.id for a in read_axioms(kpm)]
    apply_relations(kpm, RelateResult(relations=[
        Relation(ids[0], ids[1], RelationType.DERIVES_FROM, verified=True)]))
    idx = build_graph_index(kpm)
    verified = [e for e in idx["edges"] if e.get("trust") == "verified"]
    assert any(e["from"] == ids[0] and e["to"] == ids[1] and e["kind"] == "derives-from"
               for e in verified)
    # no structural edge ever uses an L3 relation kind
    assert not any(e["trust"] == "structural" and e["kind"] == "derives-from" for e in idx["edges"])


def test_compile_is_idempotent(tmp_path):
    kpm = _kpm(tmp_path)
    p1 = compile_graph(kpm); b1 = p1.read_bytes()
    p2 = compile_graph(kpm); b2 = p2.read_bytes()
    assert p1 == kpm / "graph" / "index.json"
    assert b1 == b2 and b1.endswith(b"\n")


def test_loader_neighbors_default_verified_only(tmp_path):
    kpm = _kpm(tmp_path)
    ids = [a.id for a in read_axioms(kpm)]
    apply_relations(kpm, RelateResult(relations=[
        Relation(ids[0], ids[1], RelationType.DERIVES_FROM, verified=True)]))
    g = load_graph(compile_graph(kpm))
    # default: only verified edges (A1-safe — no structural flood)
    assert all(e["trust"] == "verified" for e in g.neighbors(ids[0]))
    assert any(e["to"] == ids[1] for e in g.neighbors(ids[0]))
    # opt-in structural reveals concept mentions
    assert any(e["kind"] == "mentions" for e in g.neighbors(ids[0], include_structural=True))


def test_loader_shares_concept_neighborhood(tmp_path):
    kpm = _kpm(tmp_path)
    g = load_graph(compile_graph(kpm))
    ids = [a.id for a in read_axioms(kpm)]
    epoch_axioms = g.axioms_with("concept:epoch")
    assert len(epoch_axioms) == 3
    # the two checkpoint axioms are each other's shared-concept neighbors
    ck = [a.id for a in read_axioms(kpm) if "checkpoint" in a.statement.lower()]
    nbrs = {n["axiom"] for n in g.shares_concept(ck[0], top_k=8)}
    assert ck[1] in nbrs
    # adjacency weight is deterministic across independent loads (no set-sum drift)
    g2 = load_graph(compile_graph(kpm))
    assert g.shares_concept(ck[0]) == g2.shares_concept(ck[0])


def test_validate_flags_phantom_verified_edge(tmp_path):
    kpm = _kpm(tmp_path)
    idx = build_graph_index(kpm)
    ids = [a.id for a in read_axioms(kpm)]
    idx["edges"].append({"from": ids[0], "to": ids[2], "kind": "supports", "trust": "verified"})
    errs = validate_graph_index(kpm, idx)
    assert any("no matching note relation" in e for e in errs)
    # a clean index has no errors
    assert validate_graph_index(kpm, build_graph_index(kpm)) == []
    assert validate(str(kpm)).lint_ok    # graph build never touched the notes


def test_cli_parser_smoke():
    assert _build_parser().parse_args(["--kpm", "d"]).kpm == "d"


def test_integration_one_third_cluster_and_verified_overlay(tmp_path):
    # The "one-third" family the refuter rejected as a hard claim becomes a navigable
    # structural neighborhood — while a verified edge stays a separate, trusted overlay.
    beats = [
        {"question": "Q1", "claims": [
            _claim("An attacker can prevent finality by voting with one-third of the stake.", "https://ex.com/1"),
            _claim("Reverting a finalized block requires losing one-third of the staked eth.", "https://ex.com/2")]},
        {"question": "Q2", "claims": [
            _claim("Casper FFG is safe when fewer than one-third of validators are adversarial.", "https://ex.com/3"),
            _claim("The inactivity leak bleeds inactive validators below one-third of total stake.", "https://ex.com/4")]},
    ]
    build_from_research({"goal": "G", "in_scope": "I", "out_of_scope": "O"}, beats,
                        out_dir=tmp_path, run_date="2026-06-05", fetched_at="2026-06-05T00:00:00Z")
    ids = [a.id for a in read_axioms(tmp_path)]
    apply_relations(tmp_path, RelateResult(relations=[
        Relation(ids[0], ids[1], RelationType.SUPPORTS, verified=True)]))

    g = load_graph(compile_graph(tmp_path))
    assert len(g.axioms_with("concept:one-third")) == 4          # all four share the concept
    # every axiom has the other three as structural neighbours (dense web, on demand)
    assert {n["axiom"] for n in g.shares_concept(ids[2])} == {ids[0], ids[1], ids[3]}
    # but the default verified view is the sparse trusted overlay, not the flood
    assert [e["to"] for e in g.neighbors(ids[0])] == [ids[1]]
    assert validate_graph_index(tmp_path, build_graph_index(tmp_path)) == []
    assert validate(str(tmp_path)).lint_ok
