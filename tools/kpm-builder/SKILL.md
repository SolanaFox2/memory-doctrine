---
name: kpm-build
description: >-
  Research a topic from scratch into a doctrine-conformant knowledge package (KPM).
  You scope it once; the skill dispatches research subagents, grounds every claim against
  its source (an independent, isolated check), scores confidence from evidence, and assembles
  a labeled package — honestly reporting what it answered, what's thin, and what it couldn't
  reach. Runs on a Claude subscription alone; an optional DeepSeek/Gemini key upgrades the
  grounding to cross-family. Use when the user wants a researched, cited, honestly-weighted
  knowledge package on a topic — not when they already have the notes (use the Organizer,
  package-research, for that).
---

# KPM Builder — `/kpm-build`

You are the orchestrator of an autonomous research build. The user gives a goal; you research
it from scratch and return a knowledge package that obeys the Memory Doctrine's own rules for
good knowledge. **The thinking is done by you and your subagents; the mechanical assembly is
done by the Python engine** (`kpm_builder`). You connect them.

**Non-negotiable principles** (these are the doctrine applied to the build itself):
- **Ground or drop.** Every claim must quote a real source passage that an *independent*
  check confirms actually entails it. No entailing span → the claim does not ship.
- **The grounder is isolated.** Whoever grounds a claim sees ONLY the source text + the claim
  — never the reasoning of whoever drafted it. Same family is fine; isolated context is the point.
- **Confidence is corpus-relative.** A claim's confidence is conditional on the sources being
  right. Say so. Never present it as absolute truth.
- **Abstain, don't fabricate.** Thin or contested evidence yields an honest gap or a research
  log — never an up-filled package. "We don't know" is a success.
- **Scope-bounded.** Only gather what serves the contract. Off-topic material is dropped.
- **Mature topics only (v1).** This lens distills settled-consensus knowledge. For genuinely
  unsettled/contested topics, tell the user it's out of scope (the honest artifact there is a
  disagreement map, a future lens).

## Setup

The engine runs from the workspace with:
```
export PYTHONPATH=tools/kpm-builder:tools/package-research/src
```
Optional, for cross-family grounding: `pip install anthropic` (the SDK), then `export DEEPSEEK_API_KEY=…` (or `GOOGLE_GENAI_API_KEY`).
Without a key, you ground with Claude subagents (the subscription path) — fully supported.

## The procedure

### 1 — Scope intake (the one upfront human step)
Produce a **Scope Contract**. Ask the user (or derive from their request) and confirm:
- **goal / use** — what the package is *for* (decides what's "useful")
- **core questions** — the specific questions it must answer (these become beats and define "done")
- **in scope / out of scope** — explicit boundaries (the relevance filter's ground truth)
- **audience / depth**, **source profile** (preferred kinds + recency)
Keep it tight (5–8 questions). The contract is the spine of everything below.

### 2 — Beat plan
Decompose each core question into 1–3 **beats** (researchable sub-questions). Aim for beats
that ≥2 independent sources could each answer — single-source beats will honestly *abstain*
(the engine requires ≥2 independent quality sources to mark a question "answered").

> **DEPTH IS SET HERE, NOT IN RESEARCH (a hard-won lesson).** The breadth and depth of the final
> package are bounded by the beat plan, not by how hard the research subagents work. So **match the
> beat decomposition to the depth you promised:**
> - **lite / standard** — decompose from an authoritative *overview* (an intro paper, an official
>   docs landing page). ~5–8 beats, ~25–40 axioms.
> - **thesis / comprehensive** — decompose from the **deepest canonical source's full structure**
>   (a textbook or PhD thesis's *chapters*, a spec's *full section list*) — NOT an introductory
>   paper's sections. Include the dimensions intro papers omit: persistence/operational invariants,
>   the formal proofs/invariants, evaluation/performance, edge cases, the practice/implementation
>   chapters, related work. ~12–16 beats, ~100–160 axioms. **Mine the deepest source and any formal
>   spec for axioms** (don't let them sit cited-but-unmined). Also raise the per-beat density on the
>   subtle, proof-heavy areas (commitment, safety, membership) — weight axioms toward *difficulty*,
>   not ease of restatement.
>
> **Limit to remember:** the engine's coverage label is **scope-relative** — `converged` means you
> covered *your beats*, NOT that your beats were deep enough. Only the beat plan can be too shallow,
> and the engine can't catch that. That judgment is yours, here, at scoping. (Audit a finished
> package against the deepest source's table of contents to check for whole missing dimensions.)

### 3 — Research wave (dispatch subagents — this is the breadth)
For **each beat**, dispatch a research subagent (the Agent tool). Tell it the contract + the
beat question. It must return, as JSON, **3–5 sources** and **candidate claims**:
```
{"sources":[{"url","text","venue"}...],
 "claims":[{"statement","source_url","supporting_passage"}...]}
```
Rules for the subagent: prefer primary/reputable sources matching the source profile; `text`
is the actual passage it read (you will hash it); each claim must cite one `source_url` and
the exact `supporting_passage` from it.

**Scope each claim to its passage — this is the single biggest quality lever.** A claim must be
*entailed by the exact passage it cites*: do not add scope, mechanism, comparison, causation,
recency, or numbers the passage doesn't contain. If the passage is narrow, the claim must be
narrow. Concretely — if the passage only states "users wait one week to withdraw," draft *that*,
not the whole rollup mechanism; if it lists slashable behaviors but not the 32 ETH penalty,
don't mention the penalty. A claim that reaches past its passage will be flagged `over_claims`
and dropped at grounding (so the work is wasted and the question may go unanswered). If you need
a broader claim, cite a *longer* passage that actually supports it, or split it into two claims
each tied to its own passage. Tight, passage-faithful claims are what ship.

### 4 — Ground every claim (the rigor step — INDEPENDENT + isolated)
For **each claim**, get a verdict in `{entails, over_claims, reject}`:
- **Subscription path (default):** dispatch a *separate* grounder subagent given ONLY the
  `supporting_passage` + the `statement` (NOT the research subagent's reasoning). Prompt it as
  an independent verifier: *does the source entail the claim — no more generality, certainty,
  scope, quantity, causality, or recency than the source supports?* Return `entails` /
  `over_claims` / `reject`. (You may batch several claims in one grounder call, but never let
  it see the drafting rationale.)
- **Cross-family path (if a key is set):** stronger — a different family doesn't share Claude's blind spots:
  ```python
  from kpm_builder.providers import Family, make_provider
  from kpm_builder.ground import ground
  ground(claim, snapshot, complete_json=make_provider(Family.DEEPSEEK))
  ```
Also note, per claim: `n_corroborations` = how many *independent* sources in the beat support
the same statement (distinct authors/venues, not distinct URLs), and `survived_refuter` (v1:
true unless you ran a refuter and it broke the claim).

### 5 — (Optional, scale) Refute & gap-check
For surviving claims, you may dispatch a refuter subagent that tries to break each using the
beat's *other* sources (not the claim's own). And a gap critic: "what does the gathered corpus
say is important that the beats missed?" Re-open a beat if it surfaces something material. v1
can skip these; they raise rigor.

### 6 — Assemble the research JSON
Collect everything into the engine's input shape:
```json
{"contract":{"goal","in_scope","out_of_scope"},
 "beats":[{"question","claims":[
   {"statement","source":{"url","text","venue"},
    "ground_verdict","n_corroborations","survived_refuter","generativity"}]}]}
```
`generativity` (1–5) = how much else in the package derives from this claim — *your* judgment,
made **without reference to its confidence** (keep the two orderings separate).

### 7 — Build (the mechanical finalize — the engine)
```
python -m kpm_builder.cli build --input research.json --out <out_dir> \
  --run-date $(date +%F) --fetched-at $(date -u +%FT%TZ)
```
The engine snapshots each source, classifies its tier, scores confidence (capped by tier — a
blog can't support more than a blog), labels each question (answered / partial / abstained /
not-reached), and either assembles a doctrine KPM (running the linter) or — if too thin —
writes a `research_log.json` instead of a package that would lie about being complete.

### 8 — Relate (turn the star into a web — INDEPENDENT, like grounding)
A freshly-assembled KPM pins each axiom to its source but **not to the other axioms** — and the
doctrine's value is in the connections (A2). Add **verified** typed edges *between* axioms:
- **Propose:** one subagent reads all axioms (`(id, statement)` from `<out_dir>/axioms/`) and
  proposes directed edges `{from_id, to_id, type, rationale}`, `type ∈ {supports, derives-from,
  generalizes, contradicts}`, ≤5 out of any one axiom. Over-propose — the verifier is the gate.
- **Verify (default-drop):** for EACH candidate, a *separate* subagent sees ONLY the two
  statements (labelled FROM / TO) + the type's directional meaning — and, for `supports` /
  `derives-from`, the two source passages — never the proposer's rationale or the other axioms.
  Frame it to **refute**: *"find a concrete reason this relation fails in this direction; answer
  holds=true only if you cannot."* Default false on doubt. (Mirrors grounding's isolation.)
- **Write:** hand the verified edges to the mechanical writer — it edits the axiom frontmatter,
  adds matching `[[wikilinks]]`, and re-lints (raises rather than emit a broken KPM):
  ```python
  from kpm_builder.relate import RelateResult, Relation, RelationType
  from kpm_builder.apply_relations import apply_relations
  apply_relations(out_dir, RelateResult(relations=[
      Relation(from_id="a-…", to_id="a-…", type=RelationType.SUPPORTS, verified=True)]))
  ```
  Cross-family path (if a key is set): `python -m kpm_builder.relate --kpm <out_dir> --family deepseek`
  runs propose → verify → write end-to-end with an API provider.
- If verification rejects everything, ship **zero** relations — a thin honest web beats a fake
  one. v1 relates only; corroboration→SUPPORTED (the confidence lift) is a later increment.
- **Then compile the graph substrate:** `python -m kpm_builder.graph_index --kpm <out_dir>` writes
  `graph/index.json` — concept nodes + `mentions` edges (structural) + the verified relations
  (trust-tagged) — so the package is efficiently traversable. The dense concept adjacency is
  *derived on demand* (`load_graph(...).shares_concept(...)`), bounded and opt-in; default traversal
  stays verified-only (doctrine A1 — no indiscriminate links). The notes remain source-of-truth.
- **Then resolve contradictions (establish truth):** `detect_contradictions` finds candidates (Relate
  `contradicts` edges + same-unit value-disagreements). For each, a subagent returns one of
  `reconciled | distinct | dispute | error`. **Scope the `truth` to its passage:** a `reconciled`
  truth must contain ONLY the single precise fact its cited passage *entails* (e.g. "finalizing takes
  12.8 minutes / two epochs in-protocol") — the cross-passage reasoning ("~15 min is the rounded
  figure") goes in `explanation`. The truth is re-checked through the grounder and **downgraded to
  `dispute`** if it reaches past its passage. `distinct` = the two measure different subjects (not a
  conflict); `error` only stands if the accused axiom over-claims its *own* source. Each resolution is
  recorded as a `clusters/<a>__<b>.md` note — never mutating the axioms. CLI:
  `python -m kpm_builder.resolve --kpm <out_dir>`. Truth-seeking made a durable step, not a one-off.

### 9 — Deliver honestly
Present the engine's outcome to the user *as it is*:
- `converged` → a complete-relative-to-scope KPM. Show the coverage table + where it lives.
- `scope_partially_researchable` → a KPM with gaps; name the abstained questions.
- `research_log_only` → **not** a package — say "the evidence was too thin to package; here's
  the research log," and offer to broaden scope or add sources.
Every confidence is **corpus-relative** — frame it that way. Surface any contested/dangerous
findings rather than asserting them.

## Cost & autonomy
A standard build is many subagents over several beats and review rounds (roughly 0.5–1.5M
tokens; minutes to tens of minutes). Bound it: cap the number of beats and sources per the
contract, stop dispatching when the budget the user set is reached, and prefer the `lite`
shape (fewer beats, one ground pass) for quick scans. The human is in exactly two places —
the scope intake and reading the delivered package; everything between is autonomous.

## What this is not
Not the Organizer (`package-research`) — that packages notes you already have; this researches
from scratch. Not a search engine — it produces a *structured, grounded, labeled* package, not
a list of links. Not an oracle — its confidence is conditional on its corpus, and it will tell
you when it doesn't know.
