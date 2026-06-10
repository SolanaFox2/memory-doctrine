#!/usr/bin/env python3
"""Validate the doctrine KPM. Exit 0 = clean, 1 = violations (printed)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

WIKILINK = re.compile(r"\[\[([^\]|#]+)")
REL_KEYS = ["derives-from", "supports", "generalizes", "contradicts", "applies-to-kpm"]
STATUS_VALUES = {"candidate", "provisional", "locked"}


def _parse(p: Path):
    """Return (frontmatter, body, error). error is a string on malformed YAML, else None."""
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text, None
    # Split on a LINE-ANCHORED `---` only, so a `---` inside a frontmatter
    # value (e.g. a URL like ".../sealevel---parallel...") can't truncate it.
    parts = re.split(r"(?m)^---[ \t]*$", text, maxsplit=2)
    if len(parts) < 3:
        return {}, text, None
    _, fm, body = parts
    try:
        return (yaml.safe_load(fm) or {}), body, None
    except yaml.YAMLError as exc:
        return {}, text, str(exc).splitlines()[0] if str(exc) else "YAML parse error"


def _collect(pkg: Path):
    """Return (notes, errors). errors captures unparseable YAML and duplicate ids
    — failures that would otherwise silently drop or misidentify a note."""
    notes = {}
    errs = []
    for sub in ("axioms", "evidence", "operators", "clusters"):
        d = pkg / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            fm, body, parse_err = _parse(f)
            if parse_err:
                errs.append(f"{f.name}: YAML parse error — {parse_err}")
            nid = fm.get("id", f.stem)
            if nid in notes:
                errs.append(f"{nid}: duplicate id (also in {notes[nid]['path'].name} and {f.name})")
                continue
            notes[nid] = {"fm": fm, "body": body, "kind": sub, "path": f}
    return notes, errs


def load(pkg: Path):
    """Backward-compatible loader (reused by ingest tooling): notes only."""
    notes, _ = _collect(pkg)
    return notes


def check(pkg: Path):
    notes, errs = _collect(pkg)
    ids = set(notes)
    clusters = {nid for nid, n in notes.items() if n["kind"] == "clusters"}
    cited_evidence: set[str] = set()
    for nid, n in notes.items():
        fm, body, kind = n["fm"], n["body"], n["kind"]
        if kind == "axioms":
            c = fm.get("confidence")
            if not isinstance(c, (int, float)) or not (0.0 <= c <= 1.0):
                errs.append(f"{nid}: confidence {c!r} not in [0,1]")
            g = fm.get("generativity")
            if g not in (1, 2, 3, 4, 5):
                errs.append(f"{nid}: generativity {g!r} not in 1..5")
            # status and cluster are optional, but if declared they must be valid:
            # a typo'd status silently disables the F2 invariant, and a dangling
            # cluster pointer is a broken link the README promises to catch.
            status = fm.get("status")
            if status is not None and status not in STATUS_VALUES:
                errs.append(f"{nid}: status {status!r} not one of {sorted(STATUS_VALUES)}")
            cluster = fm.get("cluster")
            if cluster is not None and cluster not in clusters:
                errs.append(f"{nid}: cluster '{cluster}' does not resolve to a cluster note")
            ev = fm.get("evidence") or []
            if not ev:
                errs.append(f"{nid}: no evidence (every axiom needs >=1)")
            for e in ev:
                if e not in ids:
                    errs.append(f"{nid}: evidence '{e}' does not resolve")
                else:
                    cited_evidence.add(e)
            rel = fm.get("relations") or {}
            wikilinks = set(WIKILINK.findall(body))
            for k in REL_KEYS:
                for tgt in rel.get(k) or []:
                    if k != "applies-to-kpm" and tgt not in ids:
                        errs.append(f"{nid}: relation {k} -> '{tgt}' does not resolve")
                    if k != "applies-to-kpm" and tgt in ids and tgt not in wikilinks:
                        errs.append(f"{nid}: relation {k} -> '{tgt}' missing matching [[wikilink]] in body")
                if k == "contradicts":
                    for tgt in rel.get("contradicts") or []:
                        if fm.get("status") == "locked" and notes.get(tgt, {}).get("fm", {}).get("status") == "locked":
                            errs.append(f"{nid}: F2 invariant — 'contradicts' edge to locked axiom '{tgt}'")
        if kind == "evidence":
            if not fm.get("url"):
                errs.append(f"{nid}: evidence note missing url")
            if not fm.get("verified"):
                errs.append(f"{nid}: evidence note missing verified date")
    # Every evidence note must be reachable from the index (thin-index/rich-store rule).
    for nid, n in notes.items():
        if n["kind"] == "evidence" and nid not in cited_evidence:
            errs.append(f"{nid}: orphan evidence note (cited by no axiom)")
    if errs:
        print(f"doctrine_lint: {len(errs)} violation(s):")
        for e in errs:
            print("  - " + e)
        return 1
    print(f"doctrine_lint: OK ({len(notes)} notes, 0 violations)")
    return 0


if __name__ == "__main__":
    pkg = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    sys.exit(check(pkg))
