import sys
from pathlib import Path

import pytest

# Make the src-layout package importable without an editable install
# (the environment is PEP 668 externally-managed).
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

FIXTURE_NOTES = Path(__file__).parent / "fixtures" / "notes"


@pytest.fixture
def notes_dir() -> Path:
    return FIXTURE_NOTES
