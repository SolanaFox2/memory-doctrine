---
id: appendentries-receiver-rule-if-leadercommit-commitindex-set-commitindex
type: axiom
title: "AppendEntries receiver rule"
statement: "AppendEntries receiver rule: if leaderCommit > commitIndex, set commitIndex to the minimum of leaderCommit and the index of the last new entry."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [the-leader-tracks-the-highest-index-known-to]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# AppendEntries receiver rule

AppendEntries receiver rule: if leaderCommit > commitIndex, set commitIndex to the minimum of leaderCommit and the index of the last new entry.

Evidence: [[https-raft-github-io-raft]].
[[the-leader-tracks-the-highest-index-known-to]]
