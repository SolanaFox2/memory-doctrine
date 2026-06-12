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
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .cluster import ClusterNote, render_cluster
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


#: The note dirs a package owns — the ones prepare_output_dir may clear.
_PACKAGE_SUBDIRS = ("axioms", "evidence", "reference", "clusters")


class OutputDirError(RuntimeError):
    """The output dir is non-empty and not a package this tool produced."""


def prepare_output_dir(output_dir: Path, *, force: bool = False) -> None:
    """Make ``output_dir`` safe to assemble into (REVIEW.md M1).

    Assemble writes in place, so re-running over a previous package would leave
    notes whose ids no longer exist — stale orphans that pollute (and can fail)
    the lint. A directory is recognizably *ours* when it carries a
    ``knowledge.json``; then the package's own note dirs (``axioms/``,
    ``evidence/``, ``reference/``, ``clusters/``) are cleared of ``*.md`` before
    the rewrite. A non-empty directory that is NOT a recognizable package is
    someone's data: raise :class:`OutputDirError` unless ``force`` — never
    silently delete user files. A missing or empty directory is a no-op.
    """
    output_dir = Path(output_dir)
    if not output_dir.is_dir() or not any(output_dir.iterdir()):
        return
    if not (output_dir / "knowledge.json").is_file() and not force:
        raise OutputDirError(
            f"output dir {output_dir} is non-empty and not a package this tool "
            "produced (no knowledge.json). Refusing to write into it — choose "
            "an empty directory or pass --force."
        )
    for sub in _PACKAGE_SUBDIRS:
        d = output_dir / sub
        if not d.is_dir():
            continue
        for stale in d.glob("*.md"):
            stale.unlink()


@dataclass
class AssembleResult:
    """What assemble wrote: the output dir and the notes actually emitted."""

    output_dir: Path
    axioms_written: List[str]
    evidence_written: List[str]
    clusters_written: List[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.clusters_written is None:
            self.clusters_written = []


def _yaml_str(value) -> str:
    """Emit a YAML-safe double-quoted scalar (coerces non-str, e.g. Path).

    All whitespace control characters (``\\n``, ``\\r``, ``\\t``) collapse to a
    plain space so no raw control byte lands in the frontmatter (REVIEW.md L5).
    """
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    escaped = re.sub(r"[\n\r\t]", " ", escaped)
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
    relation/wikilink checks (and human navigation) resolve. The axiom's typed
    relations (from the relate pass) are rendered into the frontmatter, and
    every relation target gets a matching ``[[wikilink]]`` in the body — the
    doctrine's value lives in these connections (REVIEW.md EFF-1).
    """
    relations = axiom.relations or {}
    rel_lines = "\n".join(
        f"  {k}: [{', '.join(relations.get(k) or [])}]" for k in _RELATION_KEYS
    )
    ev_inline = "[" + ", ".join(evidence_ids) + "]"

    fm = (
        "---\n"
        f"id: {_yaml_id(axiom.id)}\n"
        "type: axiom\n"
        + (f"cluster: {axiom.cluster}\n" if getattr(axiom, "cluster", None) else "")
        + f"title: {_yaml_str(axiom.title)}\n"
        f"statement: {_yaml_str(axiom.statement)}\n"
        f"domain: {_yaml_str('distilled')}\n"
        f"generativity: {axiom.generativity}\n"
        f"confidence: {axiom.confidence}\n"
        f"status: {axiom.status}\n"
        "relations:\n"
        f"{rel_lines}\n"
        f"evidence: {ev_inline}\n"
        f"provenance: {_yaml_str(axiom.provenance)}\n"
        "---\n"
    )

    links = ", ".join(f"[[{eid}]]" for eid in evidence_ids)
    body = f"\n# {axiom.title}\n\n{axiom.statement}\n\nEvidence: {links}.\n"

    # Relation targets need a matching wikilink in the body (lint rule).
    rel_targets: List[str] = []
    for k in _RELATION_KEYS:
        if k == "applies-to-kpm":
            continue
        for tgt in relations.get(k) or []:
            if tgt not in rel_targets:
                rel_targets.append(tgt)
    if rel_targets:
        rel_links = ", ".join(f"[[{t}]]" for t in rel_targets)
        body += f"\nRelated: {rel_links}.\n"
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
    clusters: Optional[List[ClusterNote]] = None,
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

    # Reconcile clusters against the axioms actually emitted: a cluster note
    # only ships with >=2 surviving members, and no axiom may point at a
    # cluster that is not written (the lint rejects dangling pointers).
    kept_clusters: List[ClusterNote] = []
    emitted_ids = {ax.id for ax in emitted_axioms}
    for c in clusters or []:
        members = [m for m in c.members if m in emitted_ids]
        if len(members) >= 2:
            kept_clusters.append(ClusterNote(id=c.id, title=c.title, members=members))
    valid_cluster_ids = {c.id for c in kept_clusters}
    for ax in emitted_axioms:
        if getattr(ax, "cluster", None) and ax.cluster not in valid_cluster_ids:
            ax.cluster = None
        # Relation targets must resolve to emitted axioms (lint rule) — an
        # edge to a dropped axiom is stripped, never shipped dangling.
        rels = ax.relations or {}
        for k in _RELATION_KEYS:
            if k == "applies-to-kpm":
                continue
            targets = rels.get(k) or []
            kept_targets = [tgt for tgt in targets if tgt in emitted_ids]
            if len(kept_targets) != len(targets):
                rels[k] = kept_targets

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

    # Write cluster notes (the package's emergent themes, EFF-4).
    clusters_written: List[str] = []
    if kept_clusters:
        (output_dir / "clusters").mkdir(exist_ok=True)
        for c in kept_clusters:
            (output_dir / "clusters" / f"{c.id}.md").write_text(render_cluster(c), encoding="utf-8")
            clusters_written.append(c.id)

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
        clusters_written=clusters_written,
    )
