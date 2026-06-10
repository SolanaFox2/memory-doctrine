---
id: the-leader-waits-for-its-state-machine-to
type: axiom
title: "The leader waits for its state machine to advance at least as far as readIndex, which is current enough to satisfy linearizability"
statement: "The leader waits for its state machine to advance at least as far as readIndex, which is current enough to satisfy linearizability."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [in-the-read-index-procedure-the-leader-saves]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# The leader waits for its state machine to advance at least as far as readIndex, which is current enough to satisfy linearizability

The leader waits for its state machine to advance at least as far as readIndex, which is current enough to satisfy linearizability.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[in-the-read-index-procedure-the-leader-saves]]
