"""Shared low-level helpers for kpm_builder."""
from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

_SLUG = re.compile(r"[^a-z0-9]+")
_FM_SPLIT = re.compile(r"(?m)^---[ \t]*$")


def atomic_write(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically (tempfile + os.replace)."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def slug(s: str) -> str:
    """Filesystem-safe slug: lowercase, non-alphanumeric runs → single hyphen."""
    return _SLUG.sub("-", s.lower()).strip("-")


def read_frontmatters(directory: str | Path) -> list[dict]:
    """Parse the YAML frontmatter of every ``*.md`` in ``directory`` (line-anchored
    ``---`` split, so a ``---`` inside a value can't truncate it). The single home for
    this logic — reused by graph_index and resolve."""
    out: list[dict] = []
    for f in sorted(Path(directory).glob("*.md")):
        parts = _FM_SPLIT.split(f.read_text(encoding="utf-8"), maxsplit=2)
        if len(parts) >= 3:
            out.append(yaml.safe_load(parts[1]) or {})
    return out
