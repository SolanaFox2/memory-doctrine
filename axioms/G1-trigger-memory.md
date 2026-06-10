---
id: G1-trigger-memory
type: axiom
cluster: G-prospective
title: Prospective memory — prefer focal/event triggers over monitored polling
statement: >
  Remembering to DO something at the right future moment is a distinct memory system
  (prospective memory). Prefer focal/event triggers — bind the cue to a KG node the
  agent already traverses so retrieval is free — over costly monitoring/polling loops,
  which compete for the same finite attention budget and are unsustainable over long delays.
  Reserve context-gated polling only for nonfocal, high-stakes, time-based deadlines,
  and only when the trigger window is near.
domain: working-prospective
generativity: 5
confidence: 0.82
status: locked
relations:
  derives-from: [B1-spreading-activation, B3-capacity-cliff]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: [trigger-layer, task-scheduler]
evidence: [mcdaniel-2000-prospective]
provenance: memory-research/working-prospective-deep
verification: {challenged: true, citations_checked: true, gate: "rt1+purge"}
---

# G1 · Prospective memory — prefer focal/event triggers over polling

Prospective memory is the **"remember-to-DO"** axis of memory — orthogonal to the
retrospective "remember-what" graph that clusters A–F describe. An agent can recall
everything it knows and still fail to act on time if it has no trigger layer.

The multiprocess framework ([[mcdaniel-2000-prospective]]) proves two pathways:

- **Spontaneous (event/focal) retrieval:** a cue already processed by the ongoing task
  "pops" the intention into mind at zero sustained cost. Works when the trigger cue is
  **focal** — bound to a node the agent traverses during normal work.
- **Strategic monitoring (polling):** top-down, continuous scanning; measurably degrades
  ongoing-task performance; unsustainable over long delays. Required only when the cue is
  **nonfocal** (the agent wouldn't encounter it naturally).

This descends from [[B1-spreading-activation]] (retrieval = attention; a focal cue is
pre-matched by the attention mechanism) and from [[B3-capacity-cliff]] (monitoring competes
for the same finite attention budget — an unlimited polling strategy collapses the attention
cliff).

**KPM design rule:** Add a typed `intent`/`trigger` node carrying `(action, trigger-cue,
focal: bool, deadline, status)`. Embed the trigger cue on a KG node the agent already
traverses → spontaneous free retrieval. Gate polling to the deadline window only.

Evidence: [[mcdaniel-2000-prospective]].
