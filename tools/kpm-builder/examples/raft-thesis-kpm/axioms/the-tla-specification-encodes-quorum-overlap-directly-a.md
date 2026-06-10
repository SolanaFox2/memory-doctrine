---
id: the-tla-specification-encodes-quorum-overlap-directly-a
type: axiom
title: "The TLA+ specification encodes quorum overlap directly"
statement: "The TLA+ specification encodes quorum overlap directly: a quorum is any subset whose cardinality exceeds half the servers, and the only important property is that every quorum overlaps with every other."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raw-githubusercontent-com-ongardie-raft-tla-master-raft]
provenance: "package-research/distilled"
---

# The TLA+ specification encodes quorum overlap directly

The TLA+ specification encodes quorum overlap directly: a quorum is any subset whose cardinality exceeds half the servers, and the only important property is that every quorum overlaps with every other.

Evidence: [[https-raw-githubusercontent-com-ongardie-raft-tla-master-raft]].
