"""kpm_builder.concepts — mechanical, domain-agnostic concept extraction (L0).

Pure stdlib, NO LLM, NO network. Turns axiom statements into weighted concept
candidates used to build the graph substrate (see SPEC-graph-substrate.md v2).

Pipeline: tokenize → singularize (corpus-guarded) → 1–3-gram candidates
(stopword head/tail dropped) → document frequency → keep df ≥ MIN_DF → IDF.
IDF is Decimal-quantized (libm log is not byte-portable; never bare round()).
"""
from __future__ import annotations

import math
import re
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal

MIN_DF = 2
_IDF_DP = Decimal("0.0001")

# Domain-agnostic English stoplist (inline, frozen — no NLTK/sklearn dependency).
STOPWORDS: frozenset[str] = frozenset("""
a an the and or but nor not of to in on at by for with from into onto over under
as is are was were be been being am this that these those it itself its their there
here he she they we you your our my me him us them his her then than thus so such
do does did doing have has had having will would shall should can could may might must
one two each every all any some no any if while until because about above below up
down out off again further once more most other own same too very per via while
between within without across upper lower toward towards only also just both either
neither when where which who whom whose why how what whether against during before
after how's it's that's
""".split())

# token = word run optionally joined by -, _, /, . (keeps one-third, 2/3, 12.8, a_b)
_TOKEN = re.compile(r"[a-z0-9]+(?:[-_/.][a-z0-9]+)*")
_POSSESSIVE = re.compile(r"['’]s\b")


def _is_numeric(tok: str) -> bool:
    """True for tokens that are purely numeric once separators are removed (32, 2/3, 12.8)."""
    stripped = tok.replace("/", "").replace(".", "").replace("-", "").replace("_", "")
    return stripped.isdigit()


def tokenize(text: str) -> list[str]:
    """Lowercase, strip possessive ``'s``, and split into content tokens.

    Keeps hyphen/slash/numeric tokens (``one-third``, ``2/3``, ``12.8``) and
    ALLCAPS identifiers (lowercased, underscores intact). Drops tokens ≤2 chars
    unless purely numeric.
    """
    text = _POSSESSIVE.sub("", text.lower())
    out: list[str] = []
    for tok in _TOKEN.findall(text):
        if _is_numeric(tok) or len(tok) > 2:
            out.append(tok)
    return out


def singularize(tok: str, vocab: set[str]) -> str:
    """Fold ``Xs``/``Xes`` → ``X`` ONLY when ``X`` already occurs in the corpus
    vocabulary — so ``validators``→``validator`` but never ``bias``→``bia``.

    Tries the shorter strip (``s``) before ``es`` so ``caches``→``cache`` (not
    ``cach``) when both bases could exist; the most conservative real base wins."""
    for suf in ("s", "es"):
        if tok.endswith(suf):
            base = tok[: -len(suf)]
            if len(base) >= 3 and base in vocab:
                return base
    return tok


def candidates(tokens: list[str]) -> set[str]:
    """1–3-gram candidate concepts. Unigram stopwords are dropped; multi-word
    grams whose first OR last token is a stopword are dropped (require a content
    head AND tail), killing junk like ``"one-third of"`` / ``"the total"``."""
    out: set[str] = set()
    n = len(tokens)
    for size in (1, 2, 3):
        for i in range(n - size + 1):
            gram = tokens[i : i + size]
            if size == 1:
                if gram[0] not in STOPWORDS:
                    out.add(gram[0])
            elif gram[0] not in STOPWORDS and gram[-1] not in STOPWORDS:
                out.add(" ".join(gram))
    return out


def idf(df: int, n: int) -> float:
    """ln(N/df), Decimal-quantized to 4 dp (ROUND_HALF_UP) for byte-portability."""
    val = math.log(n / df)
    return float(Decimal(str(val)).quantize(_IDF_DP, rounding=ROUND_HALF_UP))


def extract_concepts(
    statements: list[str], *, min_df: int = MIN_DF
) -> tuple[list[set[str]], dict[str, dict]]:
    """Extract concepts from a list of axiom statements.

    Returns ``(axiom_concepts, info)`` where ``axiom_concepts[i]`` is the set of
    concept ids mentioned by statement i, and ``info[concept] = {"df", "idf"}``.
    A candidate is a concept iff it occurs in ≥ ``min_df`` statements (no upper
    cap — generics are suppressed by low IDF, never hard-deleted).
    """
    token_lists = [tokenize(s) for s in statements]
    vocab: set[str] = set().union(*token_lists) if token_lists else set()
    folded = [[singularize(t, vocab) for t in toks] for toks in token_lists]
    axiom_cands = [candidates(toks) for toks in folded]

    df: Counter[str] = Counter()
    for cand in axiom_cands:
        df.update(cand)

    n = len(statements)
    concepts = {g: d for g, d in df.items() if d >= min_df}
    info = {g: {"df": d, "idf": idf(d, n)} for g, d in concepts.items()}
    axiom_concepts = [{g for g in cand if g in concepts} for cand in axiom_cands]
    return axiom_concepts, info
