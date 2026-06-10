---
id: the-broadcast-time-should-be-an-order-of
type: axiom
title: "The broadcast time should be an order of magnitude less than the election timeout, and the election timeout should be a few orders of magnitude less than MTBF, so the system makes steady progress"
statement: "The broadcast time should be an order of magnitude less than the election timeout, and the election timeout should be a few orders of magnitude less than MTBF, so the system makes steady progress."
domain: "distilled"
generativity: 3
confidence: 0.5
status: candidate
relations:
  derives-from: [raft-can-elect-and-maintain-a-steady-leader]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# The broadcast time should be an order of magnitude less than the election timeout, and the election timeout should be a few orders of magnitude less than MTBF, so the system makes steady progress

The broadcast time should be an order of magnitude less than the election timeout, and the election timeout should be a few orders of magnitude less than MTBF, so the system makes steady progress.

Evidence: [[https-raft-github-io-raft]].
[[raft-can-elect-and-maintain-a-steady-leader]]
