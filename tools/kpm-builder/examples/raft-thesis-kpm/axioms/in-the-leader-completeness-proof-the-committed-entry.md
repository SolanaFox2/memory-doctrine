---
id: in-the-leader-completeness-proof-the-committed-entry
type: axiom
title: "In the Leader Completeness proof, the committed entry must have been absent from the future leader's log at the time of its election, because leaders never delete or overwrite their own entries"
statement: "In the Leader Completeness proof, the committed entry must have been absent from the future leader's log at the time of its election, because leaders never delete or overwrite their own entries."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [a-leader-never-overwrites-or-deletes-entries-in]
  supports: [the-leader-completeness-proof-proceeds-by-contradiction-assume]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# In the Leader Completeness proof, the committed entry must have been absent from the future leader's log at the time of its election, because leaders never delete or overwrite their own entries

In the Leader Completeness proof, the committed entry must have been absent from the future leader's log at the time of its election, because leaders never delete or overwrite their own entries.

Evidence: [[https-raft-github-io-raft]].
[[a-leader-never-overwrites-or-deletes-entries-in]]
[[the-leader-completeness-proof-proceeds-by-contradiction-assume]]
