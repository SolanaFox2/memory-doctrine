"""Stack-connection invariants: the tool is wired TO the doctrine.

The tool must not maintain its own fork of the standard's checker — its vendored
``doctrine_lint.py`` must BE the doctrine's canonical ``scripts/doctrine_lint.py``
(single source of truth). If the doctrine's rules change, the tool follows.
"""

from pathlib import Path

import pytest

TOOL_ROOT = Path(__file__).resolve().parents[1]
VENDOR_LINT = TOOL_ROOT / "vendor" / "doctrine_lint.py"
# tool lives at memory-doctrine/tools/package-research; canonical linter at memory-doctrine/scripts.
CANONICAL_LINT = TOOL_ROOT.parents[1] / "scripts" / "doctrine_lint.py"


def test_vendored_linter_exists():
    assert VENDOR_LINT.exists(), "tool must carry a doctrine_lint to vendor into outputs"


def test_vendored_linter_is_the_doctrine_canonical_linter():
    if not CANONICAL_LINT.exists():
        pytest.skip("doctrine canonical linter not found (tool extracted standalone)")
    assert VENDOR_LINT.read_text() == CANONICAL_LINT.read_text(), (
        "vendored linter has DRIFTED from the doctrine's canonical "
        "scripts/doctrine_lint.py — the tool must not fork the standard"
    )
