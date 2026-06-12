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


# --- structured lint failures (REVIEW.md M7 / L7) ---------------------------


def test_lint_failure_yields_structured_violations(tmp_path):
    """A broken note must surface the linter's per-violation errors."""
    _pkg(tmp_path)
    axiom = next((tmp_path / "axioms").glob("*.md"))
    axiom.write_text(axiom.read_text().replace("confidence: 0.7", "confidence: 7.0"))

    vr = V.validate(tmp_path, kpm_argv=[])
    assert not vr.lint_ok
    assert vr.lint_violations
    assert any("confidence" in v for v in vr.lint_violations)


def test_lint_failure_when_shipped_linter_missing(tmp_path):
    """The package must SHIP its validator; a missing copy is a lint failure."""
    _pkg(tmp_path)
    (tmp_path / "scripts" / "doctrine_lint.py").unlink()
    vr = V.validate(tmp_path, kpm_argv=[])
    assert not vr.lint_ok
    assert vr.lint_violations == ["vendored scripts/doctrine_lint.py is missing"]


def test_lint_runs_in_process_not_as_subprocess(tmp_path, monkeypatch):
    """REVIEW.md M7: the lint gate must not depend on subprocess stdout scraping."""

    def _boom(*args, **kwargs):
        raise AssertionError("doctrine_lint must run in-process")

    monkeypatch.setattr(V.subprocess, "run", _boom)
    vr = V.validate(_pkg(tmp_path), kpm_argv=[])  # kpm skipped -> no subprocess at all
    assert vr.lint_ok


# --- kpm doctor timeout (REVIEW.md M8) ---------------------------------------


def test_kpm_doctor_timeout_is_a_doctor_failure_not_a_crash(tmp_path, monkeypatch):
    _pkg(tmp_path)

    def _hang(cmd, **kwargs):
        assert kwargs.get("timeout") == V.SUBPROCESS_TIMEOUT_S
        raise V.subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"])

    monkeypatch.setattr(V.subprocess, "run", _hang)
    vr = V.validate(tmp_path, kpm_argv=["kpm"])
    assert vr.lint_ok  # the lint gate is unaffected
    assert vr.doctor_ok is False
    assert "timed out" in vr.doctor_output
