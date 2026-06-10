---
id: on-all-servers-if-commitindex-lastapplied-the-server
type: axiom
title: "On all servers, if commitIndex > lastApplied the server increments lastApplied and applies log[lastApplied] to its state machine"
statement: "On all servers, if commitIndex > lastApplied the server increments lastApplied and applies log[lastApplied] to its state machine."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [raft-requires-servers-to-apply-entries-in-log]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# On all servers, if commitIndex > lastApplied the server increments lastApplied and applies log[lastApplied] to its state machine

On all servers, if commitIndex > lastApplied the server increments lastApplied and applies log[lastApplied] to its state machine.

Evidence: [[https-raft-github-io-raft]].
[[raft-requires-servers-to-apply-entries-in-log]]
