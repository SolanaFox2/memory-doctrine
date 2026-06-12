"""Validate stage — run the deterministic gates against an assembled package.

Two gates against ``output_dir``:

1. **doctrine_lint** (always, in-process). Imports the vendored linter module
   and calls its ``check()`` directly (REVIEW.md M7) — no subprocess, no
   scraping another process's output format. This is the doctrine's structural
   validator: confidence/generativity bounds, every axiom cites >=1 resolving
   evidence id, every relation has a matching wikilink, evidence notes carry
   ``url`` + ``verified``. The package must still *ship* its own
   ``scripts/doctrine_lint.py`` (it self-validates), and a byte-identity test
   keeps that copy equal to the imported module.

2. **kpm doctor** (best-effort, subprocess). If the kpm CLI is present, run
   ``kpm doctor`` from the package directory with a hard timeout (REVIEW.md
   M8) — a hung kpm becomes a doctor failure, never a hung run. Absence is
   tolerated — ``doctor_ok`` is ``None`` when kpm is unavailable.

No LLM here. Pure orchestration over an already-written package.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

#: Hard cap on any validation subprocess (a hung `kpm` must not hang the run).
SUBPROCESS_TIMEOUT_S = 120


@dataclass
class ValidationResult:
    """Outcome of the validation gates."""

    lint_ok: bool
    lint_violations: List[str] = field(default_factory=list)
    # None => kpm was not available and was skipped. True/False => it ran.
    doctor_ok: Optional[bool] = None
    doctor_output: str = ""


def _run_doctrine_lint(output_dir: Path) -> tuple[bool, List[str]]:
    """Run the doctrine linter in-process against the package (REVIEW.md M7).

    Imports the vendored linter module and calls its ``check()`` directly. The
    frozen linter reports violations only by printing, so its stdout is
    captured via ``redirect_stdout`` and the ``  - <violation>`` lines are
    collected — same line shape, but now produced and consumed inside one
    process pinned to one module version, not scraped across a subprocess
    boundary. The shipped ``scripts/doctrine_lint.py`` must still exist (the
    package self-validates); a wiring test keeps it byte-identical to the
    imported module.
    """
    if not (output_dir / "scripts" / "doctrine_lint.py").is_file():
        return False, ["vendored scripts/doctrine_lint.py is missing"]
    try:
        from .vendor import doctrine_lint
    except ImportError as exc:  # e.g. pyyaml missing
        return False, [f"doctrine_lint could not be imported: {exc}"]

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = doctrine_lint.check(output_dir)
    except Exception as exc:  # a broken package must fail the gate, not the run
        return False, [f"doctrine_lint crashed: {exc}"]
    if rc == 0:
        return True, []

    violations: List[str] = []
    for line in buf.getvalue().splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            violations.append(stripped[2:])
    if not violations:
        # Surface whatever the linter printed so failures aren't silent.
        violations = [ln for ln in buf.getvalue().splitlines() if ln.strip()]
    return False, violations


def _resolve_kpm() -> Optional[List[str]]:
    """Resolve how to invoke ``kpm`` (an argv prefix), or ``None`` if unavailable.

    Portable — NO hardcoded paths, so the published tool works on any machine.
    Resolution order:

    1. ``$PACKAGE_RESEARCH_KPM`` — an explicit override: a ``kpm`` executable, or
       a ``cli.js`` (run via ``node``).
    2. a ``kpm`` executable on ``PATH``.

    Returns e.g. ``["kpm"]`` or ``["node", "/path/to/cli.js"]``; ``None`` when kpm
    is not found (``kpm doctor`` is then skipped, which is tolerated).
    """
    override = os.environ.get("PACKAGE_RESEARCH_KPM")
    if override:
        # An explicit override that can't be resolved is a user mistake — say so,
        # rather than silently falling back to a different kpm on PATH.
        p = Path(override)
        if not p.is_file():
            print(
                f"warning: PACKAGE_RESEARCH_KPM={override!r} is not a file; skipping kpm doctor.",
                file=sys.stderr,
            )
            return None
        if p.suffix == ".js":
            node = shutil.which("node")
            if node:
                return [node, str(p)]
            print(
                "warning: PACKAGE_RESEARCH_KPM points to a .js file but 'node' is not on PATH; skipping kpm doctor.",
                file=sys.stderr,
            )
            return None
        if os.access(p, os.X_OK):
            return [str(p)]
        print(
            f"warning: PACKAGE_RESEARCH_KPM={override!r} is not executable; skipping kpm doctor.",
            file=sys.stderr,
        )
        return None
    kpm = shutil.which("kpm")
    if kpm:
        return [kpm]
    return None


def _run_kpm_doctor(output_dir: Path, kpm_argv: List[str]) -> tuple[bool, str]:
    """Run ``kpm doctor`` from inside the package directory.

    A hung kpm is cut off after :data:`SUBPROCESS_TIMEOUT_S` and reported as a
    doctor *failure*, never as a crash or a hung run (REVIEW.md M8).
    """
    try:
        proc = subprocess.run(
            [*kpm_argv, "doctor"],
            cwd=str(output_dir),
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return False, f"kpm doctor timed out after {SUBPROCESS_TIMEOUT_S}s"
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()


def validate(output_dir: Path, *, kpm_argv: Optional[List[str]] = None) -> ValidationResult:
    """Validate an assembled package directory.

    Args:
        output_dir: The assembled kpm package directory.
        kpm_argv: How to invoke kpm (argv prefix). Defaults to auto-resolution
            via :func:`_resolve_kpm` (env override, then ``PATH``); tolerated
            absent.

    Returns:
        A :class:`ValidationResult`. ``doctor_ok`` is ``None`` when kpm is absent.
    """
    output_dir = Path(output_dir)
    lint_ok, violations = _run_doctrine_lint(output_dir)

    argv = kpm_argv if kpm_argv is not None else _resolve_kpm()
    doctor_ok: Optional[bool] = None
    doctor_output = ""
    if argv:
        doctor_ok, doctor_output = _run_kpm_doctor(output_dir, argv)

    return ValidationResult(
        lint_ok=lint_ok,
        lint_violations=violations,
        doctor_ok=doctor_ok,
        doctor_output=doctor_output,
    )
