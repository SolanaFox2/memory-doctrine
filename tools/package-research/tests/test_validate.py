"""Tests for validate — kpm resolution must be portable (no hardcoded paths)."""

from pathlib import Path

from package_research import validate as V
from package_research.assemble import assemble
from package_research.score import ScoredIdea
from package_research.split import split

RUN_DATE = "2026-06-04"


def _pkg(tmp_path):
    axioms, evidence = split(
        [
            ScoredIdea(
                statement="A grounded claim.",
                supporting_source_files=["g.md"],
                supporting_snippets=["snip"],
                confidence=0.7,
                generativity=3,
                rationale="r",
            )
        ]
    )
    assemble(axioms, evidence, tmp_path, run_date=RUN_DATE)
    return tmp_path


def test_validate_runs_lint_and_skips_kpm_when_forced_absent(tmp_path):
    _pkg(tmp_path)
    vr = V.validate(tmp_path, kpm_argv=[])  # force "no kpm"
    assert vr.lint_ok
    assert vr.doctor_ok is None  # skipped cleanly, not failed


def test_resolve_kpm_returns_none_when_absent(monkeypatch):
    monkeypatch.delenv("PACKAGE_RESEARCH_KPM", raising=False)
    monkeypatch.setattr(V.shutil, "which", lambda name: None)
    assert V._resolve_kpm() is None


def test_resolve_kpm_uses_path_binary(monkeypatch):
    monkeypatch.delenv("PACKAGE_RESEARCH_KPM", raising=False)
    monkeypatch.setattr(V.shutil, "which", lambda name: "/usr/bin/kpm" if name == "kpm" else None)
    assert V._resolve_kpm() == ["/usr/bin/kpm"]


def test_resolve_kpm_env_override_js_runs_via_node(tmp_path, monkeypatch):
    cli = tmp_path / "cli.js"
    cli.write_text("// kpm")
    monkeypatch.setenv("PACKAGE_RESEARCH_KPM", str(cli))
    monkeypatch.setattr(V.shutil, "which", lambda name: "/usr/bin/node" if name == "node" else None)
    assert V._resolve_kpm() == ["/usr/bin/node", str(cli)]


def test_no_hardcoded_home_path_in_source():
    # Regression guard for the exact bug the review caught.
    assert "/home/" not in Path(V.__file__).read_text(), "validate.py must not hardcode a home path"


def test_resolve_kpm_warns_and_returns_none_on_missing_override(monkeypatch, capsys):
    # A bad override must NOT silently fall back to a system kpm.
    monkeypatch.setenv("PACKAGE_RESEARCH_KPM", "/no/such/file.js")
    monkeypatch.setattr(V.shutil, "which", lambda name: "/usr/bin/kpm")
    assert V._resolve_kpm() is None
    assert "PACKAGE_RESEARCH_KPM" in capsys.readouterr().err


def test_resolve_kpm_warns_when_js_override_but_no_node(tmp_path, monkeypatch, capsys):
    cli = tmp_path / "cli.js"
    cli.write_text("// kpm")
    monkeypatch.setenv("PACKAGE_RESEARCH_KPM", str(cli))
    monkeypatch.setattr(V.shutil, "which", lambda name: None)  # no node, no kpm
    assert V._resolve_kpm() is None
    assert "node" in capsys.readouterr().err.lower()
