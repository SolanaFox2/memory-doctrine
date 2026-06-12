"""Distill stage — LLM-backed (doctrine E1: distill the generators, not the notes).

Takes the deterministic :class:`Candidate` passages from ingest and asks the
model to distill them into a small set of generative :class:`Idea` objects, each
grounded in the source files and verbatim snippets it rests on.

The LLM dependency is injected as a ``complete_json(prompt, schema) -> dict``
callable, so this stage is fully testable WITHOUT an API key: pass a fake
callable that returns fixed JSON.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .ingest import Candidate
from .llm import CompleteJSON
from .llm_core import UNTRUSTED_PREAMBLE, coerce_result_dict, delimit_untrusted

_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "distill.md"

# JSON schema handed to the model (and to complete_json) to constrain output.
DISTILL_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "statement": {"type": "string"},
                    "supporting_source_files": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "supporting_snippets": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [
                    "statement",
                    "supporting_source_files",
                    "supporting_snippets",
                ],
            },
        }
    },
    "required": ["ideas"],
}


@dataclass
class Idea:
    """A distilled generative idea grounded in its sources."""

    statement: str
    supporting_source_files: List[str] = field(default_factory=list)
    supporting_snippets: List[str] = field(default_factory=list)


def load_prompt() -> str:
    """Load the doctrine-grounded distill prompt text."""
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _render_candidates(candidates: List[Candidate]) -> str:
    blocks = []
    for i, c in enumerate(candidates, 1):
        # Use the FULL relative path (not just the basename) so the model cites
        # provenance precisely — matching skill mode, and avoiding basename
        # collisions for notes in subdirectories. The note text itself is
        # untrusted (scrapes, third-party notes) — delimited as data.
        blocks.append(
            f"[{i}] source_file: {c.source_file}\n"
            f"{delimit_untrusted(c.text.strip(), label=c.source_file)}"
        )
    return "\n\n".join(blocks)


def build_prompt(candidates: List[Candidate]) -> str:
    """Assemble the full distill prompt: rubric + rendered candidates."""
    rubric = load_prompt()
    return (
        f"{rubric}\n\n{UNTRUSTED_PREAMBLE}\n\n---\n\n"
        f"## Candidate passages\n\n{_render_candidates(candidates)}\n"
    )


def _dedupe(ideas: List[Idea]) -> List[Idea]:
    """Merge ideas with identical (normalized) statements, unioning support."""
    by_key: dict[str, Idea] = {}
    for idea in ideas:
        key = " ".join(idea.statement.lower().split())
        if key in by_key:
            existing = by_key[key]
            existing.supporting_source_files = _ordered_union(
                existing.supporting_source_files, idea.supporting_source_files
            )
            existing.supporting_snippets = _ordered_union(existing.supporting_snippets, idea.supporting_snippets)
        else:
            by_key[key] = Idea(
                statement=idea.statement.strip(),
                supporting_source_files=list(idea.supporting_source_files),
                supporting_snippets=list(idea.supporting_snippets),
            )
    return list(by_key.values())


def _ordered_union(a: List[str], b: List[str]) -> List[str]:
    seen: dict[str, None] = {}
    for item in [*a, *b]:
        if item not in seen:
            seen[item] = None
    return list(seen)


# Candidates per LLM call. One giant call over all candidates (the old
# behavior) routinely overflowed the response token cap on real corpora and
# silently dropped ideas; batches keep each response comfortably inside it.
DEFAULT_BATCH_SIZE = 40


def _parse_ideas(result: dict) -> List[Idea]:
    result = coerce_result_dict(result, stage="distill", required_key="ideas")
    raw_ideas = result.get("ideas") or []
    if not isinstance(raw_ideas, list):
        coerce_result_dict(raw_ideas, stage="distill")  # records malformed
        raw_ideas = []
    ideas: List[Idea] = []
    for item in raw_ideas:
        statement = (item.get("statement") or "").strip()
        if not statement:
            continue
        ideas.append(
            Idea(
                statement=statement,
                supporting_source_files=list(item.get("supporting_source_files") or []),
                supporting_snippets=list(item.get("supporting_snippets") or []),
            )
        )
    return ideas


def distill(
    candidates: List[Candidate],
    complete_json: CompleteJSON,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> List[Idea]:
    """Distill candidate passages into a deduped set of generative ideas.

    Candidates are sent in batches of *batch_size* per call and the per-batch
    ideas are unioned via :func:`_dedupe` (identical statements merge their
    support), so large corpora can't overflow a single response.

    Args:
        candidates: The passages produced by the ingest stage.
        complete_json: A ``(prompt, schema) -> dict`` callable. In production
            pass ``LLMClient.complete_json``; in tests pass a fake that returns
            fixed JSON so no API key is required.
        batch_size: Maximum candidates per LLM call (>= 1).
    """
    if not candidates:
        return []
    if batch_size < 1:
        raise ValueError(f"batch_size must be >= 1, got {batch_size}")

    ideas: List[Idea] = []
    for start in range(0, len(candidates), batch_size):
        batch = candidates[start : start + batch_size]
        result = complete_json(build_prompt(batch), DISTILL_SCHEMA)
        ideas.extend(_parse_ideas(result))
    return _dedupe(ideas)
