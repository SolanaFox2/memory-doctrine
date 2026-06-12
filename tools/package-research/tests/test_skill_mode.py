"""Keyless skill-mode tests — the `ingest` and `build` subcommands.

These MUST pass with NO ``ANTHROPIC_API_KEY``: skill mode never touches the LLM.
They also include a **regression test** for the bug a real run exposed —
``ingest`` produced a non-``str`` ``source_file`` that crashed ``assemble``'s
YAML serializer. We flow a real ``ingest`` source_file all the way through
``split -> assemble`` and assert the package is doctrine-lint clean.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from package_research import cli
from package_research.assemble import assemble
from package_research.config import Config
from package_research.ingest import ingest
from package_research.score import ScoredIdea
from package_research.split import split

RUN_DATE = "2026-06-03"


@pytest.fixture
def _no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def _lint_clean(out: Path) -> subprocess.CompletedProcess:
    lint = out / "scripts" / "doctrine_lint.py"
    assert lint.is_file(), "package must ship a vendored doctrine_lint.py"
    return subprocess.run([sys.executable, str(lint), str(out)], capture_output=True, text=True)


# --------------------------------------------------------------------------
# Regression: a real ingest source_file must flow cleanly through assemble.
# --------------------------------------------------------------------------
def test_real_ingest_source_file_reaches_assemble_without_crash(notes_dir, tmp_path, _no_api_key):
    """Guards the bug: ingest's source_file type must serialize in assemble."""
    candidates = ingest(Config(input_dir=notes_dir))
    assert candidates, "fixture must yield candidates"

    # Build ScoredIdeas using the REAL source_file values straight from ingest
    # (a relative path string) — exactly what crashed assemble's YAML before.
    by_source = {}
    for c in candidates:
        by_source.setdefault(c.source_file, c.text)

    scored = [
        ScoredIdea(
            statement=f"Idea grounded in {src}.",
            supporting_source_files=[src],  # the real ingest value, untouched
            supporting_snippets=[text.strip()[:120] or "snippet"],
            confidence=0.7,
            generativity=3,
            rationale="from real ingest output",
        )
        for src, text in by_source.items()
    ]
    assert scored

    out = tmp_path / "kpm-out"
    axioms, evidence = split(scored)
    result = assemble(axioms, evidence, out, run_date=RUN_DATE)

    assert result.axioms_written, "axioms should be written"
    assert result.evidence_written, "evidence should be written"

    proc = _lint_clean(out)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "0 violations" in proc.stdout


# --------------------------------------------------------------------------
# `ingest` subcommand
# --------------------------------------------------------------------------
def test_cli_ingest_json_lists_candidates(notes_dir, capsys, _no_api_key):
    rc = cli.main(["ingest", str(notes_dir), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list) and payload
    first = payload[0]
    assert set(first) == {"index", "source_file", "text"}
    assert isinstance(first["source_file"], str)
    assert first["index"] == 1
    # Nested source keeps its relative posix path.
    assert any(item["source_file"] == "sub/gamma.md" for item in payload)


def test_cli_ingest_human_readable_without_json(notes_dir, capsys, _no_api_key):
    rc = cli.main(["ingest", str(notes_dir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "source_file: alpha.md" in out


def test_cli_ingest_rejects_missing_dir(tmp_path, capsys, _no_api_key):
    rc = cli.main(["ingest", str(tmp_path / "nope")])
    assert rc == 2
    assert "not a directory" in capsys.readouterr().err


# --------------------------------------------------------------------------
# `build` subcommand
# --------------------------------------------------------------------------
_GOOD_IDEAS = [
    {
        "statement": "A thin index over a fat store keeps recall cheap.",
        "supporting_source_files": ["alpha.md"],
        "supporting_snippets": ["A thin index over a fat store keeps recall cheap."],
        "confidence": 0.8,
        "generativity": 4,
        "rationale": "verbatim from source",
    },
    {
        "statement": "Confidence is earned by evidence and never inferred from fluency.",
        "supporting_source_files": ["beta.txt"],
        "supporting_snippets": ["Confidence is earned by evidence and is revisable."],
        "confidence": 0.7,
        "generativity": 3,
    },
]


def _write_ideas(tmp_path: Path, ideas) -> Path:
    p = tmp_path / "ideas.json"
    p.write_text(json.dumps(ideas), encoding="utf-8")
    return p


def test_cli_build_produces_lint_clean_package(notes_dir, tmp_path, capsys, _no_api_key):
    ideas = _write_ideas(tmp_path, _GOOD_IDEAS)
    out = tmp_path / "kpm-out"

    rc = cli.main(["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out), "--name", "@kpm/skill-test"])
    assert rc == 0, "lint-clean build must exit 0"

    assert (out / "knowledge.json").is_file()
    assert (out / "README.md").is_file()
    assert list((out / "axioms").glob("*.md"))
    assert list((out / "evidence").glob("*.md"))

    manifest = json.loads((out / "knowledge.json").read_text())
    assert manifest["name"] == "@kpm/skill-test"

    proc = _lint_clean(out)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    summary = capsys.readouterr().out
    assert "doctrine lint       : OK" in summary


def test_cli_build_clamps_confidence_and_generativity(notes_dir, tmp_path, _no_api_key):
    ideas = _write_ideas(
        tmp_path,
        [
            {
                "statement": "Out-of-range scores must be clamped on build.",
                "supporting_source_files": ["alpha.md"],
                "supporting_snippets": ["A thin index over a fat store keeps recall cheap."],
                "confidence": 1.7,  # -> 1.0
                "generativity": 9,  # -> 5
            }
        ],
    )
    out = tmp_path / "kpm-out"
    rc = cli.main(["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out)])
    assert rc == 0

    axiom = next((out / "axioms").glob("*.md")).read_text()
    assert "confidence: 1.0" in axiom
    assert "generativity: 5" in axiom


def test_cli_build_drops_unsupported_ideas(notes_dir, tmp_path, _no_api_key):
    ideas = _write_ideas(
        tmp_path,
        [
            {
                "statement": "Supported idea with a real snippet.",
                "supporting_source_files": ["alpha.md"],
                "supporting_snippets": ["A thin index over a fat store keeps recall cheap."],
                "confidence": 0.8,
                "generativity": 4,
            },
            {
                "statement": "Unsupported idea with no snippet — must be dropped.",
                "supporting_source_files": ["beta.txt"],
                "supporting_snippets": [],  # no evidence -> dropped
                "confidence": 0.9,
                "generativity": 5,
            },
            {
                "statement": "Idea whose snippets are only whitespace — also dropped.",
                "supporting_source_files": ["beta.txt"],
                "supporting_snippets": ["   ", ""],
                "confidence": 0.6,
                "generativity": 2,
            },
        ],
    )
    out = tmp_path / "kpm-out"
    rc = cli.main(["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out)])
    assert rc == 0

    axiom_files = list((out / "axioms").glob("*.md"))
    assert len(axiom_files) == 1, "only the supported idea should produce an axiom"
    assert not (out / "axioms" / "unsupported-idea-with-no-snippet-must-be-dropped.md").exists()


def test_cli_build_accepts_ideas_object_wrapper(notes_dir, tmp_path, _no_api_key):
    """An ideas file shaped as {"ideas": [...]} is accepted too."""
    ideas = _write_ideas(tmp_path, {"ideas": _GOOD_IDEAS})
    out = tmp_path / "kpm-out"
    rc = cli.main(["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out)])
    assert rc == 0
    assert list((out / "axioms").glob("*.md"))


def test_cli_build_rejects_missing_ideas_file(notes_dir, tmp_path, capsys, _no_api_key):
    rc = cli.main(["build", str(notes_dir), "--ideas", str(tmp_path / "absent.json"), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert "ideas file not found" in capsys.readouterr().err


def test_cli_build_rejects_bad_json(notes_dir, tmp_path, capsys, _no_api_key):
    bad = tmp_path / "ideas.json"
    bad.write_text("{not valid json", encoding="utf-8")
    rc = cli.main(["build", str(notes_dir), "--ideas", str(bad), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert "could not parse ideas file" in capsys.readouterr().err


def test_cli_build_rejects_missing_input_dir(tmp_path, capsys, _no_api_key):
    ideas = _write_ideas(tmp_path, _GOOD_IDEAS)
    rc = cli.main(["build", str(tmp_path / "nope"), "--ideas", str(ideas), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert "not a directory" in capsys.readouterr().err


def test_cli_build_accepts_numeric_string_generativity(notes_dir, tmp_path, _no_api_key):
    """REVIEW.md M2: a stringly-typed "4.0" keeps its value, not the floor."""
    ideas = _write_ideas(
        tmp_path,
        [
            {
                "statement": "Stringly-typed scores survive coercion.",
                "supporting_source_files": ["alpha.md"],
                "supporting_snippets": ["A thin index over a fat store keeps recall cheap."],
                "confidence": "0.8",
                "generativity": "4.0",
            }
        ],
    )
    out = tmp_path / "kpm-out"
    rc = cli.main(["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out)])
    assert rc == 0
    axiom = next((out / "axioms").glob("*.md")).read_text()
    assert "generativity: 4" in axiom
    assert "confidence: 0.8" in axiom


# --- stale-output guard (REVIEW.md M1) ----------------------------------------


def test_cli_build_rerun_clears_orphan_notes(notes_dir, tmp_path, _no_api_key):
    out = tmp_path / "kpm-out"
    first = _write_ideas(tmp_path, _GOOD_IDEAS)
    assert cli.main(["build", str(notes_dir), "--ideas", str(first), "--out", str(out)]) == 0
    orphan_candidates = {p.name for p in (out / "axioms").glob("*.md")}

    second = tmp_path / "ideas2.json"
    second.write_text(
        json.dumps(
            [
                {
                    "statement": "A completely different second-run claim.",
                    "supporting_source_files": ["alpha.md"],
                    "supporting_snippets": ["A thin index over a fat store keeps recall cheap."],
                    "confidence": 0.7,
                    "generativity": 3,
                }
            ]
        ),
        encoding="utf-8",
    )
    assert cli.main(["build", str(notes_dir), "--ideas", str(second), "--out", str(out)]) == 0

    names = {p.name for p in (out / "axioms").glob("*.md")}
    assert names == {"a-completely-different-second-run-claim.md"}
    assert not (names & orphan_candidates), "first-run axioms must not survive a re-run"
    proc = _lint_clean(out)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_cli_build_refuses_foreign_non_empty_out_dir(notes_dir, tmp_path, capsys, _no_api_key):
    ideas = _write_ideas(tmp_path, _GOOD_IDEAS)
    out = tmp_path / "precious"
    out.mkdir()
    (out / "draft.md").write_text("user data", encoding="utf-8")

    rc = cli.main(["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out)])
    assert rc == 2
    assert "--force" in capsys.readouterr().err
    assert (out / "draft.md").read_text() == "user data"  # nothing deleted
    assert not (out / "knowledge.json").exists()  # nothing written


def test_cli_build_force_writes_into_foreign_dir(notes_dir, tmp_path, _no_api_key):
    ideas = _write_ideas(tmp_path, _GOOD_IDEAS)
    out = tmp_path / "messy"
    out.mkdir()
    (out / "leftover.txt").write_text("x", encoding="utf-8")

    rc = cli.main(["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out), "--force"])
    assert rc == 0
    assert (out / "knowledge.json").is_file()
    assert (out / "leftover.txt").exists()


# --- shared run/build flags (REVIEW.md M6 / L1) --------------------------------


def test_cli_build_max_sources_truncation_warns(notes_dir, tmp_path, capsys, _no_api_key):
    ideas = _write_ideas(tmp_path, _GOOD_IDEAS)
    out = tmp_path / "kpm-out"
    rc = cli.main(
        ["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out), "--max-sources", "1"]
    )
    assert rc == 0
    err = capsys.readouterr().err
    assert "file(s) skipped" in err and "max_sources" in err


def test_cli_build_description_lands_in_manifest(notes_dir, tmp_path, _no_api_key):
    ideas = _write_ideas(tmp_path, _GOOD_IDEAS)
    out = tmp_path / "kpm-out"
    rc = cli.main(
        ["build", str(notes_dir), "--ideas", str(ideas), "--out", str(out), "--description", "Custom blurb."]
    )
    assert rc == 0
    manifest = json.loads((out / "knowledge.json").read_text())
    assert manifest["description"] == "Custom blurb."


def test_run_and_build_share_the_output_flag_set(_no_api_key):
    """REVIEW.md L1: run accepts the same output flags as build."""
    parser = cli._build_parser()
    args = parser.parse_args(
        [
            "run", "notes", "--out", "pkg", "--name", "@kpm/x",
            "--description", "d", "--keep-uncited", "--force", "--max-sources", "5",
        ]
    )
    assert args.description == "d"
    assert args.max_sources == 5
    assert args.force is True
