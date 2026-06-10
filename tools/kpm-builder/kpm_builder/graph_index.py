"""kpm_builder.graph_index — compile the L0 graph substrate (SPEC-graph-substrate.md v2).

Mechanical, NO LLM, NO network. Reads a produced KPM's notes and emits a derived,
deterministic ``graph/index.json``: axiom nodes + concept nodes + ``mentions`` edges
(structural) + carried-over verified L3 relations. The dense axiom↔axiom adjacency
is NOT stored — it is DERIVED on demand by ``load_graph(...).shares_concept(...)``,
bounded and opt-in, to honour the doctrine's A1 fan-effect (no indiscriminate links).

The notes remain the source of truth; this index is a regenerable build artifact.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

from kpm_builder._util import atomic_write, read_frontmatters
from kpm_builder.concepts import MIN_DF, extract_concepts
from kpm_builder.relate import RelationType

GRAPH_VERSION = 1
_TOP_K_DEFAULT = 8
_L3_KINDS = frozenset(t.value for t in RelationType)


def _read_axiom_fms(kpm_dir: Path) -> list[dict]:
    return [fm for fm in read_frontmatters(Path(kpm_dir) / "axioms") if fm.get("id")]


# ── build ─────────────────────────────────────────────────────────────────────

def build_graph_index(kpm_dir: str | Path) -> dict:
    """Build the in-memory graph index dict from a produced KPM's notes."""
    kpm_dir = Path(kpm_dir)
    fms = _read_axiom_fms(kpm_dir)
    ids = [fm["id"] for fm in fms]
    valid = set(ids)
    statements = [str(fm.get("statement", "")) for fm in fms]
    axiom_concepts, info = extract_concepts(statements)

    nodes: list[dict] = []
    for fm in fms:
        nodes.append({"id": fm["id"], "kind": "axiom", "label": str(fm.get("statement", "")),
                      "confidence": fm.get("confidence"), "generativity": fm.get("generativity")})
    for c, m in info.items():
        nodes.append({"id": f"concept:{c}", "kind": "concept", "label": c,
                      "df": m["df"], "idf": m["idf"]})

    edges: list[dict] = []
    for i, concepts in enumerate(axiom_concepts):
        for c in concepts:
            edges.append({"from": ids[i], "to": f"concept:{c}", "kind": "mentions",
                          "weight": info[c]["idf"], "trust": "structural"})
    for fm in fms:
        rel = fm.get("relations") or {}
        for kind in _L3_KINDS:
            for tgt in rel.get(kind) or []:
                if tgt in valid:
                    edges.append({"from": fm["id"], "to": tgt, "kind": kind, "trust": "verified"})

    nodes.sort(key=lambda n: (n["kind"], n["id"]))
    edges.sort(key=lambda e: (e["from"], e["to"], e["kind"]))
    meta = {"version": GRAPH_VERSION, "n_axioms": len(ids), "n_concepts": len(info),
            "n_mentions": sum(1 for e in edges if e["kind"] == "mentions"),
            "params": {"MIN_DF": MIN_DF, "TOP_K_DEFAULT": _TOP_K_DEFAULT, "idf_dp": 4}}
    return {"version": GRAPH_VERSION, "nodes": nodes, "edges": edges, "meta": meta}


# ── compile (deterministic, atomic) ───────────────────────────────────────────

def _canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n"


def compile_graph(kpm_dir: str | Path, index: dict | None = None) -> Path:
    """Write ``<kpm>/graph/index.json`` (canonical, byte-stable). Returns the path.
    Pass a prebuilt ``index`` to avoid re-reading the notes."""
    kpm_dir = Path(kpm_dir)
    if index is None:
        index = build_graph_index(kpm_dir)
    gdir = kpm_dir / "graph"
    gdir.mkdir(exist_ok=True)
    out = gdir / "index.json"
    atomic_write(out, _canonical_json(index))
    return out


# ── consistency check ─────────────────────────────────────────────────────────

def validate_graph_index(kpm_dir: str | Path, index: dict) -> list[str]:
    """Return a list of consistency errors (empty == clean): every ``verified`` edge
    must resolve to a real note relation, and no ``structural`` edge may use an L3 kind."""
    kpm_dir = Path(kpm_dir)
    note_rel: set[tuple[str, str, str]] = set()
    for fm in _read_axiom_fms(kpm_dir):
        rel = fm.get("relations") or {}
        for kind in _L3_KINDS:
            for tgt in rel.get(kind) or []:
                note_rel.add((fm["id"], kind, tgt))
    node_ids = {n["id"] for n in index["nodes"]}
    errs: list[str] = []
    for e in index["edges"]:
        if e.get("trust") == "verified" and (e["from"], e["kind"], e["to"]) not in note_rel:
            errs.append(f"verified edge {e['from']} -{e['kind']}-> {e['to']} has no matching note relation")
        if e.get("trust") == "structural" and e["kind"] in _L3_KINDS:
            errs.append(f"structural edge {e['from']}->{e['to']} uses reserved L3 kind '{e['kind']}'")
        if e["kind"] == "mentions" and e["to"] not in node_ids:
            errs.append(f"mentions edge {e['from']}->{e['to']} points at a missing concept node")
    return errs


# ── loader (derived adjacency is a bounded, opt-in query) ─────────────────────

def _is_contiguous_subseq(small: list[str], big: list[str]) -> bool:
    if len(small) >= len(big):
        return False
    return any(big[i:i + len(small)] == small for i in range(len(big) - len(small) + 1))


class Graph:
    """Thin reader over a compiled index. Adjacency between axioms is derived, never stored."""

    def __init__(self, data: dict):
        self.data = data
        self.nodes = {n["id"]: n for n in data["nodes"]}
        self._by_from: dict[str, list[dict]] = collections.defaultdict(list)
        self._axioms_with: dict[str, list[str]] = collections.defaultdict(list)
        self._concepts_of: dict[str, set[str]] = collections.defaultdict(set)
        for e in data["edges"]:
            self._by_from[e["from"]].append(e)
            if e["kind"] == "mentions":
                self._axioms_with[e["to"]].append(e["from"])
                self._concepts_of[e["from"]].add(e["to"])

    def neighbors(self, node_id: str, include_structural: bool = False) -> list[dict]:
        """Edges out of ``node_id``. Default: verified only (A1-safe); structural on request."""
        return [e for e in self._by_from.get(node_id, [])
                if e["trust"] == "verified" or (include_structural and e["kind"] == "mentions")]

    def axioms_with(self, concept_id: str) -> list[str]:
        return sorted(self._axioms_with.get(concept_id, []))

    def _idf(self, concept_id: str) -> float:
        node = self.nodes.get(concept_id)
        return node["idf"] if node else 0.0

    def _label_tokens(self, concept_id: str) -> list[str]:
        node = self.nodes.get(concept_id)
        return node["label"].split() if node else []

    def _longest_cover(self, concept_ids: set[str]) -> list[str]:
        """Keep only the longest-covering grams (a shared unigram subsumed by a shared
        bigram is dropped) so a multi-word concept isn't triple-counted. Sorted output
        so the downstream Σ-idf is order-independent and byte-deterministic."""
        ordered = sorted(concept_ids, key=lambda c: (-len(self._label_tokens(c)), c))
        kept: list[str] = []
        for c in ordered:
            toks = self._label_tokens(c)
            if not any(_is_contiguous_subseq(toks, self._label_tokens(k)) for k in kept):
                kept.append(c)
        return sorted(kept)

    def shares_concept(self, axiom_id: str, top_k: int = _TOP_K_DEFAULT) -> list[dict]:
        """Derived adjacency: the top-K axioms sharing concepts with ``axiom_id``,
        weighted Σ idf(shared) with longest-gram de-dup. Bounded + deterministic."""
        mine = self._concepts_of.get(axiom_id, set())
        shared: dict[str, set[str]] = collections.defaultdict(set)
        for cid in mine:
            for other in self._axioms_with.get(cid, []):
                if other != axiom_id:
                    shared[other].add(cid)
        scored = []
        for other, concepts in shared.items():
            kept = self._longest_cover(concepts)              # sorted → stable sum
            weight = round(sum(self._idf(c) for c in kept), 4)
            scored.append((weight, other, kept))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [{"axiom": o, "weight": w, "via": v} for w, o, v in scored[:top_k]]


def load_graph(path: str | Path) -> Graph:
    return Graph(json.loads(Path(path).read_text(encoding="utf-8")))


# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog="python -m kpm_builder.graph_index",
        description="Compile the L0 graph substrate index (graph/index.json) for a KPM.",
    )
    p.add_argument("--kpm", required=True, help="Path to a produced KPM directory.")
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    idx = build_graph_index(args.kpm)          # build once; reuse for write + validate
    out = compile_graph(args.kpm, index=idx)
    m = idx["meta"]
    print(f"compiled {out} | axioms={m['n_axioms']} concepts={m['n_concepts']} "
          f"mentions={m['n_mentions']}")
    errs = validate_graph_index(args.kpm, idx)
    if errs:
        print("WARN graph/notes inconsistency:")
        for e in errs:
            print("  - " + e)


if __name__ == "__main__":
    main()
