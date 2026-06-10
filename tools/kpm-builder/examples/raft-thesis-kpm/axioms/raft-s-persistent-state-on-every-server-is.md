---
id: raft-s-persistent-state-on-every-server-is
type: axiom
title: "Raft's persistent state on every server is currentTerm, votedFor, and log[], and this state must be written to stable storage before the server responds to RPCs"
statement: "Raft's persistent state on every server is currentTerm, votedFor, and log[], and this state must be written to stable storage before the server responds to RPCs."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: [each-server-persists-its-current-term-and-vote]
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Raft's persistent state on every server is currentTerm, votedFor, and log[], and this state must be written to stable storage before the server responds to RPCs

Raft's persistent state on every server is currentTerm, votedFor, and log[], and this state must be written to stable storage before the server responds to RPCs.

Evidence: [[https-raft-github-io-raft]].
[[each-server-persists-its-current-term-and-vote]]
