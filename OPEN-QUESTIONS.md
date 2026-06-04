# Open Questions

The doctrine is *made to be argued with* — and that includes being honest about
what its **standard hasn't settled.** These are known gaps: places where building
and running the consuming tool (`tools/package-research`) stress-tested the
standard and surfaced a question the theory hasn't answered.

Each question states the gap, the current stance, and what evidence would move it.
Challenge them the same way you'd [challenge an axiom](CONTRIBUTING.md).

---

## Q1 — What is the status of *un-distilled* source material?

**The gap.** The standard recognizes two kinds of note: **axioms** (the distilled,
load-bearing ideas) and **evidence** (the cited source behind them). It has no
category for *source you want to keep but haven't distilled into an axiom.* The
implicit assumption was that everything is either load-bearing (→ axiom + evidence)
or noise. In practice there's a third bucket: real content that didn't rise to an
axiom but isn't garbage either.

**Why it matters.** When a tool distills a folder of notes, sources that no axiom
cites are, by the strict standard, not "evidence" — so they fall out of the
package entirely. On large or redundant corpora that can be a large fraction of
the input. Distillation quality then silently controls what's retained.

**Current stance.** The tool added an opt-in `reference/` bucket (`type:
reference`, `status: uncited`) that preserves un-cited sources, plus an always-on
coverage report so nothing is dropped without being named. The standard's linter
**ignores** `reference/`, so this is a *tool* concept, deliberately **outside** the
standard — a labeled holding area, not claimed as evidence.

**The open decision.**
- **(a) Keep it tool-level** — only distilled, cited knowledge is part of a
  knowledge package; un-distilled source is a staging concern. *Current lean.*
- **(b) Promote it** — define a third tier (index → evidence → reference) and have
  the linter acknowledge it (a reference note must be `status: uncited` and must
  not be cited by any axiom). Makes "preserve, don't silently drop" a first-class
  rule of the standard.

**What would move it.** Evidence so far: the size of the un-cited bucket varies as
much with the distiller's citing breadth as with the corpus, so it isn't a fixed
property of a well-formed package. That leans toward (a). Consistent large buckets
that clearly *should* have been retained would argue for (b).

---

## Q2 — Should the standard assess *source quality*?

**The gap.** The standard says confidence is *earned from evidence*, and checks
confidence per-axiom — but neither the standard nor the tool judges whether a
*source* is worth distilling at all. Noise-trimming removes process *sections*
(methodology, follow-up lists) by heading; it cannot tell a real finding from a
malformed source (e.g. a failed web scrape whose body is off-topic boilerplate).
Point a tool at a corpus where most sources are junk and it will faithfully
ingest, preserve, and structure the junk. Garbage in → garbage packaged.

**Current stance.** Out of scope for the tool today: it organizes what it is given,
and source quality is the author's responsibility. The limit is documented, and
narrowing the input by hand is the current mitigation.

**The open decision.**
- **(a) Out of scope** — keep the tool a faithful organizer; make the limit loud.
  *Current lean.*
- **(b) A quality pre-filter** in the tool — drop sources that are mostly link
  lists, or whose content is near-duplicated boilerplate across many files. A
  tool concern, not a standard change.
- **(c) A standard-level signal** — a per-source quality score that *caps* the
  confidence of any axiom resting on a low-quality source. This would make source
  quality part of how confidence is earned.

**What would move it.** (c) is the most doctrine-native (it ties quality to the
confidence axiom), but it's premature until (b) shows a quality signal can be
computed reliably.

---

*See also [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to challenge the doctrine,
and [`tools/package-research`](tools/package-research) for the tool whose use
surfaced these questions.*
