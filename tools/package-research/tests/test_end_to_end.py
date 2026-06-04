"""End-to-end test: ingest -> distill -> score -> verify -> split -> assemble.

Only the three LLM stages (distill, score, verify) are mocked; every
deterministic stage runs for real. After assembling the package we run the REAL
vendored ``doctrine_lint.py`` (as a subprocess, the same one shipped inside the
package) against the output and assert **0 violations** — proving the generated
package is doctrine-lint clean with NO API key.
"""

import subprocess
import sys

from package_research.assemble import assemble
from package_research.config import Config
from package_research.distill import distill
from package_research.ingest import ingest, passages_by_source
from package_research.score import score
from package_research.split import split
from package_research.validate import validate
from package_research.verify import verify

RUN_DATE = "2026-06-03"

# Distilled ideas grounded in the fixture sources. The distill stage renders
# candidates by file *basename*, so the mock attaches basenames as sources and
# verbatim snippets copied from the fixtures.
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
                "It must never be inferred from fluency",
            ],
        },
        {
            # This one will be REFUTED by the verify mock and must not appear.
            "statement": "Unsupported overreaching claim with no real backing.",
            "supporting_source_files": ["beta.txt"],
            "supporting_snippets": ["Confidence is a credence that changes only when evidence changes."],
        },
    ]
}


def _mock_distill(prompt, schema):
    return _DISTILLED


def _mock_score(prompt, schema):
    # High confidence for grounded ideas; the verify stage will adjust/refute.
    return {"confidence": 0.8, "generativity": 4, "rationale": "snippets converge"}


def _mock_verify(prompt, schema):
    # Refute the deliberately-weak overreaching claim; keep the rest, down-scored.
    if "Unsupported overreaching claim" in prompt:
        return {"survives": False, "reason": "snippet does not establish the claim", "adjusted_confidence": 0.1}
    return {"survives": True, "reason": "snippet establishes the claim", "adjusted_confidence": 0.75}


def test_end_to_end_produces_doctrine_lint_clean_package(notes_dir, tmp_path):
    out = tmp_path / "kpm-out"

    config = Config(input_dir=notes_dir, output_dir=out)

    # --- pipeline (LLM stages mocked, everything else real) ---
    candidates = ingest(config)
    assert candidates, "ingest should find fixture passages"

    ideas = distill(candidates, _mock_distill)
    scored = score(ideas, _mock_score)
    verified = verify(scored, _mock_verify)
    axioms, evidence = split(verified, passages_by_source(candidates))
    result = assemble(axioms, evidence, out, run_date=RUN_DATE)

    # The refuted idea must have been dropped before assembly.
    assert "unsupported-overreaching-claim-with-no-real-backing" not in result.axioms_written
    assert result.axioms_written, "at least one axiom should survive"
    assert result.evidence_written, "evidence notes should be written"

    # --- run the REAL vendored doctrine_lint.py against the output ---
    lint = out / "scripts" / "doctrine_lint.py"
    assert lint.is_file(), "package must self-validate (vendored doctrine_lint.py)"
    proc = subprocess.run(
        [sys.executable, str(lint), str(out)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, "doctrine_lint must pass with 0 violations:\n" + proc.stdout + proc.stderr
    assert "0 violations" in proc.stdout


def test_end_to_end_validate_reports_clean(notes_dir, tmp_path):
    out = tmp_path / "kpm-out2"
    config = Config(input_dir=notes_dir, output_dir=out)

    candidates = ingest(config)
    ideas = distill(candidates, _mock_distill)
    scored = score(ideas, _mock_score)
    verified = verify(scored, _mock_verify)
    axioms, evidence = split(verified, passages_by_source(candidates))
    assemble(axioms, evidence, out, run_date=RUN_DATE)

    vr = validate(out)
    assert vr.lint_ok, f"lint violations: {vr.lint_violations}"
    assert vr.lint_violations == []
    # kpm doctor is best-effort: None (absent) or True (clean) are both fine here.
    assert vr.doctor_ok in (None, True), f"kpm doctor failed: {vr.doctor_output}"
