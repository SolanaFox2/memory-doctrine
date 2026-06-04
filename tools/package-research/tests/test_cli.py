"""CLI tests — the ``run`` path with the LLM fully MOCKED.

These tests must pass with NO ``ANTHROPIC_API_KEY`` set. We monkeypatch the
CLI's ``_make_llm`` factory so the real Anthropic client is never constructed;
instead a fake provider answers ``complete_json`` by dispatching on the schema
(distill vs score vs verify). The deterministic stages (ingest/split/assemble/
validate) all run for real, so the test asserts a real package directory is
produced and that it is doctrine-lint clean.
"""

import subprocess
import sys

import pytest
from package_research import cli
from package_research.distill import DISTILL_SCHEMA
from package_research.score import SCORE_SCHEMA
from package_research.verify import VERIFY_SCHEMA

# Distilled ideas grounded in the fixture sources (basenames + verbatim snippets
# copied from tests/fixtures/notes). One idea is deliberately weak so verify
# refutes it — proving the kept-count is smaller than the distilled-count.
_DISTILLED = {
    "ideas": [
        {
            "statement": "Retrieval is energy-descent pattern completion over a content-addressable store.",
            "supporting_source_files": ["alpha.md"],
            "supporting_snippets": ["Retrieval is energy-descent pattern completion over a content-addressable store."],
        },
        {
            "statement": "A thin index over a fat store keeps recall cheap.",
            "supporting_source_files": ["alpha.md"],
            "supporting_snippets": ["A thin index over a fat store keeps recall cheap."],
        },
        {
            "statement": "Confidence is earned by evidence and never inferred from fluency.",
            "supporting_source_files": ["beta.txt"],
            "supporting_snippets": [
                "Confidence is earned by evidence and is revisable.",
            ],
        },
        {
            "statement": "Unsupported overreaching claim with no real backing.",
            "supporting_source_files": ["beta.txt"],
            "supporting_snippets": ["Confidence is a credence that changes only when evidence changes."],
        },
    ]
}


class _FakeLLM:
    """A stand-in for LLMClient: dispatches complete_json on the schema."""

    def complete_json(self, prompt: str, schema: dict) -> dict:
        if schema is DISTILL_SCHEMA:
            return _DISTILLED
        if schema is SCORE_SCHEMA:
            return {"confidence": 0.8, "generativity": 4, "rationale": "snippets converge"}
        if schema is VERIFY_SCHEMA:
            if "Unsupported overreaching claim" in prompt:
                return {
                    "survives": False,
                    "reason": "snippet does not establish the claim",
                    "adjusted_confidence": 0.1,
                }
            return {
                "survives": True,
                "reason": "snippet establishes the claim",
                "adjusted_confidence": 0.75,
            }
        raise AssertionError(f"unexpected schema: {schema}")


@pytest.fixture
def _no_api_key(monkeypatch):
    """Guarantee the test runs with NO API key present."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def _fake_llm(monkeypatch):
    """Replace the CLI's LLM factory so no real client / API key is needed."""
    monkeypatch.setattr(cli, "_make_llm", lambda config: _FakeLLM())


def test_cli_run_produces_lint_clean_package(notes_dir, tmp_path, capsys, _no_api_key, _fake_llm):
    out = tmp_path / "kpm-out"

    rc = cli.main(["run", str(notes_dir), "--out", str(out), "--name", "@kpm/test"])

    assert rc == 0, "lint-clean run must exit 0"

    # A real package directory was produced.
    assert (out / "knowledge.json").is_file()
    assert (out / "README.md").is_file()
    axiom_files = list((out / "axioms").glob("*.md"))
    evidence_files = list((out / "evidence").glob("*.md"))
    assert axiom_files, "at least one axiom note should be written"
    assert evidence_files, "evidence notes should be written"

    # The refuted idea must not have produced an axiom note.
    assert not (out / "axioms" / "unsupported-overreaching-claim-with-no-real-backing.md").exists()

    # The package is doctrine-lint clean (run the vendored linter directly).
    lint = out / "scripts" / "doctrine_lint.py"
    assert lint.is_file()
    proc = subprocess.run([sys.executable, str(lint), str(out)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    # The summary reports the pipeline counts and a clean lint.
    summary = capsys.readouterr().out
    assert "candidates ingested" in summary
    assert "kept after verify" in summary
    assert "doctrine lint       : OK" in summary


def test_cli_run_rejects_missing_input_dir(tmp_path, capsys, _no_api_key, _fake_llm):
    missing = tmp_path / "does-not-exist"
    rc = cli.main(["run", str(missing), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert "not a directory" in capsys.readouterr().err


def test_cli_run_requires_api_key_when_unmocked(notes_dir, tmp_path, monkeypatch, capsys):
    """Without a key AND without the fake, the run aborts with a clear error."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rc = cli.main(["run", str(notes_dir), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert "ANTHROPIC_API_KEY" in capsys.readouterr().err


def test_cli_no_command_prints_help(capsys):
    rc = cli.main([])
    assert rc == 2
    out = capsys.readouterr().out
    assert "package-research" in out
    assert "run" in out
