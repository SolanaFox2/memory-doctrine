"""Assemble stage — DETERMINISTIC. Write a valid kpm knowledge package.

Takes the in-memory ``AxiomNote`` / ``EvidenceNote`` objects from the split
stage and writes a complete, doctrine-lint-clean kpm package to
``config.output_dir``:

* ``knowledge.json`` — the package manifest.
* ``axioms/<id>.md`` — one thin index note per axiom, frontmatter matching the
  doctrine schema exactly, body carrying a ``[[evidence-id]]`` wikilink per
  cited evidence id.
* ``evidence/<id>.md`` — one store note per distinct source, frontmatter with
  the doctrine-required ``url`` + ``verified`` fields, body holding the
  snippet(s).
* ``scripts/doctrine_lint.py`` — a vendored copy of the doctrine's validator so
  the package self-validates.
* ``README.md`` — the entrypoint, a short generated overview.

No LLM here — this stage is pure I/O over already-decided data, so it is fully
deterministic and testable. The ``run_date`` (the evidence ``verified`` date) is
passed IN, never read from ``datetime.now()``, so output is reproducible.

Invariants enforced (so the output always passes ``doctrine_lint``):
* Only axioms with >=1 cited evidence id are emitted (the rest are dropped).
* Every evidence id an emitted axiom cites has a written evidence note.
* ``relations`` carries all five keys, each ``[]`` (``contradicts`` stays ``[]``).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .split import AxiomNote, EvidenceNote, _slugify

# The vendored validator ships inside the package (so it survives a wheel/pip
# install, not just an editable checkout). A test keeps it byte-identical to the
# doctrine's canonical scripts/doctrine_lint.py; that canonical path is the
# fallback for the in-repo case where someone deletes the vendored copy.
_PARENTS = Path(__file__).resolve().parents
_VENDOR_LINT = _PARENTS[0] / "vendor" / "doctrine_lint.py"
_CANONICAL_LINT = _PARENTS[4] / "scripts" / "doctrine_lint.py" if len(_PARENTS) > 4 else None

_RELATION_KEYS = (
    "derives-from",
    "supports",
    "generalizes",
    "contradicts",
    "applies-to-kpm",
)


@dataclass
class AssembleResult:
    """What assemble wrote: the output dir and the notes actually emitted."""

    output_dir: Path
    axioms_written: List[str]
    evidence_written: List[str]


def _yaml_str(value) -> str:
    """Emit a YAML-safe double-quoted scalar (coerces non-str, e.g. Path)."""
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{escaped}"'


def _yaml_id(value: str) -> str:
    """Emit a bare YAML scalar for slug-style ids (no quoting needed)."""
    return value


def build_knowledge_json(
    *,
    name: str,
    description: str,
    version: str = "0.1.0",
) -> dict:
    """The kpm manifest, matching the doctrine package's shape."""
    return {
        "name": name,
        "version": version,
        "description": description,
        "license": "CC-BY-4.0",
        "type": "knowledge-package",
        "files": ["**/*.md", "!wiki/**", "!knowledge_modules/**"],
        "entrypoint": "README.md",
        "knowledgeDependencies": {},
    }


def render_axiom(axiom: AxiomNote, evidence_ids: List[str]) -> str:
    """Render an axiom note: doctrine-schema frontmatter + wikilinked body.

    ``evidence_ids`` is the *filtered* list of evidence ids that actually have a
    written note — every one gets a ``[[id]]`` wikilink in the body so the lint's
    relation/wikilink checks (and human navigation) resolve.
    """
    rel_lines = "\n".join(f"  {k}: []" for k in _RELATION_KEYS)
    ev_inline = "[" + ", ".join(evidence_ids) + "]"

    fm = (
        "---\n"
        f"id: {_yaml_id(axiom.id)}\n"
        "type: axiom\n"
        f"title: {_yaml_str(axiom.title)}\n"
        f"statement: {_yaml_str(axiom.statement)}\n"
        f"domain: {_yaml_str('distilled')}\n"
        f"generativity: {axiom.generativity}\n"
        f"confidence: {axiom.confidence}\n"
        "status: candidate\n"
        "relations:\n"
        f"{rel_lines}\n"
        f"evidence: {ev_inline}\n"
        f"provenance: {_yaml_str(axiom.provenance)}\n"
        "---\n"
    )

    links = ", ".join(f"[[{eid}]]" for eid in evidence_ids)
    body = f"\n# {axiom.title}\n\n{axiom.statement}\n\nEvidence: {links}.\n"
    return fm + body


def render_evidence(evidence: EvidenceNote, *, run_date: str) -> str:
    """Render an evidence note: doctrine-schema frontmatter + snippet body.

    ``ref`` and ``url`` both derive from the source locator; ``verified`` is the
    passed-in ``run_date`` (never ``datetime.now()``), keeping output reproducible.
    ``supports`` lists the axiom ids that rest on this evidence.
    """
    supports_inline = "[" + ", ".join(evidence.supports) + "]"
    fm = (
        "---\n"
        f"id: {_yaml_id(evidence.id)}\n"
        "type: evidence\n"
        f"ref: {_yaml_str(evidence.ref)}\n"
        f"url: {_yaml_str(evidence.ref)}\n"
        f"verified: {run_date}\n"
        f"supports: {supports_inline}\n"
        "---\n"
    )
    body_snippets = evidence.body or "(snippet unavailable)"
    body = f"\n# Evidence: {evidence.ref}\n\n{body_snippets}\n"
    return fm + body


def _readme_bullet(title: str, statement: str) -> str:
    """A README list bullet that never repeats the title inside the statement.

    ``title`` is the statement's leading clause (see ``split._title_from_statement``),
    so a naive ``**title** — statement`` duplicates that clause. When the statement
    just is the title, emit the bold title alone; when it merely starts with it,
    show the bold title and only the remainder.
    """
    title = title.strip()
    statement = statement.strip()
    if statement == title:
        return f"**{statement}**"
    if statement.startswith(title):
        remainder = statement[len(title) :].lstrip(" :;,—-")
        # Real elaboration after the lead clause: keep bold title + remainder.
        if any(ch.isalnum() for ch in remainder):
            return f"**{title}** — {remainder}"
        # Only trailing punctuation differed (e.g. the period): bold the whole.
        return f"**{statement}**"
    return f"**{title}** — {statement}"


def render_readme(name: str, description: str, axioms: List[AxiomNote]) -> str:
    """A short entrypoint overview listing the emitted axioms (no dangling links)."""
    lines = [
        f"# {name}",
        "",
        description,
        "",
        "## Axioms",
        "",
    ]
    if axioms:
        for ax in axioms:
            lines.append(f"- {_readme_bullet(ax.title, ax.statement)}")
    else:
        lines.append("_(no axioms survived verification)_")
    lines.append("")
    return "\n".join(lines)


def _ref_slug(source: str, used: set) -> str:
    """A unique reference-note id from a source path (disambiguated -2, -3)."""
    base = _slugify(Path(source).with_suffix("").as_posix(), max_words=12) or "ref"
    candidate, n = base, 1
    while candidate in used:
        n += 1
        candidate = f"{base}-{n}"
    used.add(candidate)
    return candidate


def render_reference(ref_id: str, source: str, passages: List[str], *, run_date: str) -> str:
    """Render an *uncited* source as a reference note: preserved, clearly flagged.

    Same preserved body as an evidence note, but ``type: reference`` and
    ``status: uncited`` — no axiom rests on it. Lives in ``reference/`` (which the
    doctrine linter ignores), so it preserves content without claiming evidence.
    """
    body = "\n\n".join(p.strip() for p in passages if p.strip()) or "(no content)"
    fm = (
        "---\n"
        f"id: {ref_id}\n"
        "type: reference\n"
        f"ref: {_yaml_str(source)}\n"
        f"url: {_yaml_str(source)}\n"
        f"verified: {run_date}\n"
        "status: uncited\n"
        "---\n"
    )
    header = f"\n# Reference: {source}\n\n*No axiom cites this source yet — preserved here so nothing is lost.*\n\n"
    return fm + header + body + "\n"


def write_reference_notes(uncited: Dict[str, List[str]], output_dir: Path, *, run_date: str) -> List[str]:
    """Write the uncited sources into ``reference/``; return the ids written.

    No-op (returns ``[]``) when there is nothing uncited. The linter ignores this
    directory, so reference notes never affect the validation gates.
    """
    if not uncited:
        return []
    ref_dir = Path(output_dir) / "reference"
    ref_dir.mkdir(parents=True, exist_ok=True)
    used: set = set()
    written: List[str] = []
    for source in sorted(uncited):
        rid = _ref_slug(source, used)
        (ref_dir / f"{rid}.md").write_text(
            render_reference(rid, source, uncited[source], run_date=run_date),
            encoding="utf-8",
        )
        written.append(rid)
    return written


def _vendor_lint_source() -> str:
    """Read the canonical doctrine_lint.py to copy into each output package.

    Tries the vendored symlink first, then the doctrine's canonical
    ``scripts/doctrine_lint.py``. Raises a clear, actionable error (not a bare
    ``FileNotFoundError``) if neither is readable — e.g. the tool was extracted
    on its own or installed as a non-editable wheel that dropped the symlink.
    """
    for candidate in (_VENDOR_LINT, _CANONICAL_LINT):
        if candidate is None:
            continue
        try:
            return candidate.read_text(encoding="utf-8")
        except OSError:
            continue
    raise FileNotFoundError(
        "doctrine_lint.py not found. Run package-research from a full checkout of "
        "the memory-doctrine repo, where tools/package-research/vendor/"
        "doctrine_lint.py links to scripts/doctrine_lint.py (an editable install, "
        "`pip install -e .`, is the supported setup)."
    )


def assemble(
    axioms: List[AxiomNote],
    evidence: List[EvidenceNote],
    output_dir: Path,
    *,
    run_date: str,
    name: str = "@kpm/distilled-research",
    description: str = "A doctrine-grounded knowledge package distilled from source notes.",
    version: str = "0.1.0",
) -> AssembleResult:
    """Write the kpm package to ``output_dir`` deterministically.

    Args:
        axioms: Axiom notes from split.
        evidence: Evidence notes from split.
        output_dir: Destination package directory (created if missing).
        run_date: ``YYYY-MM-DD`` written as each evidence note's ``verified``
            date. Passed in (never ``datetime.now()``) for reproducibility.
        name/description/version: Package manifest fields.

    Returns:
        An :class:`AssembleResult` naming what was emitted.
    """
    output_dir = Path(output_dir)
    (output_dir / "axioms").mkdir(parents=True, exist_ok=True)
    (output_dir / "evidence").mkdir(parents=True, exist_ok=True)
    (output_dir / "scripts").mkdir(parents=True, exist_ok=True)

    evidence_by_id = {e.id: e for e in evidence}

    # Decide which axioms survive: must cite >=1 evidence id that has a note.
    emitted_axioms: List[AxiomNote] = []
    needed_evidence_ids: set[str] = set()
    axiom_to_evids: dict[str, List[str]] = {}
    for ax in axioms:
        resolvable = [eid for eid in ax.evidence if eid in evidence_by_id]
        if not resolvable:
            continue  # drop axioms with no written evidence (doctrine: >=1)
        emitted_axioms.append(ax)
        axiom_to_evids[ax.id] = resolvable
        needed_evidence_ids.update(resolvable)

    # Write axioms.
    axioms_written: List[str] = []
    for ax in emitted_axioms:
        (output_dir / "axioms" / f"{ax.id}.md").write_text(render_axiom(ax, axiom_to_evids[ax.id]), encoding="utf-8")
        axioms_written.append(ax.id)

    # Write only the evidence notes that an emitted axiom actually cites.
    evidence_written: List[str] = []
    for eid in sorted(needed_evidence_ids):
        ev = evidence_by_id[eid]
        # Trim supports to axioms that were actually emitted.
        ev_supports = [a for a in ev.supports if a in axiom_to_evids]
        ev_copy = EvidenceNote(
            id=ev.id,
            type=ev.type,
            ref=ev.ref,
            supports=ev_supports,
            snippets=list(ev.snippets),
        )
        (output_dir / "evidence" / f"{eid}.md").write_text(
            render_evidence(ev_copy, run_date=run_date), encoding="utf-8"
        )
        evidence_written.append(eid)

    # Manifest, README, and the vendored self-validator.
    (output_dir / "knowledge.json").write_text(
        json.dumps(
            build_knowledge_json(name=name, description=description, version=version),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(render_readme(name, description, emitted_axioms), encoding="utf-8")
    (output_dir / "scripts" / "doctrine_lint.py").write_text(_vendor_lint_source(), encoding="utf-8")

    return AssembleResult(
        output_dir=output_dir,
        axioms_written=axioms_written,
        evidence_written=evidence_written,
    )
