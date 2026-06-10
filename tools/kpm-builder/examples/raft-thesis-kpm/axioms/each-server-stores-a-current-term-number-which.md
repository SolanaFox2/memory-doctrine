---
id: each-server-stores-a-current-term-number-which
type: axiom
title: "Each server stores a current term number, which increases monotonically over time"
statement: "Each server stores a current term number, which increases monotonically over time."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [raft-divides-time-into-terms-numbered-with-consecutive]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Each server stores a current term number, which increases monotonically over time

Each server stores a current term number, which increases monotonically over time.

Evidence: [[https-raft-github-io-raft]].
[[raft-divides-time-into-terms-numbered-with-consecutive]]
