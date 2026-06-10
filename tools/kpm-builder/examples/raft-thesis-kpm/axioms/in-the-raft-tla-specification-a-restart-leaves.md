---
id: in-the-raft-tla-specification-a-restart-leaves
type: axiom
title: "In the Raft TLA+ specification, a restart leaves currentTerm, votedFor, and log unchanged while resetting commitIndex to 0, formally encoding the persistent-versus-volatile state classification"
statement: "In the Raft TLA+ specification, a restart leaves currentTerm, votedFor, and log unchanged while resetting commitIndex to 0, formally encoding the persistent-versus-volatile state classification."
domain: "distilled"
generativity: 3
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [raft-s-persistent-state-on-every-server-is]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raw-githubusercontent-com-ongardie-raft-tla-master-raft]
provenance: "package-research/distilled"
---

# In the Raft TLA+ specification, a restart leaves currentTerm, votedFor, and log unchanged while resetting commitIndex to 0, formally encoding the persistent-versus-volatile state classification

In the Raft TLA+ specification, a restart leaves currentTerm, votedFor, and log unchanged while resetting commitIndex to 0, formally encoding the persistent-versus-volatile state classification.

Evidence: [[https-raw-githubusercontent-com-ongardie-raft-tla-master-raft]].
[[raft-s-persistent-state-on-every-server-is]]
