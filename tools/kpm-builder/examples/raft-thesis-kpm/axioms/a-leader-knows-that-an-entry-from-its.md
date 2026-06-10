---
id: a-leader-knows-that-an-entry-from-its
type: axiom
title: "A leader knows that an entry from its current term is committed once it is stored on a majority, but a leader cannot immediately conclude that an entry from a previous term is committed once it is stored on a majority"
statement: "A leader knows that an entry from its current term is committed once it is stored on a majority, but a leader cannot immediately conclude that an entry from a previous term is committed once it is stored on a majority."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [raft-never-commits-log-entries-from-previous-terms]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# A leader knows that an entry from its current term is committed once it is stored on a majority, but a leader cannot immediately conclude that an entry from a previous term is committed once it is stored on a majority

A leader knows that an entry from its current term is committed once it is stored on a majority, but a leader cannot immediately conclude that an entry from a previous term is committed once it is stored on a majority.

Evidence: [[https-raft-github-io-raft]].
[[raft-never-commits-log-entries-from-previous-terms]]
