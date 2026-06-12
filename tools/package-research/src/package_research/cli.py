"""Command-line entry point for package-research.

Wires the FULL doctrine pipeline behind a single ``run`` command::

    package-research run <input_dir> --out <output_dir> [--model MODEL] [--name NAME]

The pipeline is::

    ingest -> distill -> score -> verify -> split -> assemble -> validate

The deterministic stages (ingest/split/assemble/validate) run as-is; the three
LLM-backed stages (distill/score/verify) are driven by a real
:class:`~package_research.llm.LLMClient`, which reads ``ANTHROPIC_API_KEY`` from
the environment. The evidence ``run_date`` is computed ONCE here (today's date)
and threaded down to ``assemble`` so the stage functions stay deterministic and
injection-friendly.

Two extra subcommands provide a **keyless "skill mode"** so an LLM agent can
drive the pipeline with NO API key — the agent itself does the distill/score/
verify judgment:

    package-research ingest <input_dir> [--json]
    package-research build  <input_dir> --ideas <ideas.json> --out <output_dir>

``ingest`` prints the candidate passages as JSON for the agent to read; ``build``
takes the agent's distilled ``ideas.json`` and runs the deterministic tail
(split -> assemble -> validate). Neither needs ``ANTHROPIC_API_KEY``.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .assemble import OutputDirError, assemble, prepare_output_dir, write_reference_notes
from .clamps import clamp_confidence, clamp_generativity
from .cluster import cluster_axioms
from .config import Config
from .distill import distill
from .ingest import Candidate, ingest, passages_by_source
from .relate import RelateStats, relate_axioms
from .llm import LLMClient
from .llm_core import malformed_counts, reset_malformed
from .score import ScoredIdea, score
from .split import split, uncited_sources
from .validate import ValidationResult, validate
from .verify import verify


def _add_output_args(parser: argparse.ArgumentParser) -> None:
    """Add the output/ingest args shared by ``run`` and ``build`` (REVIEW.md L1)."""
    parser.add_argument(
        "--out",
        required=True,
        dest="out",
        help="Output directory for the produced KPM package.",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Package name written into knowledge.json (e.g. @kpm/my-notes).",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Package description written into knowledge.json.",
    )
    parser.add_argument(
        "--keep-uncited",
        action="store_true",
        dest="keep_uncited",
        help="Preserve sources no axiom cited into reference/ (nothing dropped).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Write into a non-empty --out dir even when it is not a package "
            "this tool produced (its note dirs are cleared of stale *.md)."
        ),
    )
    parser.add_argument(
        "--max-sources",
        type=int,
        default=None,
        dest="max_sources",
        help=(
            "Cap on source files ingested (alphabetical order; truncation "
            "warns to stderr). Default: config default (200)."
        ),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="package-research",
        description=(
            "Turn a folder of raw notes into a doctrine-grounded knowledge "
            "package (KPM). The Memory Doctrine's consuming tool."
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    run = sub.add_parser(
        "run",
        help="Run the full pipeline on a notes folder and write a KPM package.",
        description=(
            "Ingest a notes folder, distill + score + verify ideas against the "
            "doctrine, then assemble and validate a KPM package."
        ),
    )
    run.add_argument(
        "input_dir",
        help="Folder of source notes (.md/.txt) to ingest (searched recursively).",
    )
    run.add_argument(
        "--model",
        default=None,
        help="Anthropic model for the LLM-backed stages (default: config default).",
    )
    _add_output_args(run)
    run.set_defaults(func=_cmd_run)

    # --- keyless skill mode: ingest -----------------------------------------
    ing = sub.add_parser(
        "ingest",
        help="Print the ingested candidate passages (skill mode — no API key).",
        description=(
            "Deterministically read + chunk a notes folder and print the "
            "candidate passages an agent should distill. With --json, emit a "
            "JSON list of {index, source_file, text}."
        ),
    )
    ing.add_argument(
        "input_dir",
        help="Folder of source notes (.md/.txt) to ingest (searched recursively).",
    )
    ing.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit the candidates as a JSON array (the agent's input).",
    )
    ing.set_defaults(func=_cmd_ingest)

    # --- keyless skill mode: build ------------------------------------------
    build = sub.add_parser(
        "build",
        help="Build a KPM package from an agent-written ideas.json (no API key).",
        description=(
            "Skill mode: take an agent's distilled ideas.json (a list of "
            "{statement, supporting_source_files, supporting_snippets, "
            "confidence, generativity, rationale?}) and run the deterministic "
            "tail split -> assemble -> validate. No API key required."
        ),
    )
    build.add_argument(
        "input_dir",
        help=(
            "The notes folder the ideas were distilled from. Re-read so the "
            "store preserves the source content, not just the cited lines."
        ),
    )
    build.add_argument(
        "--ideas",
        required=True,
        dest="ideas",
        help="Path to the agent-written ideas.json (list of idea objects).",
    )
    _add_output_args(build)
    build.set_defaults(func=_cmd_build)
    return parser


def _make_llm(config: Config) -> LLMClient:
    """Construct the production LLM client, requiring a real API key.

    Factored out so tests can monkeypatch it with a fake (no API key needed).
    """
    api_key = Config.resolve_api_key()  # raises a clear error if missing
    return LLMClient(api_key=api_key, model=config.model, max_tokens=config.max_tokens)


def _summarize(
    *,
    n_candidates: int,
    n_ideas: int,
    n_scored: int,
    n_kept: int,
    package_dir: Path,
    result: ValidationResult,
    out: "object",
    n_sources: int = 0,
    uncited: "Optional[List[str]]" = None,
    kept_uncited: bool = False,
    malformed: "Optional[dict]" = None,
    relations: "Optional[RelateStats]" = None,
) -> None:
    """Print a clear, human-readable run summary."""
    print("package-research run complete", file=out)
    print(f"  candidates ingested : {n_candidates}", file=out)
    print(f"  ideas distilled     : {n_ideas}", file=out)
    print(f"  ideas scored        : {n_scored}", file=out)
    print(f"  kept after verify   : {n_kept}", file=out)
    if relations is not None:
        extra = ""
        if relations.capped or relations.skipped:
            extra = f" (capped {relations.capped}, skipped {relations.skipped})"
        print(
            f"  relations verified  : {relations.verified}/{relations.proposed}{extra}",
            file=out,
        )

    # Malformed model outputs are never silent (an all-malformed run must be
    # distinguishable from a legitimate "nothing survived").
    malformed = malformed or {}
    if malformed:
        per_stage = ", ".join(f"{k}={v}" for k, v in sorted(malformed.items()))
        print(
            f"  malformed outputs   : {sum(malformed.values())} ({per_stage}) — "
            "low counts above may be model garbage, not judgment",
            file=out,
        )
    print(f"  output package      : {package_dir}", file=out)

    # Source coverage — never drop a file silently (no hidden loss).
    uncited = uncited or []
    if n_sources:
        represented = n_sources - len(uncited)
        print(
            f"  source coverage     : {represented}/{n_sources} files in the store",
            file=out,
        )
        if uncited:
            where = (
                "preserved in reference/" if kept_uncited else "NOT in package — rerun with --keep-uncited to preserve"
            )
            print(f"  uncited sources     : {len(uncited)} ({where})", file=out)
            for s in uncited:
                print(f"      - {s}", file=out)

    lint = "OK" if result.lint_ok else "FAILED"
    print(
        f"  doctrine lint       : {lint} ({len(result.lint_violations)} violations)",
        file=out,
    )
    if not result.lint_ok:
        for v in result.lint_violations:
            print(f"      - {v}", file=out)

    if result.doctor_ok is None:
        doctor = "skipped (kpm CLI not available)"
    elif result.doctor_ok:
        doctor = "OK"
    else:
        doctor = "FAILED"
    print(f"  kpm doctor          : {doctor}", file=out)
    if result.doctor_ok is False and result.doctor_output:
        print(f"      {result.doctor_output}", file=out)


def _cmd_run(args: argparse.Namespace) -> int:
    overrides: dict = {}
    if args.model:
        overrides["model"] = args.model
    if args.max_sources is not None:
        overrides["max_sources"] = args.max_sources
    config = Config(input_dir=args.input_dir, output_dir=args.out, **overrides)

    input_dir = Path(config.input_dir)
    if not input_dir.is_dir():
        print(f"error: input_dir is not a directory: {input_dir}", file=sys.stderr)
        return 2

    # Guard the output dir BEFORE any LLM spend (REVIEW.md M1).
    try:
        prepare_output_dir(Path(config.output_dir), force=args.force)
    except OutputDirError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Compute today's date ONCE; thread it into assemble (stages stay deterministic).
    run_date = datetime.date.today().isoformat()

    # Build the LLM client (resolves ANTHROPIC_API_KEY; clear error if missing).
    try:
        llm = _make_llm(config)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    complete_json = llm.complete_json
    reset_malformed()

    # --- the full pipeline -------------------------------------------------
    candidates = ingest(config)
    ideas = distill(candidates, complete_json, batch_size=config.distill_batch_size)
    scored = score(ideas, complete_json)
    verified = verify(scored, complete_json)
    # Preserve the source content in the store (keep details, not just headlines).
    pbs = passages_by_source(candidates)
    axioms, evidence = split(verified, pbs, survived_challenge=True)
    # Relate pass: the package's value lives in the connections (EFF-1).
    rel_stats = relate_axioms(axioms, complete_json)
    # Cluster pass: connected components of the relation graph are the
    # package's emergent themes (EFF-4). Deterministic, no LLM call.
    clusters = cluster_axioms(axioms)

    name = args.name or "@kpm/distilled-research"
    kwargs: dict = {"clusters": clusters, "run_date": run_date, "name": name}
    if args.description:
        kwargs["description"] = args.description
    assemble(axioms, evidence, config.output_dir, **kwargs)

    # Coverage: which sources no axiom cited. Optionally preserve them so the
    # package never drops a file silently.
    uncited = uncited_sources(pbs, evidence)
    if getattr(args, "keep_uncited", False):
        write_reference_notes(uncited, Path(config.output_dir), run_date=run_date)

    result = validate(config.output_dir)

    _summarize(
        n_candidates=len(candidates),
        n_ideas=len(ideas),
        n_scored=len(scored),
        n_kept=len(verified),
        package_dir=Path(config.output_dir),
        result=result,
        out=sys.stdout,
        n_sources=len(pbs),
        uncited=sorted(uncited),
        kept_uncited=getattr(args, "keep_uncited", False),
        malformed=malformed_counts(),
        relations=rel_stats,
    )

    # Lint is the hard gate: a structurally invalid package is a failure.
    return 0 if result.lint_ok else 1


def _candidates_to_json(candidates: List[Candidate]) -> List[dict]:
    """Shape candidates for the agent: ``[{index, source_file, text}, ...]``."""
    return [
        {
            "index": i,
            "source_file": str(c.source_file),
            "text": c.text,
        }
        for i, c in enumerate(candidates, 1)
    ]


def _cmd_ingest(args: argparse.Namespace) -> int:
    """Skill mode: print the candidate passages an agent will distill."""
    config = Config(input_dir=args.input_dir, output_dir="./kpm-out")
    input_dir = Path(config.input_dir)
    if not input_dir.is_dir():
        print(f"error: input_dir is not a directory: {input_dir}", file=sys.stderr)
        return 2

    candidates = ingest(config)
    payload = _candidates_to_json(candidates)

    if args.as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for item in payload:
            print(f"[{item['index']}] source_file: {item['source_file']}")
            print(item["text"].strip())
            print()
    return 0


def _coerce_idea(raw: object) -> Optional[ScoredIdea]:
    """Validate + coerce one ideas.json entry into a :class:`ScoredIdea`.

    Clamps ``confidence`` to [0, 1] and ``generativity`` to 1..5, and **drops**
    (returns ``None`` for) any idea that carries no non-empty supporting snippet
    — confidence is earned from evidence actually present (doctrine C1/E4).
    """
    if not isinstance(raw, dict):
        return None
    statement = str(raw.get("statement") or "").strip()
    if not statement:
        return None

    snippets = [str(s) for s in (raw.get("supporting_snippets") or []) if str(s).strip()]
    if not snippets:
        return None  # drop unsupported ideas — no snippet, no admission
    source_files = [str(f) for f in (raw.get("supporting_source_files") or []) if str(f).strip()]

    return ScoredIdea(
        statement=statement,
        supporting_source_files=source_files,
        supporting_snippets=snippets,
        confidence=clamp_confidence(raw.get("confidence")),
        generativity=clamp_generativity(raw.get("generativity")),
        rationale=str(raw.get("rationale") or "").strip(),
    )


def _load_ideas(path: Path) -> List[ScoredIdea]:
    """Load + coerce an ideas.json file into validated ScoredIdea objects."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "ideas" in data:
        data = data["ideas"]
    if not isinstance(data, list):
        raise ValueError('ideas file must be a JSON list of idea objects (or {"ideas": [...]})')
    ideas: List[ScoredIdea] = []
    for raw in data:
        coerced = _coerce_idea(raw)
        if coerced is not None:
            ideas.append(coerced)
    return ideas


def _cmd_build(args: argparse.Namespace) -> int:
    """Skill mode: build a KPM package from an agent-written ideas.json."""
    overrides: dict = {}
    if args.max_sources is not None:
        overrides["max_sources"] = args.max_sources
    config = Config(input_dir=args.input_dir, output_dir=args.out, **overrides)

    input_dir = Path(config.input_dir)
    if not input_dir.is_dir():
        print(f"error: input_dir is not a directory: {input_dir}", file=sys.stderr)
        return 2

    # Guard the output dir before writing anything (REVIEW.md M1).
    try:
        prepare_output_dir(Path(config.output_dir), force=args.force)
    except OutputDirError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    ideas_path = Path(args.ideas)
    if not ideas_path.is_file():
        print(f"error: ideas file not found: {ideas_path}", file=sys.stderr)
        return 2
    try:
        scored = _load_ideas(ideas_path)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: could not parse ideas file: {exc}", file=sys.stderr)
        return 2

    # Compute today's date ONCE; thread it into assemble (stays deterministic).
    run_date = datetime.date.today().isoformat()

    # Re-read the notes folder so the store preserves the source content (the
    # details), not just the one line each idea quoted. The agent's ideas.json
    # supplies the index (axioms + confidence); ingest supplies the rich store.
    candidates = ingest(config)
    pbs = passages_by_source(candidates)
    axioms, evidence = split(scored, pbs)

    name = args.name or "@kpm/distilled-research"
    kwargs: dict = {"run_date": run_date, "name": name}
    if args.description:
        kwargs["description"] = args.description
    assemble(axioms, evidence, config.output_dir, **kwargs)

    # Coverage: sources no axiom cited. Optionally preserve them in reference/.
    uncited = uncited_sources(pbs, evidence)
    if getattr(args, "keep_uncited", False):
        write_reference_notes(uncited, Path(config.output_dir), run_date=run_date)

    result = validate(config.output_dir)

    _summarize(
        n_candidates=len(scored),
        n_ideas=len(scored),
        n_scored=len(scored),
        n_kept=len(scored),
        package_dir=Path(config.output_dir),
        result=result,
        out=sys.stdout,
        n_sources=len(pbs),
        uncited=sorted(uncited),
        kept_uncited=getattr(args, "keep_uncited", False),
    )

    return 0 if result.lint_ok else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
