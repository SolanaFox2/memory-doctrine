---
id: when-a-follower-receives-a-snapshot-describing-a
type: axiom
title: "When a follower receives a snapshot describing a prefix of its log, the entries covered by the snapshot are deleted but entries following the snapshot are still valid and must be retained"
statement: "When a follower receives a snapshot describing a prefix of its log, the entries covered by the snapshot are deleted but entries following the snapshot are still valid and must be retained."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# When a follower receives a snapshot describing a prefix of its log, the entries covered by the snapshot are deleted but entries following the snapshot are still valid and must be retained

When a follower receives a snapshot describing a prefix of its log, the entries covered by the snapshot are deleted but entries following the snapshot are still valid and must be retained.

Evidence: [[https-raft-github-io-raft]].
