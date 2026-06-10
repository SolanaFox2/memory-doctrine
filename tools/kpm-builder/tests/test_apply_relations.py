"""Tests for the Relate stage's mechanical writer (apply_relations.py)."""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

from kpm_builder.apply_relations import (
    apply_relations,
    relate_and_apply,
    rewrite_axiom_md,
)
from kpm_builder.cli import build_from_research
from kpm_builder.relate import (
    Relation,
    RelateResult,
    RelationType,
    _build_parser,
    parse_axiom_md,
    read_axioms,
    relate_kpm,
)
from package_research.validate import validate

SAMPLE_AXIOM = textwrap.dedent('''\
    ---
    id: a-alpha
    type: axiom
    title: "Alpha"
    statement: "Alpha is a fundamental property."
    domain: "distilled"
    generativity: 4
    confidence: 0.5
    status: candidate
    relations:
      derives-from: []
      supports: []
      generalizes: []
      contradicts: []
      applies-to-kpm: []
    evidence: [https-ex-com-alpha]
    provenance: "package-research/distilled"
    ---

    # Alpha

    Alpha is a fundamental property.

    Evidence: [[https-ex-com-alpha]].
    ''')


# ── T6 rewrite_axiom_md (pure) ────────────────────────────────────────────────

def test_rewrite_inserts_relation_and_wikilink():
    out = rewrite_axiom_md(SAMPLE_AXIOM, [(RelationType.SUPPORTS, "a-beta")])
    assert "supports: [a-beta]" in out
    assert "[[a-beta]]" in out
    # other relation lines untouched, evidence wikilink intact, still parseable
    assert "derives-from: []" in out
    assert "[[https-ex-com-alpha]]" in out
    assert parse_axiom_md(out).id == "a-alpha"


def test_rewrite_is_idempotent():
    once = rewrite_axiom_md(SAMPLE_AXIOM, [(RelationType.SUPPORTS, "a-beta")])
    twice = rewrite_axiom_md(once, [(RelationType.SUPPORTS, "a-beta")])
    assert once == twice


def test_rewrite_sorts_and_dedups():
    out = rewrite_axiom_md(
        SAMPLE_AXIOM,
        [(RelationType.SUPPORTS, "z-id"),
         (RelationType.SUPPORTS, "a-id"),
         (RelationType.SUPPORTS, "a-id")],
    )
    assert "supports: [a-id, z-id]" in out


def test_rewrite_reciprocal_contradicts_via_incoming():
    out = rewrite_axiom_md(SAMPLE_AXIOM, [], incoming_contradicts=["a-foe"])
    assert "contradicts: [a-foe]" in out
    assert "[[a-foe]]" in out


def test_rewrite_absent_line_is_noop_for_that_type():
    # 'applies-to-kpm' line exists; an unknown relation block line would be skipped.
    txt = SAMPLE_AXIOM.replace("  supports: []\n", "")   # remove the supports line
    out = rewrite_axiom_md(txt, [(RelationType.SUPPORTS, "a-beta")])
    # no supports line to edit → frontmatter unchanged; only the wikilink appended
    assert "supports: [a-beta]" not in out
    assert "[[a-beta]]" in out


# ── T7/T8 apply_relations + integration (build → relate → apply → lint) ───────

def _claim(stmt: str, url: str) -> dict:
    return {
        "statement": stmt,
        "source": {"url": url, "text": stmt, "venue": "ex"},
        "ground_verdict": "entails",
        "n_corroborations": 1,
        "generativity": 3,
    }


def _file_for(kpm: Path, aid: str) -> Path:
    for f in (kpm / "axioms").glob("*.md"):
        if parse_axiom_md(f.read_text(encoding="utf-8")).id == aid:
            return f
    raise AssertionError(f"no axiom file for {aid}")


def test_build_relate_apply_keeps_lint_green_and_forms_web(tmp_path):
    contract = {"goal": "G", "in_scope": "I", "out_of_scope": "O"}
    beats = [
        {"question": "Q1", "claims": [
            _claim("Alpha is a fundamental property of system X.", "https://ex.com/1"),
            _claim("Gamma constrains Alpha within system X.", "https://ex.com/2")]},
        {"question": "Q2", "claims": [
            _claim("Beta is derivable from Alpha in system X.", "https://ex.com/3"),
            _claim("Delta bounds Beta in system X.", "https://ex.com/4")]},
    ]
    outcome = build_from_research(
        contract, beats, out_dir=tmp_path,
        run_date="2026-06-04", fetched_at="2026-06-04T00:00:00Z",
    )
    assert outcome.is_kpm
    assert validate(str(tmp_path)).lint_ok          # clean before relate

    ids = [a.id for a in read_axioms(tmp_path)]
    assert len(ids) == 4

    def fake(prompt, schema):
        if "AXIOMS:" in prompt and "PROPOSED RELATION" not in prompt:
            aids = re.findall(r"(?m)^- (\S+):", prompt)
            return {"relations": [
                {"from_id": aids[0], "to_id": aids[1], "type": "supports", "rationale": "r"}]}
        return {"holds": True, "reason": "x"}   # verifier confirms

    result = relate_kpm(tmp_path, complete_json=fake)
    assert len(result.relations) == 1
    frm, to = result.relations[0].from_id, result.relations[0].to_id

    apply_relations(tmp_path, result)

    assert validate(str(tmp_path)).lint_ok          # still clean after relate
    written = _file_for(tmp_path, frm).read_text(encoding="utf-8")
    assert f"supports: [{to}]" in written
    assert f"[[{to}]]" in written

    # idempotent: applying again changes nothing on disk
    before = _file_for(tmp_path, frm).read_text(encoding="utf-8")
    apply_relations(tmp_path, result)
    assert _file_for(tmp_path, frm).read_text(encoding="utf-8") == before


# ── T9 CLI surface ────────────────────────────────────────────────────────────

def test_cli_parser_smoke():
    ns = _build_parser().parse_args(["--kpm", "somedir", "--family", "deepseek"])
    assert ns.kpm == "somedir" and ns.family == "deepseek"


def test_apply_relations_never_writes_unverified(tmp_path):
    contract = {"goal": "G", "in_scope": "I", "out_of_scope": "O"}
    beats = [
        {"question": "Q1", "claims": [
            _claim("Alpha is a fundamental property of system X.", "https://ex.com/1"),
            _claim("Gamma constrains Alpha within system X.", "https://ex.com/2")]},
    ]
    build_from_research(contract, beats, out_dir=tmp_path,
                        run_date="2026-06-04", fetched_at="2026-06-04T00:00:00Z")
    ids = [a.id for a in read_axioms(tmp_path)]

    # An unverified edge must be dropped, not written.
    apply_relations(tmp_path, RelateResult(relations=[
        Relation(ids[0], ids[1], RelationType.SUPPORTS, verified=False)]))

    text = _file_for(tmp_path, ids[0]).read_text(encoding="utf-8")
    assert "supports: []" in text            # unchanged
    assert f"[[{ids[1]}]]" not in text
    assert validate(str(tmp_path)).lint_ok


def test_relate_and_apply_wrapper(tmp_path):
    contract = {"goal": "G", "in_scope": "I", "out_of_scope": "O"}
    beats = [
        {"question": "Q1", "claims": [
            _claim("Alpha is a fundamental property of system X.", "https://ex.com/1"),
            _claim("Gamma constrains Alpha within system X.", "https://ex.com/2")]},
        {"question": "Q2", "claims": [
            _claim("Beta is derivable from Alpha in system X.", "https://ex.com/3"),
            _claim("Delta bounds Beta in system X.", "https://ex.com/4")]},
    ]
    build_from_research(contract, beats, out_dir=tmp_path,
                        run_date="2026-06-04", fetched_at="2026-06-04T00:00:00Z")

    def fake(prompt, schema):
        if "AXIOMS:" in prompt and "PROPOSED RELATION" not in prompt:
            aids = re.findall(r"(?m)^- (\S+):", prompt)
            return {"relations": [
                {"from_id": aids[0], "to_id": aids[1], "type": "supports"}]}
        return {"holds": True, "reason": "x"}

    result = relate_and_apply(tmp_path, complete_json=fake)
    assert len(result.relations) == 1
    assert validate(str(tmp_path)).lint_ok
