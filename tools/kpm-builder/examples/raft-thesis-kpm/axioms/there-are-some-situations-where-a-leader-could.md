---
id: there-are-some-situations-where-a-leader-could
type: axiom
title: "There are some situations where a leader could safely conclude that an older log entry is committed (for example if that entry is stored on every server), but Raft takes a more conservative approach for simplicity"
statement: "There are some situations where a leader could safely conclude that an older log entry is committed (for example if that entry is stored on every server), but Raft takes a more conservative approach for simplicity."
domain: "distilled"
generativity: 3
confidence: 0.5
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

# There are some situations where a leader could safely conclude that an older log entry is committed (for example if that entry is stored on every server), but Raft takes a more conservative approach for simplicity

There are some situations where a leader could safely conclude that an older log entry is committed (for example if that entry is stored on every server), but Raft takes a more conservative approach for simplicity.

Evidence: [[https-raft-github-io-raft]].
[[raft-never-commits-log-entries-from-previous-terms]]
