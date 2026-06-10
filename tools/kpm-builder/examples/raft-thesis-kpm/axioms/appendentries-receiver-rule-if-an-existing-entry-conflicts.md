---
id: appendentries-receiver-rule-if-an-existing-entry-conflicts
type: axiom
title: "AppendEntries receiver rule"
statement: "AppendEntries receiver rule: if an existing entry conflicts with a new one (same index but different terms), delete the existing entry and all that follow it."
domain: "distilled"
generativity: 5
confidence: 0.5
status: candidate
relations:
  derives-from: [raft-handles-inconsistencies-by-forcing-followers-logs-to]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# AppendEntries receiver rule

AppendEntries receiver rule: if an existing entry conflicts with a new one (same index but different terms), delete the existing entry and all that follow it.

Evidence: [[https-raft-github-io-raft]].
[[raft-handles-inconsistencies-by-forcing-followers-logs-to]]
