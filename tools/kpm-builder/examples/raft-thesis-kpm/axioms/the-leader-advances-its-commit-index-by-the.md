---
id: the-leader-advances-its-commit-index-by-the
type: axiom
title: "The leader advances its commit index by the rule"
statement: "The leader advances its commit index by the rule: if there exists an N such that N > commitIndex, a majority of matchIndex[i] >= N, and log[N].term == currentTerm, then set commitIndex = N."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: [a-log-entry-is-committed-once-the-leader]
  supports: [raft-never-commits-log-entries-from-previous-terms]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# The leader advances its commit index by the rule

The leader advances its commit index by the rule: if there exists an N such that N > commitIndex, a majority of matchIndex[i] >= N, and log[N].term == currentTerm, then set commitIndex = N.

Evidence: [[https-raft-github-io-raft]].
[[a-log-entry-is-committed-once-the-leader]]
[[raft-never-commits-log-entries-from-previous-terms]]
