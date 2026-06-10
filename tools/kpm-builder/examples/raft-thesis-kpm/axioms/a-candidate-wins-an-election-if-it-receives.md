---
id: a-candidate-wins-an-election-if-it-receives
type: axiom
title: "A candidate wins an election if it receives votes from a majority of the servers in the full cluster for the same term"
statement: "A candidate wins an election if it receives votes from a majority of the servers in the full cluster for the same term."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: [the-tla-specification-encodes-quorum-overlap-directly-a]
  supports: [election-safety-at-most-one-leader-can-be]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# A candidate wins an election if it receives votes from a majority of the servers in the full cluster for the same term

A candidate wins an election if it receives votes from a majority of the servers in the full cluster for the same term.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[election-safety-at-most-one-leader-can-be]]
[[the-tla-specification-encodes-quorum-overlap-directly-a]]
