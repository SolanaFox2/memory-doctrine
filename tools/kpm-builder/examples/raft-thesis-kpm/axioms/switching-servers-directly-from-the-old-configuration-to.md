---
id: switching-servers-directly-from-the-old-configuration-to
type: axiom
title: "Switching servers directly from the old configuration to the new is unsafe because the change cannot be applied atomically, so the cluster can split into two independent majorities during the transition"
statement: "Switching servers directly from the old configuration to the new is unsafe because the change cannot be applied atomically, so the cluster can split into two independent majorities during the transition."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [in-the-paper-s-approach-raft-first-switches]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Switching servers directly from the old configuration to the new is unsafe because the change cannot be applied atomically, so the cluster can split into two independent majorities during the transition

Switching servers directly from the old configuration to the new is unsafe because the change cannot be applied atomically, so the cluster can split into two independent majorities during the transition.

Evidence: [[https-raft-github-io-raft]].
[[in-the-paper-s-approach-raft-first-switches]]
