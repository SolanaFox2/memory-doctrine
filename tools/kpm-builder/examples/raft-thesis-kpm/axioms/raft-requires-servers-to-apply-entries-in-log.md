---
id: raft-requires-servers-to-apply-entries-in-log
type: axiom
title: "Raft requires servers to apply entries in log index order, which combined with the State Machine Safety Property means all servers apply exactly the same set of log entries to their state machines in the same order"
statement: "Raft requires servers to apply entries in log index order, which combined with the State Machine Safety Property means all servers apply exactly the same set of log entries to their state machines in the same order."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [state-machine-safety-if-a-server-has-applied]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Raft requires servers to apply entries in log index order, which combined with the State Machine Safety Property means all servers apply exactly the same set of log entries to their state machines in the same order

Raft requires servers to apply entries in log index order, which combined with the State Machine Safety Property means all servers apply exactly the same set of log entries to their state machines in the same order.

Evidence: [[https-raft-github-io-raft]].
[[state-machine-safety-if-a-server-has-applied]]
