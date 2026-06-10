"""kpm_builder.apply_relations — the Relate stage (mechanical side).

Takes a ``RelateResult`` (verified edges from ``relate.relate_kpm``) and writes
the relations into a produced KPM's axiom notes — frontmatter + matching body
wikilinks — then asserts the package still lints clean.  NO LLM, NO network.

Two layers (the pure one is trivially unit-testable with no filesystem):
- ``rewrite_axiom_md(text, outgoing, incoming_contradicts) -> text``  (PURE)
- ``apply_relations(kpm_dir, result)``  (read → rewrite → atomic write → validate)

Idempotent: applying the same result twice yields byte-identical files
(relation lists are sorted+deduped; wikilinks are added only when missing).
The frontmatter is edited surgically (one ``  <type>: [...]`` line at a time),
NOT via a full YAML round-trip — that preserves byte-stability.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from kpm_builder._util import atomic_write
from kpm_builder.relate import (
    CompleteJSON,
    RelateResult,
    RelationType,
    parse_axiom_md,
    relate_kpm,
)

# Organizer tail — the lint post-condition.
from package_research.validate import validate

#: Matches a wikilink target (same shape as doctrine_lint's WIKILINK).
_WIKILINK = re.compile(r"\[\[([^\]|#]+)")

#: Line-anchored frontmatter delimiter (same shape as the public linter's _parse).
_FM_SPLIT = re.compile(r"(?m)^---[ \t]*$")


def _merge_relation_line(text: str, type_value: str, new_ids: Iterable[str]) -> str:
    """Surgically merge ``new_ids`` into the single ``  <type>: [...]`` frontmatter
    line, keeping the list sorted + deduped.  No-op if the line is absent."""
    new = set(new_ids)
    pat = re.compile(rf"(?m)^(?P<indent>[ \t]+){re.escape(type_value)}:[ \t]*\[(?P<inner>.*?)\][ \t]*$")

    def _repl(m: re.Match) -> str:
        existing = [x.strip() for x in m.group("inner").split(",") if x.strip()]
        merged = sorted(set(existing) | new)
        return f"{m.group('indent')}{type_value}: [{', '.join(merged)}]"

    return pat.sub(_repl, text, count=1)


def rewrite_axiom_md(
    text: str,
    outgoing: Iterable[tuple[RelationType, str]],
    incoming_contradicts: Iterable[str] = (),
) -> str:
    """Return ``text`` with the given relations written in.

    Parameters
    ----------
    outgoing:
        ``(type, to_id)`` edges declared FROM this axiom.
    incoming_contradicts:
        ids of axioms that contradict this one — written as reciprocal
        ``contradicts`` edges so the symmetric relation is navigable from both
        sides (``contradicts`` is symmetric; the other types are directional).
    """
    by_type: dict[RelationType, set[str]] = {}
    for rtype, to_id in outgoing:
        by_type.setdefault(rtype, set()).add(to_id)
    incoming = set(incoming_contradicts)
    if incoming:
        by_type.setdefault(RelationType.CONTRADICTS, set()).update(incoming)

    # Edit relation lines ONLY inside the frontmatter block — never a body line
    # that happens to look like ``  supports: [...]`` (e.g. in an example/code block).
    parts = _FM_SPLIT.split(text, maxsplit=2)
    if len(parts) >= 3:
        fm = parts[1]
        for rtype, ids in by_type.items():
            fm = _merge_relation_line(fm, rtype.value, ids)
        text = parts[0] + "---" + fm + "---" + parts[2]

    # Every declared relation target needs a matching [[wikilink]] in the body
    # (doctrine_lint requires it). Add only the missing ones, sorted (idempotent).
    targets = sorted({tid for ids in by_type.values() for tid in ids})
    present = set(_WIKILINK.findall(text))
    missing = [t for t in targets if t not in present]
    if missing:
        if not text.endswith("\n"):
            text += "\n"
        text += "".join(f"[[{t}]]\n" for t in missing)
    return text


def apply_relations(kpm_dir: str | Path, result: RelateResult) -> None:
    """Persist verified relations into the KPM at ``kpm_dir``.

    Plans every affected axiom note (frontmatter + wikilinks), writes them
    atomically, then asserts ``validate(kpm_dir).lint_ok``.  If lint fails it
    **rolls every file back** to its original bytes and raises — so the KPM is
    never left broken or half-applied.  Only ``verified`` relations are written.
    """
    kpm_dir = Path(kpm_dir)
    axdir = kpm_dir / "axioms"

    # Never write an unverified edge, whoever built the RelateResult.
    relations = [r for r in result.relations if r.verified]

    # axiom id → its file path
    id_to_file: dict[str, Path] = {}
    for f in sorted(axdir.glob("*.md")):
        av = parse_axiom_md(f.read_text(encoding="utf-8"))
        if av.id:
            id_to_file[av.id] = f

    outgoing: dict[str, list[tuple[RelationType, str]]] = {}
    incoming_contradicts: dict[str, set[str]] = {}
    for r in relations:
        outgoing.setdefault(r.from_id, []).append((r.type, r.to_id))
        if r.type is RelationType.CONTRADICTS:
            incoming_contradicts.setdefault(r.to_id, set()).add(r.from_id)

    # Plan first (no writes): path → (original, new_text) for files that change.
    planned: dict[Path, tuple[str, str]] = {}
    for aid in set(outgoing) | set(incoming_contradicts):
        f = id_to_file.get(aid)
        if f is None:
            continue
        original = f.read_text(encoding="utf-8")
        new_text = rewrite_axiom_md(
            original,
            outgoing.get(aid, []),
            incoming_contradicts.get(aid, set()),
        )
        if new_text != original:
            planned[f] = (original, new_text)

    for f, (_, new_text) in planned.items():
        atomic_write(f, new_text)

    report = validate(str(kpm_dir))
    if not report.lint_ok:
        for f, (original, _) in planned.items():     # roll back — leave it clean
            atomic_write(f, original)
        raise RuntimeError(
            f"apply_relations would break lint on {kpm_dir}; rolled back: {report}"
        )


def relate_and_apply(
    kpm_dir: str | Path,
    *,
    complete_json: CompleteJSON,
    max_out_degree: int = 5,
    global_cap: int = 200,
) -> RelateResult:
    """Convenience: run ``relate_kpm`` then persist the result with
    ``apply_relations``.  Returns the (verified) RelateResult."""
    result = relate_kpm(
        kpm_dir,
        complete_json=complete_json,
        max_out_degree=max_out_degree,
        global_cap=global_cap,
    )
    apply_relations(kpm_dir, result)
    return result
