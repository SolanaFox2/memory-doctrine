"""Ingest stage — DETERMINISTIC.

Read every ``.md``/``.txt`` file under ``input_dir`` (recursively), strip YAML
frontmatter, split each file into passages on Markdown heading boundaries (then
again on a character cap), and return a flat list of :class:`Candidate` objects.

Each Candidate records the exact ``char_span`` into the *raw* source file such
that ``raw[start:end] == candidate.text`` — so every passage is traceable back
to its origin (doctrine: provenance / index→store).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from .config import Config

SUPPORTED_SUFFIXES = {".md", ".txt"}
_HEADING = re.compile(r"^#{1,6}[ \t]", re.MULTILINE)

# Section headings that carry *process* rather than *knowledge*. We trim these
# from the preserved store so the evidence notes keep findings, not search
# bookkeeping. Deliberately conservative — when in doubt, a passage is kept,
# because the whole point of the store is to NOT lose the user's information.
_NOISE_HEADING_PREFIXES = (
    "methodology",
    "follow-up search",  # "Follow-Up Searches", "Follow-Up Searches (Needed)"
    "follow up search",
    "tool failure",  # "Tool Failure Report"
    "web search attempt",  # "Web Search Attempts"
    "research strategy",  # "Research Strategy (Attempted)"
)


@dataclass(frozen=True)
class Candidate:
    """A raw candidate passage pulled from a source file.

    Attributes:
        text: The passage text, an exact substring of the source file.
        source_file: A **relative path string** (posix form, relative to the
            ingest ``input_dir``) naming the file it came from. Kept as a plain
            ``str`` so the whole pipeline (distill/score/split/assemble) is
            string-consistent and serializes cleanly to YAML/JSON.
        char_span: ``(start, end)`` character offsets into the raw file, so
            ``raw[start:end] == text``.
        section_heading: The heading (lowercased, no ``#``) of the Markdown
            section this passage belongs to — propagated to EVERY chunk of that
            section, even the cap-split tails that carry no heading of their own.
            This lets noise-trimming judge a chunk by its section, not just by
            whether the chunk happens to start with the heading line.
    """

    text: str
    source_file: str
    char_span: Tuple[int, int]
    section_heading: str = ""


def _frontmatter_offset(raw: str) -> int:
    """Return the char offset where the body begins, skipping YAML frontmatter."""
    if not raw.startswith("---"):
        return 0
    # Find the closing delimiter line after the opening one.
    m = re.search(r"^---[ \t]*\r?\n", raw)  # opening
    if not m:
        return 0
    rest_start = m.end()
    close = re.search(r"^---[ \t]*\r?\n?", raw[rest_start:], re.MULTILINE)
    if not close:
        return 0
    return rest_start + close.end()


def _section_spans(raw: str, body_start: int) -> List[Tuple[int, int]]:
    """Split the body into [start, end) spans on heading boundaries."""
    heads = [m.start() for m in _HEADING.finditer(raw) if m.start() >= body_start]
    if not heads:
        return [(body_start, len(raw))]
    spans: List[Tuple[int, int]] = []
    # Any preamble before the first heading is its own section.
    if heads[0] > body_start:
        spans.append((body_start, heads[0]))
    for i, h in enumerate(heads):
        end = heads[i + 1] if i + 1 < len(heads) else len(raw)
        spans.append((h, end))
    return spans


def _split_by_cap(raw: str, start: int, end: int, cap: int) -> List[Tuple[int, int]]:
    """Split a single span into sub-spans each no longer than ``cap`` chars.

    Prefers to break on a whitespace boundary so words are not severed.
    """
    spans: List[Tuple[int, int]] = []
    cur = start
    while end - cur > cap:
        cut = cur + cap
        # Walk back to the last whitespace within the window.
        win = raw[cur:cut]
        ws = win.rfind(" ")
        nl = win.rfind("\n")
        boundary = max(ws, nl)
        if boundary <= 0:
            boundary = cap  # no whitespace; hard cut
        spans.append((cur, cur + boundary))
        cur = cur + boundary
        while cur < end and raw[cur] in " \n\t":
            cur += 1
    if cur < end:
        spans.append((cur, end))
    return spans


def _relative_source(path: Path, input_dir: Path) -> str:
    """Return ``path`` as a posix string relative to ``input_dir``.

    Falls back to the file's bare *basename* if ``path`` is not under
    ``input_dir`` — NEVER an absolute path, which would leak the local
    filesystem layout into the package's ``ref:``/``url:`` fields (REVIEW.md M5).
    """
    try:
        return path.relative_to(input_dir).as_posix()
    except ValueError:
        return path.name


def _passages_for_file(path: Path, input_dir: Path, cap: int) -> List[Candidate]:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # One non-UTF-8 note must not abort the whole run; skip it loudly.
        print(f"warning: {path} is not valid UTF-8 — skipped", file=sys.stderr)
        return []
    body_start = _frontmatter_offset(raw)
    source = _relative_source(path, input_dir)
    out: List[Candidate] = []
    for s, e in _section_spans(raw, body_start):
        # Read the section heading once and stamp it on every sub-chunk, so a
        # long process section is recognised as noise across all its cap-split
        # tails — not just the first chunk that carries the heading line.
        section_heading = passage_heading(raw[s:e])
        for ss, ee in _split_by_cap(raw, s, e, cap):
            text = raw[ss:ee]
            if not text.strip():
                continue
            out.append(
                Candidate(
                    text=text,
                    source_file=source,
                    char_span=(ss, ee),
                    section_heading=section_heading,
                )
            )
    return out


def _iter_source_files(input_dir: Path) -> List[Path]:
    """Supported source files under ``input_dir``, sorted.

    Symlinks resolving *outside* the input tree are skipped with a stderr
    warning (REVIEW.md M5): following them would pull foreign content into the
    package and their locators could not be expressed relative to ``input_dir``.
    Symlinks resolving inside the tree are kept.
    """
    root = input_dir.resolve()
    out: List[Path] = []
    for p in sorted(input_dir.rglob("*")):
        if not (p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES):
            continue
        if p.is_symlink():
            try:
                resolved = p.resolve(strict=True)
            except OSError:
                continue  # broken link — nothing to read
            if not resolved.is_relative_to(root):
                print(
                    f"warning: {p} is a symlink resolving outside {input_dir} — skipped",
                    file=sys.stderr,
                )
                continue
        out.append(p)
    return out


def passage_heading(text: str) -> str:
    """Return the passage's Markdown heading (without ``#``), lowercased.

    A passage produced by the chunker starts at a heading boundary, so the
    heading is the first non-empty line when it begins with ``#``. Returns ``""``
    when the passage has no leading heading (e.g. preamble or a cap-split tail).
    """
    for line in text.lstrip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip().lower()
        return ""
    return ""


def _heading_is_noise(heading: str) -> bool:
    """True if a (lowercased, ``#``-stripped) heading names a process section."""
    if not heading:
        return False
    return any(heading.startswith(prefix) for prefix in _NOISE_HEADING_PREFIXES)


def is_noise_passage(text: str) -> bool:
    """True if the passage is a *process* section we trim from the store.

    Matches the passage's own heading against :data:`_NOISE_HEADING_PREFIXES`.
    Headingless passages are never noise (kept by default). For cap-split tails
    that carry no heading, :func:`passages_by_source` consults the passage's
    ``section_heading`` instead — so a long process section is fully trimmed.
    """
    return _heading_is_noise(passage_heading(text))


def passages_by_source(candidates: List[Candidate], *, drop_noise: bool = True) -> Dict[str, List[str]]:
    """Group candidate passages by source **relative path**, preserving content.

    Returns ``{relative_path: [passage, ...]}`` in source order, exact-duplicate
    passages removed. With ``drop_noise`` (default), process sections
    (methodology, follow-up searches, tool-failure reports) are trimmed so the
    store keeps findings rather than bookkeeping — judged by each passage's
    ``section_heading`` so cap-split tails of a long process section are dropped
    too, not just its first chunk.

    Keyed by the full relative path (not basename) so two files that share a
    basename in different folders (``2025/notes.md`` vs ``2026/notes.md``) stay
    distinct rather than silently merging. :func:`split.split` resolves an
    axiom's cited source against these keys, with an unambiguous-basename
    fallback for agents that cite bare filenames.
    """
    grouped: Dict[str, List[str]] = {}
    seen: Dict[str, set] = {}
    for cand in candidates:
        heading = cand.section_heading or passage_heading(cand.text)
        if drop_noise and _heading_is_noise(heading):
            continue
        text = cand.text.strip()
        if not text:
            continue
        key = cand.source_file
        bucket = grouped.setdefault(key, [])
        seen_set = seen.setdefault(key, set())
        if text in seen_set:
            continue
        seen_set.add(text)
        bucket.append(text)
    return grouped


def ingest(config: Config) -> List[Candidate]:
    """Read + chunk all supported source files into ordered Candidates."""
    input_dir = Path(config.input_dir)
    if not input_dir.is_dir():
        raise NotADirectoryError(f"input_dir is not a directory: {input_dir}")

    files = _iter_source_files(input_dir)
    if not files:
        # An empty corpus must be distinguishable from "all refuted" (REVIEW.md L2).
        print(
            f"warning: no .md/.txt source files found under {input_dir} — "
            "the resulting package will be empty.",
            file=sys.stderr,
        )
    if len(files) > config.max_sources:
        # Never truncate silently — say exactly what was dropped (no hidden caps).
        print(
            f"warning: {len(files)} source files found; ingesting the first "
            f"{config.max_sources} (max_sources). {len(files) - config.max_sources} "
            f"file(s) skipped — their content will be ABSENT from the package.",
            file=sys.stderr,
        )
        files = files[: config.max_sources]

    candidates: List[Candidate] = []
    for path in files:
        candidates.extend(_passages_for_file(path, input_dir, config.max_chunk_chars))
    return candidates
