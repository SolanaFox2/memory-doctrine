---
id: commitindex-and-lastapplied-are-volatile-state-on-all
type: axiom
title: "commitIndex and lastApplied are volatile state on all servers, each initialized to 0 and increasing monotonically"
statement: "commitIndex and lastApplied are volatile state on all servers, each initialized to 0 and increasing monotonically."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: [figure-2-lists-lastapplied-as-volatile-but-the]
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# commitIndex and lastApplied are volatile state on all servers, each initialized to 0 and increasing monotonically

commitIndex and lastApplied are volatile state on all servers, each initialized to 0 and increasing monotonically.

Evidence: [[https-raft-github-io-raft]].
[[figure-2-lists-lastapplied-as-volatile-but-the]]
