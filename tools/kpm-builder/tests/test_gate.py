"""
tests/test_gate.py
------------------
TDD tests for kpm_builder.gate — Gate A (classify_tier) and Gate B (is_relevant / dual_gate).

All tests use a fake complete_json; NO real LLM calls.
"""
from __future__ import annotations

import pytest
from kpm_builder.schema import SourceTier
from kpm_builder.gate import (
    Source,
    ScopeContract,
    GateResult,
    classify_tier,
    is_relevant,
    dual_gate,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def make_contract(
    goal: str = "Understand short-term memory in LLMs",
    in_scope: str = "attention mechanisms, context windows, KV-cache",
    out_of_scope: str = "long-term storage, retrieval-augmented generation",
) -> ScopeContract:
    return ScopeContract(goal=goal, in_scope=in_scope, out_of_scope=out_of_scope)


def fake_complete_json_true(prompt: str, schema: dict) -> dict:
    """Always votes relevant=True."""
    return {"relevant": True, "reason": "on-topic"}


def fake_complete_json_false(prompt: str, schema: dict) -> dict:
    """Always votes relevant=False."""
    return {"relevant": False, "reason": "off-topic"}


def fake_complete_json_empty(prompt: str, schema: dict) -> dict:
    """Returns an empty dict — defensive default must kick in."""
    return {}


# ---------------------------------------------------------------------------
# Gate A: classify_tier
# ---------------------------------------------------------------------------

class TestClassifyTier:

    def test_arxiv_url_is_preprint(self):
        src = Source(url="https://arxiv.org/abs/2401.00001", text="paper text")
        assert classify_tier(src) == SourceTier.PREPRINT

    def test_url_with_abs_segment_is_preprint(self):
        # "/abs/" keyword match (not just arxiv.org)
        src = Source(url="https://someserver.io/abs/1234", text="preprint body")
        assert classify_tier(src) == SourceTier.PREPRINT

    def test_biorxiv_is_preprint(self):
        src = Source(url="https://www.biorxiv.org/content/10.1101/2024.01.01", text="bio paper")
        assert classify_tier(src) == SourceTier.PREPRINT

    def test_preprint_keyword_in_url_is_preprint(self):
        src = Source(url="https://example.com/preprint/paper-123", text="text")
        assert classify_tier(src) == SourceTier.PREPRINT

    def test_doi_url_is_peer_reviewed(self):
        src = Source(url="https://doi.org/10.1038/s41586-020-2649-2", text="paper")
        assert classify_tier(src) == SourceTier.PEER_REVIEWED

    def test_pubmed_is_peer_reviewed(self):
        src = Source(url="https://pubmed.ncbi.nlm.nih.gov/12345678/", text="abstract")
        assert classify_tier(src) == SourceTier.PEER_REVIEWED

    def test_edu_domain_is_peer_reviewed(self):
        src = Source(url="https://cs.mit.edu/papers/transformer.html", text="text")
        assert classify_tier(src) == SourceTier.PEER_REVIEWED

    def test_journal_in_url_is_peer_reviewed(self):
        src = Source(url="https://nature.com/journal/articles/12345", text="text")
        assert classify_tier(src) == SourceTier.PEER_REVIEWED

    def test_acm_org_is_peer_reviewed(self):
        src = Source(url="https://dl.acm.org/doi/10.1145/3456789", text="text")
        assert classify_tier(src) == SourceTier.PEER_REVIEWED

    def test_ieee_is_peer_reviewed(self):
        src = Source(url="https://ieeexplore.ieee.org/document/12345", text="text")
        assert classify_tier(src) == SourceTier.PEER_REVIEWED

    def test_docs_subdomain_is_official_docs(self):
        src = Source(url="https://docs.python.org/3/library/os.html", text="text")
        assert classify_tier(src) == SourceTier.OFFICIAL_DOCS

    def test_developer_subdomain_is_official_docs(self):
        src = Source(url="https://developer.mozilla.org/en-US/docs/Web/API", text="text")
        assert classify_tier(src) == SourceTier.OFFICIAL_DOCS

    def test_dev_path_segment_is_official_docs(self):
        src = Source(url="https://pkg.go.dev/net/http", text="text")
        assert classify_tier(src) == SourceTier.OFFICIAL_DOCS

    def test_readthedocs_is_official_docs(self):
        src = Source(url="https://requests.readthedocs.io/en/latest/", text="text")
        assert classify_tier(src) == SourceTier.OFFICIAL_DOCS

    def test_reuters_is_reputable_press(self):
        src = Source(url="https://www.reuters.com/technology/ai-chip-2024", text="text")
        assert classify_tier(src) == SourceTier.REPUTABLE_PRESS

    def test_nytimes_is_reputable_press(self):
        src = Source(url="https://www.nytimes.com/2024/01/01/tech/ai.html", text="text")
        assert classify_tier(src) == SourceTier.REPUTABLE_PRESS

    def test_apnews_is_reputable_press(self):
        src = Source(url="https://apnews.com/article/ai-regulation-12345", text="text")
        assert classify_tier(src) == SourceTier.REPUTABLE_PRESS

    def test_bloomberg_is_reputable_press(self):
        src = Source(url="https://www.bloomberg.com/news/articles/2024-01-01/tech", text="text")
        assert classify_tier(src) == SourceTier.REPUTABLE_PRESS

    def test_bbc_is_reputable_press(self):
        src = Source(url="https://www.bbc.com/news/technology-12345678", text="text")
        assert classify_tier(src) == SourceTier.REPUTABLE_PRESS

    def test_medium_com_is_blog(self):
        src = Source(url="https://medium.com/@author/my-take-on-ai-abcdef123456", text="text")
        assert classify_tier(src) == SourceTier.BLOG

    def test_substack_is_blog(self):
        src = Source(url="https://author.substack.com/p/my-post", text="text")
        assert classify_tier(src) == SourceTier.BLOG

    def test_blog_in_url_is_blog(self):
        src = Source(url="https://example.com/blog/post-title", text="text")
        assert classify_tier(src) == SourceTier.BLOG

    def test_wordpress_is_blog(self):
        src = Source(url="https://mysite.wordpress.com/2024/01/ai-thoughts", text="text")
        assert classify_tier(src) == SourceTier.BLOG

    def test_random_com_is_unknown(self):
        src = Source(url="https://somerandombusiness.com/report", text="text")
        assert classify_tier(src) == SourceTier.UNKNOWN

    def test_empty_url_is_unknown(self):
        src = Source(url="", text="text")
        assert classify_tier(src) == SourceTier.UNKNOWN

    def test_case_insensitive_arxiv(self):
        # URL shouldn't be uppercase in practice, but venue hint might be mixed case
        src = Source(url="https://example.com", text="text", venue="ArXiv.org preprint")
        assert classify_tier(src) == SourceTier.PREPRINT

    def test_case_insensitive_blog(self):
        src = Source(url="https://example.com/BLOG/post", text="text")
        assert classify_tier(src) == SourceTier.BLOG

    def test_venue_hint_used_when_url_is_unknown(self):
        # URL alone → UNKNOWN; venue hint has "doi.org" → PEER_REVIEWED
        src = Source(url="https://generic.com/paper", text="text", venue="doi.org")
        assert classify_tier(src) == SourceTier.PEER_REVIEWED

    def test_preprint_beats_peer_reviewed_on_first_match(self):
        # URL contains both "arxiv.org" AND "doi" — first match (PREPRINT) wins
        src = Source(url="https://arxiv.org/abs/doi-crossref/1234", text="text")
        assert classify_tier(src) == SourceTier.PREPRINT


# ---------------------------------------------------------------------------
# Gate B: is_relevant
# ---------------------------------------------------------------------------

class TestIsRelevant:

    def test_returns_true_when_llm_says_relevant(self):
        src = Source(url="https://arxiv.org/abs/1234", text="context window scaling")
        contract = make_contract()
        result = is_relevant(src, contract, complete_json=fake_complete_json_true)
        assert result is True

    def test_returns_false_when_llm_says_not_relevant(self):
        src = Source(url="https://arxiv.org/abs/9999", text="unrelated topic")
        contract = make_contract()
        result = is_relevant(src, contract, complete_json=fake_complete_json_false)
        assert result is False

    def test_defensive_false_on_empty_response(self):
        """If the LLM returns {} (missing 'relevant' key), gate must default to False."""
        src = Source(url="https://example.com/paper", text="any text")
        contract = make_contract()
        result = is_relevant(src, contract, complete_json=fake_complete_json_empty)
        assert result is False

    def test_prompt_contains_goal(self):
        """The built prompt must embed the contract goal."""
        captured: list[str] = []

        def capturing_cj(prompt: str, schema: dict) -> dict:
            captured.append(prompt)
            return {"relevant": True, "reason": "ok"}

        contract = make_contract(goal="Understand attention head pruning in BERT")
        src = Source(url="https://arxiv.org/abs/1234", text="pruning paper")
        is_relevant(src, contract, complete_json=capturing_cj)

        assert captured, "complete_json was never called"
        assert "Understand attention head pruning in BERT" in captured[0]

    def test_prompt_contains_out_of_scope(self):
        """The prompt must include the out_of_scope text so the judge can screen it."""
        captured: list[str] = []

        def capturing_cj(prompt: str, schema: dict) -> dict:
            captured.append(prompt)
            return {"relevant": False, "reason": "nope"}

        contract = make_contract(out_of_scope="retrieval-augmented generation, knowledge graphs")
        src = Source(url="https://medium.com/@x/rag-blog", text="RAG post")
        is_relevant(src, contract, complete_json=capturing_cj)

        assert "retrieval-augmented generation, knowledge graphs" in captured[0]

    def test_prompt_contains_in_scope(self):
        captured: list[str] = []

        def capturing_cj(prompt: str, schema: dict) -> dict:
            captured.append(prompt)
            return {"relevant": True, "reason": "yes"}

        contract = make_contract(in_scope="attention mechanisms, context windows, KV-cache")
        src = Source(url="https://arxiv.org/abs/1234", text="KV-cache paper")
        is_relevant(src, contract, complete_json=capturing_cj)

        assert "attention mechanisms, context windows, KV-cache" in captured[0]

    def test_bool_conversion_from_truthy_int(self):
        """If LLM returns {"relevant": 1, ...} (truthy int), should still return True."""
        def truthy_int_cj(prompt: str, schema: dict) -> dict:
            return {"relevant": 1, "reason": "ok"}

        src = Source(url="https://arxiv.org/abs/1234", text="paper")
        contract = make_contract()
        assert is_relevant(src, contract, complete_json=truthy_int_cj) is True


# ---------------------------------------------------------------------------
# dual_gate: combines both gates
# ---------------------------------------------------------------------------

class TestDualGate:

    def test_dual_gate_keep_true_arxiv(self):
        src = Source(url="https://arxiv.org/abs/2401.12345", text="attention paper")
        contract = make_contract()
        result = dual_gate(src, contract, complete_json=fake_complete_json_true)
        assert isinstance(result, GateResult)
        assert result.keep is True
        assert result.tier == SourceTier.PREPRINT

    def test_dual_gate_keep_false_medium(self):
        src = Source(url="https://medium.com/@blogger/rag-hype", text="RAG hype post")
        contract = make_contract()
        result = dual_gate(src, contract, complete_json=fake_complete_json_false)
        assert result.keep is False
        assert result.tier == SourceTier.BLOG

    def test_dual_gate_unknown_tier_irrelevant(self):
        src = Source(url="https://randomsite.biz/article", text="random stuff")
        contract = make_contract()
        result = dual_gate(src, contract, complete_json=fake_complete_json_false)
        assert result.keep is False
        assert result.tier == SourceTier.UNKNOWN

    def test_dual_gate_official_docs_relevant(self):
        src = Source(url="https://docs.pytorch.org/nn/attention.html", text="attention docs")
        contract = make_contract()
        result = dual_gate(src, contract, complete_json=fake_complete_json_true)
        assert result.keep is True
        assert result.tier == SourceTier.OFFICIAL_DOCS

    def test_dual_gate_tier_independent_of_relevance(self):
        """Tier classification is purely mechanical — it must not depend on LLM output."""
        src = Source(url="https://pubmed.ncbi.nlm.nih.gov/99999999/", text="medical paper")
        contract = make_contract()

        result_yes = dual_gate(src, contract, complete_json=fake_complete_json_true)
        result_no = dual_gate(src, contract, complete_json=fake_complete_json_false)

        # Tier must be identical regardless of LLM answer
        assert result_yes.tier == result_no.tier == SourceTier.PEER_REVIEWED
        # But keep must differ
        assert result_yes.keep is True
        assert result_no.keep is False

    def test_dual_gate_empty_llm_response_keep_false(self):
        src = Source(url="https://arxiv.org/abs/0000.00000", text="paper")
        contract = make_contract()
        result = dual_gate(src, contract, complete_json=fake_complete_json_empty)
        assert result.keep is False
        assert result.tier == SourceTier.PREPRINT


def test_canonical_ethereum_spec_repos_are_official():
    from kpm_builder.gate import Source, classify_tier
    from kpm_builder.schema import SourceTier
    # The canonical consensus-specs / EIPs (served from GitHub) and eth2book are official.
    assert classify_tier(Source("https://raw.githubusercontent.com/ethereum/consensus-specs/master/specs/phase0/beacon-chain.md", "x")) is SourceTier.OFFICIAL_DOCS
    assert classify_tier(Source("https://raw.githubusercontent.com/ethereum/EIPs/master/EIPS/eip-7251.md", "x")) is SourceTier.OFFICIAL_DOCS
    assert classify_tier(Source("https://eth2book.info/latest/part2/consensus/casper_ffg/", "x")) is SourceTier.OFFICIAL_DOCS
    # But a random (non-ethereum) GitHub repo must NOT be promoted to official.
    assert classify_tier(Source("https://github.com/someuser/somerepo", "x")) is SourceTier.UNKNOWN


def test_usenix_and_raft_official_tiers():
    from kpm_builder.gate import Source, classify_tier
    from kpm_builder.schema import SourceTier
    assert classify_tier(Source("https://www.usenix.org/conference/atc14/...","x")) is SourceTier.PEER_REVIEWED
    assert classify_tier(Source("https://raft.github.io/raft.pdf","x")) is SourceTier.OFFICIAL_DOCS
    assert classify_tier(Source("https://arxiv.org/pdf/1710.09437","x")) is SourceTier.PREPRINT  # /abs and /pdf both preprint


def test_ongardie_tla_spec_official_tier():
    """Ongaro's canonical Raft TLA+ formal spec must not rate UNKNOWN."""
    from kpm_builder.gate import Source, classify_tier
    from kpm_builder.schema import SourceTier
    assert classify_tier(Source("https://raw.githubusercontent.com/ongardie/raft.tla/master/raft.tla","x")) is SourceTier.OFFICIAL_DOCS
    assert classify_tier(Source("https://github.com/ongardie/dissertation","x")) is SourceTier.OFFICIAL_DOCS
    # but a random other user's github repo stays UNKNOWN (org-scoped, not all of github)
    assert classify_tier(Source("https://github.com/someuser/raft-impl","x")) is SourceTier.UNKNOWN


def test_move_book_official_tier():
    """The canonical Move Book / Reference must not rate UNKNOWN."""
    from kpm_builder.gate import Source, classify_tier
    from kpm_builder.schema import SourceTier
    assert classify_tier(Source("https://move-book.com/reference/abilities/","x")) is SourceTier.OFFICIAL_DOCS
    assert classify_tier(Source("https://move-language.github.io/move/","x")) is SourceTier.OFFICIAL_DOCS
