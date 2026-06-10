---
id: in-the-paper-s-approach-raft-first-switches
type: axiom
title: "In the paper's approach, Raft first switches to a transitional joint-consensus configuration, and only after it is committed does the system transition to the new configuration"
statement: "In the paper's approach, Raft first switches to a transitional joint-consensus configuration, and only after it is committed does the system transition to the new configuration."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: [once-a-server-adds-a-new-configuration-entry, the-thesis-describes-its-first-membership-change-approach, the-thesis-recommends-restricting-membership-changes-so-that]
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# In the paper's approach, Raft first switches to a transitional joint-consensus configuration, and only after it is committed does the system transition to the new configuration

In the paper's approach, Raft first switches to a transitional joint-consensus configuration, and only after it is committed does the system transition to the new configuration.

Evidence: [[https-raft-github-io-raft]].
[[once-a-server-adds-a-new-configuration-entry]]
[[the-thesis-describes-its-first-membership-change-approach]]
[[the-thesis-recommends-restricting-membership-changes-so-that]]
