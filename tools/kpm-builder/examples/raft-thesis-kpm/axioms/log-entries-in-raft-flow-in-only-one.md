---
id: log-entries-in-raft-flow-in-only-one
type: axiom
title: "Log entries in Raft flow in only one direction, outward from the leader in AppendEntries RPCs, whereas in Viewstamped Replication they flow in both directions, which adds mechanism and complexity"
statement: "Log entries in Raft flow in only one direction, outward from the leader in AppendEntries RPCs, whereas in Viewstamped Replication they flow in both directions, which adds mechanism and complexity."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [raft-has-less-mechanism-than-viewstamped-replication-and, raft-uses-a-stronger-form-of-leadership-than]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Log entries in Raft flow in only one direction, outward from the leader in AppendEntries RPCs, whereas in Viewstamped Replication they flow in both directions, which adds mechanism and complexity

Log entries in Raft flow in only one direction, outward from the leader in AppendEntries RPCs, whereas in Viewstamped Replication they flow in both directions, which adds mechanism and complexity.

Evidence: [[https-raft-github-io-raft]].
[[raft-has-less-mechanism-than-viewstamped-replication-and]]
[[raft-uses-a-stronger-form-of-leadership-than]]
