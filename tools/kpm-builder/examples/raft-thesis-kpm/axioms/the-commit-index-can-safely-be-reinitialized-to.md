---
id: the-commit-index-can-safely-be-reinitialized-to
type: axiom
title: "The commit index can safely be reinitialized to zero on a restart because it is reconstructed"
statement: "The commit index can safely be reinitialized to zero on a restart because it is reconstructed: once a leader is elected and commits a new entry, its commit index advances and propagates to followers."
domain: "distilled"
generativity: 3
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [commitindex-and-lastapplied-are-volatile-state-on-all]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# The commit index can safely be reinitialized to zero on a restart because it is reconstructed

The commit index can safely be reinitialized to zero on a restart because it is reconstructed: once a leader is elected and commits a new entry, its commit index advances and propagates to followers.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[commitindex-and-lastapplied-are-volatile-state-on-all]]
