"""Tests for the assemble stage — DETERMINISTIC, no LLM, no API key."""

import json

import yaml
from package_research.assemble import assemble, build_knowledge_json
from package_research.score import ScoredIdea
from package_research.split import split

RUN_DATE = "2026-06-03"


def _parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---")
    _, fm, body = text.split("---", 2)
    return yaml.safe_load(fm), body


def _scored(statement, sources, snippets, *, confidence=0.7, generativity=3):
    return ScoredIdea(
        statement=statement,
        supporting_source_files=list(sources),
        supporting_snippets=list(snippets),
        confidence=confidence,
        generativity=generativity,
        rationale="because snippet",
    )


def test_knowledge_json_has_required_fields():
    kj = build_knowledge_json(name="@kpm/x", description="d")
    assert kj["name"] == "@kpm/x"
    assert kj["version"] == "0.1.0"
    assert kj["license"] == "CC-BY-4.0"
    assert kj["type"] == "knowledge-package"
    assert kj["entrypoint"] == "README.md"
    assert kj["files"] == ["**/*.md", "!wiki/**", "!knowledge_modules/**"]
    assert kj["knowledgeDependencies"] == {}


def test_assemble_writes_expected_files(tmp_path):
    axioms, evidence = split([_scored("Retrieval is pattern completion.", ["alpha.md"], ["pattern completion"])])
    res = assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)

    assert (tmp_path / "knowledge.json").is_file()
    assert (tmp_path / "README.md").is_file()
    assert (tmp_path / "scripts" / "doctrine_lint.py").is_file()
    assert res.axioms_written == ["retrieval-is-pattern-completion"]
    assert res.evidence_written == ["alpha"]
    assert (tmp_path / "axioms" / "retrieval-is-pattern-completion.md").is_file()
    assert (tmp_path / "evidence" / "alpha.md").is_file()


def test_assemble_knowledge_json_valid(tmp_path):
    axioms, evidence = split([_scored("A claim.", ["s.md"], ["snip"])])
    assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    kj = json.loads((tmp_path / "knowledge.json").read_text())
    assert kj["version"] == "0.1.0"
    assert kj["license"] == "CC-BY-4.0"
    assert kj["entrypoint"] == "README.md"


def test_assemble_axiom_frontmatter_fields(tmp_path):
    axioms, evidence = split([_scored("Memory is associative.", ["s.md"], ["snip"], confidence=0.85, generativity=5)])
    assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    fm, body = _parse_frontmatter(tmp_path / "axioms" / "memory-is-associative.md")
    assert fm["type"] == "axiom"
    assert fm["status"] == "candidate"
    assert fm["confidence"] == 0.85
    assert fm["generativity"] == 5
    assert fm["evidence"] == ["s"]
    assert set(fm["relations"]) == {"derives-from", "supports", "generalizes", "contradicts", "applies-to-kpm"}
    assert all(v == [] for v in fm["relations"].values())
    assert fm["relations"]["contradicts"] == []
    assert "title" in fm and "statement" in fm and "domain" in fm and "provenance" in fm
    # Body has a wikilink to the cited evidence id.
    assert "[[s]]" in body


def test_assemble_evidence_has_url_and_verified(tmp_path):
    axioms, evidence = split([_scored("A claim.", ["src.md"], ["the snippet"])])
    assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    fm, body = _parse_frontmatter(tmp_path / "evidence" / "src.md")
    assert fm["type"] == "evidence"
    assert fm["url"]  # REQUIRED by doctrine_lint
    assert fm["verified"]  # REQUIRED by doctrine_lint
    # verified is the passed-in run_date (deterministic), not now().
    assert str(fm["verified"]) == RUN_DATE
    assert "the snippet" in body
    assert "src" in fm["supports"] or "a-claim" in fm["supports"]


def test_assemble_drops_axiom_without_evidence(tmp_path):
    # An axiom whose evidence list cannot resolve must be dropped.
    bad = _scored("Floating claim.", [], [])  # no sources => no evidence
    good = _scored("Grounded claim.", ["g.md"], ["snip"])
    axioms, evidence = split([bad, good])
    res = assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    assert "floating-claim" not in res.axioms_written
    assert "grounded-claim" in res.axioms_written
    assert not (tmp_path / "axioms" / "floating-claim.md").exists()


def test_assemble_every_axiom_evidence_id_has_a_note(tmp_path):
    axioms, evidence = split(
        [
            _scored("First.", ["a.md", "b.md"], ["s1"]),
            _scored("Second.", ["b.md", "c.txt"], ["s2"]),
        ]
    )
    res = assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    written_ev = set(res.evidence_written)
    for ax_id in res.axioms_written:
        fm, _ = _parse_frontmatter(tmp_path / "axioms" / f"{ax_id}.md")
        for eid in fm["evidence"]:
            assert eid in written_ev, f"{ax_id} cites {eid} with no note"
            assert (tmp_path / "evidence" / f"{eid}.md").is_file()


def test_assemble_readme_lists_axioms_no_dangling_links(tmp_path):
    axioms, evidence = split([_scored("Listed claim.", ["s.md"], ["snip"])])
    assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    readme = (tmp_path / "README.md").read_text()
    assert "Listed claim." in readme
    # README must not introduce unresolved wikilinks.
    assert "[[" not in readme


def test_readme_bullet_no_title_statement_duplication(tmp_path):
    # A statement whose leading clause IS the whole statement (no .;: inside)
    # must not render the title twice ("**X** — X").
    full = "Three benchmarks define agent memory in 2026 and the field is converging"
    axioms, evidence = split([_scored(full, ["s.md"], ["snip"])])
    assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    readme = (tmp_path / "README.md").read_text()
    assert f"**{full}** — {full}" not in readme
    assert f"- **{full}**" in readme

    # A statement of form "Lead clause: elaboration" keeps the bold lead but
    # drops the duplicated prefix from the trailing text.
    # A ';' or ',' separator after the lead clause must also be stripped clean.
    semi = "Polymarket uses a CLOB; LMSR is only a mental model"
    axioms3, evidence3 = split([_scored(semi, ["u.md"], ["snip"])])
    out3 = tmp_path / "pkg3"
    assemble(axioms3, evidence3, out3, run_date=RUN_DATE)
    readme3 = (out3 / "README.md").read_text()
    assert "**Polymarket uses a CLOB** — LMSR is only a mental model" in readme3
    assert "—  ;" not in readme3 and "— ;" not in readme3

    colon = "Memory is not long context: the two are measured differently"
    axioms2, evidence2 = split([_scored(colon, ["t.md"], ["snip"])])
    out2 = tmp_path / "pkg2"
    assemble(axioms2, evidence2, out2, run_date=RUN_DATE)
    readme2 = (out2 / "README.md").read_text()
    assert "**Memory is not long context** — the two are measured differently" in readme2
    assert "Memory is not long context: the two are measured differently —" not in readme2


# --- uncited reference bucket (keep-uncited): preserve, never claim evidence ---

from package_research.assemble import write_reference_notes  # noqa: E402
from package_research.validate import validate  # noqa: E402


def test_write_reference_notes_preserves_uncited_content(tmp_path):
    uncited = {"sentiment.md": ["## Hypothesis\n\nsentiment diverges from price"]}
    written = write_reference_notes(uncited, tmp_path, run_date=RUN_DATE)
    assert written  # at least one id
    ref = tmp_path / "reference" / f"{written[0]}.md"
    assert ref.is_file()
    fm, body = _parse_frontmatter(ref)
    assert fm["type"] == "reference"
    assert fm["status"] == "uncited"
    assert "sentiment diverges from price" in body  # content preserved
    assert "No axiom cites this source yet" in body  # clearly flagged


def test_write_reference_notes_noop_when_empty(tmp_path):
    assert write_reference_notes({}, tmp_path, run_date=RUN_DATE) == []
    assert not (tmp_path / "reference").exists()


def test_reference_bucket_does_not_break_doctrine_lint(tmp_path):
    # A normal package + a reference/ note must still lint clean (lint ignores it).
    axioms, evidence = split([_scored("A grounded claim.", ["g.md"], ["snip"])])
    assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    write_reference_notes({"dropped.md": ["## X\n\nuncited content"]}, tmp_path, run_date=RUN_DATE)
    vr = validate(tmp_path)
    assert vr.lint_ok, f"reference/ must not break lint: {vr.lint_violations}"
