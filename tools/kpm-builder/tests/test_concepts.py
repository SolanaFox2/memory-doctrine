"""Tests for kpm_builder.concepts (pure, mechanical concept extraction)."""
from __future__ import annotations

from kpm_builder.concepts import (
    candidates,
    extract_concepts,
    idf,
    singularize,
    tokenize,
)


# ── tokenize ──────────────────────────────────────────────────────────────────

def test_tokenize_keeps_domain_tokens_drops_noise():
    toks = tokenize("An attestation's source indicates one-third of 2/3 at 12.8 minutes.")
    assert "attestation" in toks          # possessive 's stripped
    assert "attestation's" not in toks
    assert "one-third" in toks            # hyphenated kept
    assert "2/3" in toks                  # fraction kept
    assert "12.8" in toks                 # decimal kept
    assert "an" not in toks and "of" not in toks and "at" not in toks  # <=2 char dropped


def test_tokenize_allcaps_identifier_lowercased_intact():
    toks = tokenize("In the phase0 spec, MAX_EFFECTIVE_BALANCE is 32 ETH.")
    assert "max_effective_balance" in toks
    assert "eth" in toks


# ── singularize ───────────────────────────────────────────────────────────────

def test_singularize_folds_only_when_base_in_vocab():
    vocab = {"validator", "vote", "bias"}
    assert singularize("validators", vocab) == "validator"   # base present → fold
    assert singularize("votes", vocab) == "vote"
    assert singularize("bias", vocab) == "bias"              # not a plural of "bia"
    assert singularize("epochs", vocab) == "epochs"          # "epoch" not in vocab → keep


# ── candidates ────────────────────────────────────────────────────────────────

def test_candidates_drop_stopword_head_or_tail():
    cand = candidates(["one-third", "of", "the", "total", "staked", "supermajority", "link"])
    assert "supermajority link" in cand        # content head AND tail
    assert "one-third" in cand
    assert "one-third of" not in cand          # tail stopword
    assert "the total" not in cand             # head stopword
    assert "of" not in cand and "the" not in cand


# ── extract_concepts ──────────────────────────────────────────────────────────

def test_extract_merges_plurals_and_applies_min_df():
    statements = [
        "validator votes count",
        "validators count again",      # validators → validator (base present in axiom 1)
        "unrelated singleton phrase",
    ]
    axiom_concepts, info = extract_concepts(statements)
    # 'validator' appears in axioms 0 and 1 (after folding) → df 2 → a concept
    assert "validator" in info and info["validator"]["df"] == 2
    assert "validator" in axiom_concepts[0] and "validator" in axiom_concepts[1]
    # 'singleton' appears once → df 1 → not a concept
    assert "singleton" not in info


def test_extract_one_third_cluster():
    statements = [
        "an attacker can prevent finality by voting with one-third of the stake",
        "reverting a finalized block requires losing one-third of the staked eth",
        "casper ffg is safe when fewer than one-third of validators are adversarial",
        "the inactivity leak bleeds inactive validators below one-third of total stake",
    ]
    _, info = extract_concepts(statements)
    assert "one-third" in info and info["one-third"]["df"] == 4


# ── idf quantization (byte-stable) ────────────────────────────────────────────

def test_idf_is_quantized_4dp():
    # ln(8/2) = ln 4 = 1.38629... → 1.3863
    assert idf(2, 8) == 1.3863
    assert str(idf(2, 8)) == "1.3863"     # byte-stable string form
    # ln(4/4) = 0 (generic concept in every axiom)
    assert idf(4, 4) == 0.0
