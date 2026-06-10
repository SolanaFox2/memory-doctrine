"""
kpm_builder.gate
----------------
Dual gate for fetched sources:
  Gate A — classify_tier()   : deterministic quality tier (mechanical heuristic)
  Gate B — is_relevant()     : LLM-judged binary relevance to a ScopeContract

The public entry-point is dual_gate(), which returns a GateResult combining both.
No network calls are made here; Gate B delegates to the injected `complete_json`
callable so tests can inject a fake without hitting any LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from kpm_builder.schema import SourceTier

# Type alias for the injected LLM completion function.
# Signature: (prompt: str, schema: dict) -> dict
CompleteJSON = Callable[[str, dict], dict]


# ---------------------------------------------------------------------------
# Domain objects
# ---------------------------------------------------------------------------

@dataclass
class Source:
    """A fetched web source whose findings may enter the knowledge package."""
    url: str
    text: str
    venue: str = ""  # optional domain / venue hint (e.g. "arxiv.org")


@dataclass
class ScopeContract:
    """Minimal scope definition for the MVP relevance gate."""
    goal: str
    in_scope: str
    out_of_scope: str


@dataclass
class GateResult:
    """Combined result from dual_gate()."""
    keep: bool        # Gate B: LLM-judged relevance
    tier: SourceTier  # Gate A: mechanical quality tier


# ---------------------------------------------------------------------------
# Gate A: tier classification (pure / deterministic)
# ---------------------------------------------------------------------------

# Ordered list of (keywords, tier).  First match wins; UNKNOWN is the fallback.
# NOTE: a curated heuristic for v1 — a real source-quality gate (retraction checks,
# venue reputation) is a Scale refinement (SPEC Q2). BLOG is matched BEFORE official
# domains so a blog *post* on an official domain (blog.ethereum.org, helius.dev/blog)
# is rated as a blog, not as official docs.
_TIER_RULES: list[tuple[list[str], SourceTier]] = [
    (
        ["arxiv.org", "/abs/", "biorxiv", "preprint", "ssrn"],
        SourceTier.PREPRINT,
    ),
    (
        ["doi.org", "pubmed", "ncbi.nlm", ".edu", "journal", "acm.org", "ieee",
         "nature.com", "sciencedirect", "springer", "usenix.org", "arxiv.org/pdf"],
        SourceTier.PEER_REVIEWED,
    ),
    (
        # blog posts (incl. on official/dev domains) + known explainer sites
        ["medium.com", "substack", "wordpress", "/blog", "blog.",
         "helius.dev", "consensys.io", "river.com", "lightspark.com"],
        SourceTier.BLOG,
    ),
    (
        # official project sites, specs, and documentation subdomains.
        # Canonical spec/standard repos are matched ORG-SCOPED (github.com/ethereum/…,
        # raw.githubusercontent.com/ethereum/…) so only the official org counts, not
        # all of GitHub. eth2book.info is Edgington's annotated consensus spec.
        ["ethereum.org", "solana.com", "bitcoin.org", "eips.ethereum.org",
         "anza.xyz", "docs.", "developer.", ".dev/", "readthedocs", "w3.org",
         "ietf.org", "rust-lang.org",
         "github.com/ethereum/", "githubusercontent.com/ethereum/", "eth2book.info",
         "raft.github.io",
         # Canonical author-hosted formal specs: Diego Ongaro's (ongardie) Raft
         # repos — raft.tla is the machine-checked TLA+ spec, the most
         # authoritative artifact in the Raft corpus. A ".tla" formal spec is at
         # least official-docs grade regardless of host.
         "github.com/ongardie/", "githubusercontent.com/ongardie/", "raft.tla",
         # Canonical language documentation: the Move Book / Move Reference
         # (move-book.com, move-language.github.io) is the official Move spec.
         "move-book.com", "move-language.github.io"],
        SourceTier.OFFICIAL_DOCS,
    ),
    (
        ["reuters", "nytimes", "apnews", "bloomberg", "bbc.", "theguardian",
         "wsj.com", "ft.com"],
        SourceTier.REPUTABLE_PRESS,
    ),
]


def classify_tier(source: Source) -> SourceTier:
    """
    Classify source quality tier from source.url and source.venue.

    Both fields are concatenated (space-separated) and lowercased before
    matching.  The first matching rule wins.  Never raises; returns UNKNOWN
    when no rule matches.
    """
    haystack = (source.url + " " + source.venue).lower()

    for keywords, tier in _TIER_RULES:
        if any(kw in haystack for kw in keywords):
            return tier

    return SourceTier.UNKNOWN


# ---------------------------------------------------------------------------
# Gate B: relevance (LLM judge, injected)
# ---------------------------------------------------------------------------

RELEVANCE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "relevant": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["relevant", "reason"],
    "additionalProperties": False,
}

_RELEVANCE_PROMPT_TEMPLATE = """\
You are a relevance judge for a knowledge-package builder.

## Research goal
{goal}

## In scope
{in_scope}

## Out of scope
{out_of_scope}

## Source to evaluate
URL: {url}

Content (first 2000 chars):
{text_snippet}

## Task
Decide whether this source directly addresses the research goal and is in scope.
Answer ONLY in the JSON schema provided.
- Set "relevant" to true if the source is on-topic and in scope, false otherwise.
- Set "reason" to a one-sentence justification.
"""


def is_relevant(
    source: Source,
    contract: ScopeContract,
    *,
    complete_json: CompleteJSON,
) -> bool:
    """
    Ask the injected LLM judge whether `source` is relevant to `contract`.

    Returns True iff the judge returns {"relevant": True, ...}.
    Defensively defaults to False if the key is missing.
    """
    prompt = _RELEVANCE_PROMPT_TEMPLATE.format(
        goal=contract.goal,
        in_scope=contract.in_scope,
        out_of_scope=contract.out_of_scope,
        url=source.url,
        text_snippet=source.text[:2000],
    )
    result = complete_json(prompt, RELEVANCE_SCHEMA)
    return bool(result.get("relevant", False))


# ---------------------------------------------------------------------------
# Public entry-point: dual_gate
# ---------------------------------------------------------------------------

def dual_gate(
    source: Source,
    contract: ScopeContract,
    *,
    complete_json: CompleteJSON,
) -> GateResult:
    """
    Run both gates and return a GateResult.

    Gate A (tier) is purely mechanical and runs first, independently of Gate B.
    Gate B (relevance) uses the injected complete_json callable.
    """
    return GateResult(
        keep=is_relevant(source, contract, complete_json=complete_json),
        tier=classify_tier(source),
    )
