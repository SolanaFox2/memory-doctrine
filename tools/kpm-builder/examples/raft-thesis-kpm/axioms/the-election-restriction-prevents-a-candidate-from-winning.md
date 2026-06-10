---
id: the-election-restriction-prevents-a-candidate-from-winning
type: axiom
title: "The election restriction prevents a candidate from winning unless its log contains all committed entries"
statement: "The election restriction prevents a candidate from winning unless its log contains all committed entries: a voter denies its vote if its own log is more up-to-date than the candidate's."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [leader-completeness-if-a-log-entry-is-committed]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# The election restriction prevents a candidate from winning unless its log contains all committed entries

The election restriction prevents a candidate from winning unless its log contains all committed entries: a voter denies its vote if its own log is more up-to-date than the candidate's.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[leader-completeness-if-a-log-entry-is-committed]]
