---
id: raft-ensures-safety-never-returning-an-incorrect-result
type: axiom
title: "Raft ensures safety (never returning an incorrect result) under all non-Byzantine conditions, including network delays, partitions, and packet loss, duplication, and reordering"
statement: "Raft ensures safety (never returning an incorrect result) under all non-Byzantine conditions, including network delays, partitions, and packet loss, duplication, and reordering."
domain: "distilled"
generativity: 5
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [raft-s-safety-must-not-depend-on-timing]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Raft ensures safety (never returning an incorrect result) under all non-Byzantine conditions, including network delays, partitions, and packet loss, duplication, and reordering

Raft ensures safety (never returning an incorrect result) under all non-Byzantine conditions, including network delays, partitions, and packet loss, duplication, and reordering.

Evidence: [[https-raft-github-io-raft]].
[[raft-s-safety-must-not-depend-on-timing]]
