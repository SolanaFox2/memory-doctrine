---
id: G2-intention-lifecycle
type: axiom
cluster: G-prospective
title: Intention lifecycle — boost on open, inhibit on completion
statement: >
  Open intentions sit at heightened activation (intention-superiority effect) and must be
  actively inhibited on completion, not merely flagged done. Un-inhibited completed intentions
  perseverate — the agent re-fires discharged tasks. The lifecycle is: created → boosted
  (retrievability raised) → fired → inhibited (activation floor). The boost is a
  retrievability signal only; it must never be conflated with evidential confidence.
domain: working-prospective
generativity: 4
confidence: 0.74
status: locked
relations:
  derives-from: [D1-retrievability-decay]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: [trigger-layer, task-scheduler]
evidence: [goschke-1993-intention]
provenance: memory-research/working-prospective-deep
verification: {challenged: true, citations_checked: true, gate: "rt1+purge"}
---

# G2 · Intention lifecycle — boost on open, inhibit on completion

Pending intentions are not inert stored objects. [[goschke-1993-intention]] establishes the
**intention-superiority effect**: items from a to-be-executed script are recognized *faster*
than items from a merely memorized script — open intentions are held at **heightened
activation**, making them spontaneously accessible so the agent notices trigger cues (G1).

Critically, on completion the effect **reverses**: related items slow *below* neutral,
indicating **active inhibition** that prevents perseveration. "Mark as done" is insufficient;
the activation must be driven to a floor.

The lifecycle has four stages:

1. **Created** — intention node minted, activation at baseline.
2. **Boosted** — activation raised above baseline; agent is primed to notice trigger cues.
3. **Fired** — trigger matched; action executed.
4. **Inhibited** — activation dropped to floor; node remains in the graph for audit but no
   longer surfaces in normal retrieval.

The boost/inhibit signal lives entirely in **retrievability** — the volatile activation
dimension — and is governed by [[D1-retrievability-decay]]. It is strictly orthogonal to
evidential confidence ([[C2-three-orderings]]): a pending task is not more *true* than a
completed one; it is just more *active*.

**Guardrail:** A suppressed (inhibited) intention must remain a first-class retrieval
candidate during any C-tier or E4 adversarial audit pass — inhibition is invisible to
`kpm doctor` and re-grounding. This mirrors the D5 reversibility clause.

Evidence: [[goschke-1993-intention]].
