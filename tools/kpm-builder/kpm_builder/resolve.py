"""kpm_builder.resolve — the contradiction → resolve loop (SPEC-resolve.md v2).

Detect contradiction candidates (mechanically), resolve them by grounding against
primary sources (LLM seam + ground.py), and record the established truth as a
first-class doctrine note. The resolution is held to the same evidential bar as
every axiom — a `reconciled` truth must be *entailed* by a cited passage.

This file (T1): the data model + the precise numeric machinery the value-
disagreement detector is built on (units + fraction/percent normalization +
complementary-equivalence), kept deliberately strict so detection is ~2 candidates,
not ~75.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml

from kpm_builder._util import atomic_write, read_frontmatters, slug
from kpm_builder.concepts import extract_concepts
from kpm_builder.relate import read_axioms, read_evidence
from kpm_builder.schema import ConfidenceBucket


# ── data model ────────────────────────────────────────────────────────────────

class Verdict(Enum):
    RECONCILED = "reconciled"   # apparent conflict resolves to one grounded truth
    DISTINCT = "distinct"       # they measure different subjects — not actually a conflict
    DISPUTE = "dispute"         # genuine same-quantity disagreement
    ERROR = "error"             # one axiom misrepresents its own source


@dataclass
class Contradiction:
    a_id: str
    b_id: str
    source: str            # "relate" | "value"
    detail: str = ""


@dataclass
class Resolution:
    a_id: str
    b_id: str
    status: Verdict
    truth: str = ""
    truth_passage_id: str | None = None
    explanation: str = ""
    basis: list[str] = field(default_factory=list)
    confidence: ConfidenceBucket = ConfidenceBucket.UNVERIFIED
    dissent: dict | None = None


@dataclass
class Measure:
    """A numeric assertion: a normalized value + its (singularized) unit token."""
    value: float
    unit: str
    raw: str


# ── numeric normalization (precise — fractions/percents/thousands) ────────────

_WORD_FRAC: dict[str, float] = {
    "one-third": 1 / 3, "two-thirds": 2 / 3, "one-half": 0.5, "three-quarters": 0.75,
    "one-quarter": 0.25, "one-fifth": 0.2, "two-fifths": 0.4, "three-fifths": 0.6,
    "four-fifths": 0.8, "one-sixth": 1 / 6, "five-sixths": 5 / 6,
}

#: Recognized number forms (order matters: word-fractions and composites before bare ints).
_NUM_RE = re.compile(
    r"(?<![\w.])("
    r"one-third|two-thirds|one-half|three-quarters|one-quarter|one-fifth|two-fifths|"
    r"three-fifths|four-fifths|one-sixth|five-sixths"
    r"|\d{1,3}(?:,\d{3})+|\d+\.\d+|\d+/\d+|\d+%|\d+"
    r")(?![\w])",
    re.IGNORECASE,
)

_UNIT_SKIP = frozenset(
    "of the a an to per in at is are was were and or that this its for with".split()
)
_WORD = re.compile(r"[a-z]+")   # NB: excludes '%' — it's part of the number, never a unit


def normalize_number(raw: str) -> float | None:
    """Normalize a number form to a float: word-fractions, ``a/b``, ``N%``, decimals,
    integers (thousands separators stripped). Returns None if unrecognized."""
    r = raw.strip().lower().replace(",", "")
    if r in _WORD_FRAC:
        return round(_WORD_FRAC[r], 3)
    try:
        if r.endswith("%"):
            return round(float(r[:-1]) / 100, 4)
        if "/" in r:
            num, den = r.split("/")
            return round(float(num) / float(den), 4)
        return float(r)
    except (ValueError, ZeroDivisionError):
        return None


def _singular(w: str) -> str:
    """Strip a single trailing plural ``s`` (so unit ``minute`` and concept ``minutes``
    compare equal). Conservative: only for words longer than 3 chars."""
    return w[:-1] if (w.endswith("s") and len(w) > 3) else w


def _unit_after(text: str, end: int) -> str:
    """The first content word following a number (skipping ``of the …``), singularized."""
    for w in _WORD.findall(text[end:end + 48].lower()):
        if w not in _UNIT_SKIP:
            return _singular(w)
    return ""


def extract_measures(statement: str) -> list[Measure]:
    """Pull every ``(value, unit)`` numeric assertion from a statement."""
    out: list[Measure] = []
    for m in _NUM_RE.finditer(statement):
        val = normalize_number(m.group(1))
        if val is not None:
            out.append(Measure(value=val, unit=_unit_after(statement, m.end()), raw=m.group(1)))
    return out


def measures_disagree(m1: Measure, m2: Measure, *, tol: float = 0.01, comp_tol: float = 0.02) -> bool:
    """True iff two measures carry the SAME (non-empty) unit, DIFFERENT values, and are
    not complementary (``x`` vs ``1−x`` on a fractional dimension — the same fact stated
    from opposite sides)."""
    if not m1.unit or m1.unit != m2.unit:
        return False
    if abs(m1.value - m2.value) <= tol:
        return False
    if abs(m1.value + m2.value - 1.0) <= comp_tol:   # complementary fractions
        return False
    return True


# ── detect (mechanical) ───────────────────────────────────────────────────────

def _axiom_fms(kpm_dir: str | Path) -> list[dict]:
    return [fm for fm in read_frontmatters(Path(kpm_dir) / "axioms") if fm.get("id")]


def _numberish(term: str) -> bool:
    return normalize_number(term) is not None


def detect_contradictions(
    kpm_dir: str | Path, *, idf_floor: float = 0.5, max_candidates: int = 50
) -> list[Contradiction]:
    """Mechanical contradiction candidates from two sources: Relate's verified
    ``contradicts`` edges, and value-disagreements (same-unit, differing,
    non-complementary numbers gated by a shared *non-numeric, non-unit* concept
    above an IDF floor). High precision by design — the resolver is the final gate."""
    fms = _axiom_fms(kpm_dir)
    ids = [fm["id"] for fm in fms]
    valid = set(ids)
    statements = [str(fm.get("statement", "")) for fm in fms]
    axiom_concepts, info = extract_concepts(statements)
    measures = [extract_measures(s) for s in statements]

    # Gating concepts: non-numeric, IDF-specific, and NOT a unit token of this axiom
    # (so "12.8 minutes" vs "6.4 minutes" — sharing only the unit "minute" — don't match).
    gating: list[set[str]] = []
    for i, concepts in enumerate(axiom_concepts):
        unit_stems = {m.unit for m in measures[i]}     # m.unit is already singularized
        gating.append({
            c for c in concepts
            if not _numberish(c) and info[c]["idf"] >= idf_floor and _singular(c) not in unit_stems
        })

    cands: list[Contradiction] = []
    seen: set[tuple[str, str]] = set()

    for fm in fms:
        for tgt in (fm.get("relations") or {}).get("contradicts") or []:
            if tgt in valid:
                key = tuple(sorted((fm["id"], tgt)))
                if key not in seen:
                    seen.add(key)
                    cands.append(Contradiction(key[0], key[1], source="relate"))

    n = len(fms)
    for i in range(n):
        for j in range(i + 1, n):
            key = tuple(sorted((ids[i], ids[j])))
            if key in seen or not (gating[i] & gating[j]):
                continue
            if any(measures_disagree(m1, m2) for m1 in measures[i] for m2 in measures[j]):
                seen.add(key)
                cands.append(Contradiction(key[0], key[1], source="value"))

    cands.sort(key=lambda c: (c.a_id, c.b_id, c.source))
    return cands[:max_candidates]


# ── resolve (LLM seam + ground.py — default to honesty) ───────────────────────

_RESOLVE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["reconciled", "distinct", "dispute", "error"]},
        "truth": {"type": "string"},
        "truth_passage_id": {"type": "string"},
        "error_axiom": {"type": "string"},
        "explanation": {"type": "string"},
        "basis": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "explanation"],
    "additionalProperties": False,
}

_RESOLVE_SYSTEM = """\
You are establishing the truth between two ideas that appear to conflict. Decide one status:
- reconciled: they appear to conflict but a concrete mechanism resolves it to ONE precise fact
  (a rounding/approximation of a precise value, a temporal change, a synonym). Put that single fact
  in `truth` and cite the ONE evidence id whose passage establishes it in `truth_passage_id`.
  CRITICAL — `truth` must contain ONLY the one precise fact that the cited passage entails. Do NOT
  bundle the other figure, a comparison, or any cross-passage reasoning into `truth` — put all of
  that in `explanation`. A `truth` that reaches past its one cited passage will be rejected and the
  verdict downgraded to dispute. (E.g. truth="finalizing a checkpoint takes 12.8 minutes / two
  epochs in-protocol", with the "~15 min is a rounded figure" reasoning in `explanation`.)
- distinct: the two axioms measure DIFFERENT quantities or subjects and do not actually conflict
  (e.g. block-finalization time vs epoch length; two differently-named constants). No reconciling
  truth is needed — explain why they are different.
- dispute: the sources genuinely disagree about the SAME quantity — record both positions.
- error: ONE axiom misrepresents its OWN cited source (name it in `error_axiom`).
Default to `dispute` when unsure about a same-quantity disagreement. Use ONLY the statements and
passages below."""


def _resolve_prompt(
    a_id: str, b_id: str,
    statements: dict[str, str],
    evidence_passages: dict[str, str],
    axiom_evidence: dict[str, list[str]],
) -> str:
    def block(aid: str) -> str:
        lines = [f"AXIOM {aid}: {statements.get(aid, '')}"]
        for eid in axiom_evidence.get(aid, []):
            lines.append(f"  evidence {eid}: {evidence_passages.get(eid, '')}")
        return "\n".join(lines)

    return (
        f"{_RESOLVE_SYSTEM}\n\n{block(a_id)}\n\n{block(b_id)}\n\n"
        'Respond with JSON only: {"status","truth","truth_passage_id","error_axiom",'
        '"explanation","basis"}.'
    )


def _default_ground(claim: str, passage: str, *, complete_json) -> str:
    """Ground a claim against a passage via the engine's grounder (independent check)."""
    from kpm_builder.ground import ground
    from kpm_builder.snapshot import snapshot
    snap = snapshot("internal://passage", fetcher=lambda u: passage,
                    fetched_at="2026-01-01T00:00:00Z")
    return ground(claim, snap, complete_json=complete_json).verdict


def resolve(
    cand: Contradiction,
    statements: dict[str, str],
    evidence_passages: dict[str, str],
    axiom_evidence: dict[str, list[str]],
    *,
    complete_json,
    ground_fn=None,
) -> Resolution:
    """Resolve one contradiction candidate to a grounded verdict.

    Sees only the two statements + their passages (never ``cand.detail`` — isolation).
    A ``reconciled`` truth must be *entailed* by a cited passage (re-checked via the
    grounder) or it downgrades to ``dispute``; an ``error`` is only kept if the accused
    axiom over-claims its OWN source. Malformed output → ``dispute`` (fail safe).
    """
    if ground_fn is None:
        def ground_fn(claim: str, passage: str) -> str:
            return _default_ground(claim, passage, complete_json=complete_json)

    a, b = cand.a_id, cand.b_id
    raw = complete_json(
        _resolve_prompt(a, b, statements, evidence_passages, axiom_evidence), _RESOLVE_SCHEMA
    )
    raw = raw if isinstance(raw, dict) else {}
    status = raw.get("status")
    explanation = str(raw.get("explanation", ""))
    basis = [e for e in (raw.get("basis") or []) if e in evidence_passages]
    dissent = {a: statements.get(a, ""), b: statements.get(b, "")}

    if status == "distinct":
        # Different subjects — not a conflict, no single truth to ground.
        return Resolution(a, b, Verdict.DISTINCT, explanation=explanation, basis=basis,
                          confidence=ConfidenceBucket.UNVERIFIED, dissent=dissent)

    if status == "reconciled":
        truth = str(raw.get("truth", ""))
        tp = raw.get("truth_passage_id")
        # The truth is a new claim — it must be entailed by its cited passage.
        if truth and tp in evidence_passages and ground_fn(truth, evidence_passages[tp]) == "entails":
            if tp not in basis:
                basis = [tp, *basis]
            # Single grounded source → PARTIAL: the doctrine caps single-source confidence
            # at PARTIAL (SUPPORTED would require corroboration — deferred to a later increment).
            return Resolution(a, b, Verdict.RECONCILED, truth=truth, truth_passage_id=tp,
                              explanation=explanation, basis=basis,
                              confidence=ConfidenceBucket.PARTIAL)
        # no entailing passage → cannot reconcile
        return Resolution(a, b, Verdict.DISPUTE, explanation=explanation, basis=basis,
                          confidence=ConfidenceBucket.UNVERIFIED, dissent=dissent)

    if status == "error":
        ea = raw.get("error_axiom")
        # The accused axiom must be one of THIS candidate's two (no hallucinated third id).
        if ea in (a, b) and ea in axiom_evidence:
            own_passage = "\n".join(evidence_passages.get(e, "") for e in axiom_evidence[ea])
            # Only an axiom that over-claims its OWN source is a real error; a faithfully
            # grounded minority position is a dispute, never marked wrong.
            if ground_fn(statements.get(ea, ""), own_passage) != "entails":
                return Resolution(a, b, Verdict.ERROR, explanation=explanation, basis=basis,
                                  confidence=ConfidenceBucket.UNVERIFIED, dissent=dissent)
        return Resolution(a, b, Verdict.DISPUTE, explanation=explanation, basis=basis,
                          confidence=ConfidenceBucket.UNVERIFIED, dissent=dissent)

    return Resolution(a, b, Verdict.DISPUTE, explanation=explanation, basis=basis,
                      confidence=ConfidenceBucket.UNVERIFIED, dissent=dissent)


# ── record (mechanical — a clusters/ doctrine note, additive & idempotent) ────

def record_resolution(kpm_dir: str | Path, res: Resolution, *, resolved: str) -> Path:
    """Persist a Resolution as a ``clusters/<a>__<b>.md`` note (doctrine + KG already
    understand ``clusters/``). Canonical + idempotent; never mutates axiom notes.
    ``resolved`` is the injected date (no clock)."""
    kpm_dir = Path(kpm_dir)
    cdir = kpm_dir / "clusters"
    cdir.mkdir(exist_ok=True)
    a, b = sorted([res.a_id, res.b_id])

    fm: dict = {"type": "resolution", "axioms": [a, b], "status": res.status.value,
                "basis": sorted(res.basis), "confidence": res.confidence.value, "resolved": resolved}
    if res.status is Verdict.RECONCILED:
        fm["truth"] = res.truth
        fm["truth_passage_id"] = res.truth_passage_id
    fm_yaml = yaml.safe_dump(fm, sort_keys=True, default_flow_style=False, allow_unicode=True).strip()

    text = f"---\n{fm_yaml}\n---\n\n# Resolution: {a} ↔ {b}\n\n{res.explanation or '(no explanation)'}\n"
    if res.dissent:
        text += "\n## Positions\n" + "".join(
            f"- **{k}**: {res.dissent[k]}\n" for k in sorted(res.dissent))

    path = cdir / f"{slug(a)}__{slug(b)}.md"
    atomic_write(path, text)
    return path


# ── orchestrate + CLI ─────────────────────────────────────────────────────────

def resolve_kpm(kpm_dir: str | Path, *, complete_json, resolved: str) -> list[Resolution]:
    """Detect contradiction candidates, resolve each (grounded), and record every
    resolution as a clusters/ note. Returns the resolutions."""
    axioms = read_axioms(kpm_dir)
    statements = {a.id: a.statement for a in axioms}
    axiom_evidence = {a.id: a.evidence_ids for a in axioms}
    evidence_passages = read_evidence(kpm_dir)

    out: list[Resolution] = []
    for cand in detect_contradictions(kpm_dir):
        res = resolve(cand, statements, evidence_passages, axiom_evidence,
                      complete_json=complete_json)
        record_resolution(kpm_dir, res, resolved=resolved)
        out.append(res)
    return out


def _build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog="python -m kpm_builder.resolve",
        description="Detect + resolve contradictions in a KPM, recording the truth (API path).",
    )
    p.add_argument("--kpm", required=True, help="Path to a produced KPM directory.")
    p.add_argument("--family", default="anthropic",
                   choices=["anthropic", "deepseek", "google"], help="Provider family.")
    p.add_argument("--resolved", default="2026-01-01", help="Resolution date (YYYY-MM-DD).")
    return p


def main(argv: list[str] | None = None) -> None:
    import collections

    args = _build_parser().parse_args(argv)
    from kpm_builder.providers import Family, make_provider

    cj = make_provider(Family(args.family))
    res = resolve_kpm(args.kpm, complete_json=cj, resolved=args.resolved)
    counts = collections.Counter(r.status.value for r in res)
    print(f"resolved {len(res)} contradiction(s) in {args.kpm}: {dict(counts)}")


if __name__ == "__main__":
    main()
