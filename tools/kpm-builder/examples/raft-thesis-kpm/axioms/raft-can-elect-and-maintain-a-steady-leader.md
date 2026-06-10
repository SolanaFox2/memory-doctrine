---
id: raft-can-elect-and-maintain-a-steady-leader
type: axiom
title: "Raft can elect and maintain a steady leader as long as the system satisfies the timing requirement broadcastTime << electionTimeout << MTBF"
statement: "Raft can elect and maintain a steady leader as long as the system satisfies the timing requirement broadcastTime << electionTimeout << MTBF."
domain: "distilled"
generativity: 5
confidence: 0.5
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

# Raft can elect and maintain a steady leader as long as the system satisfies the timing requirement broadcastTime << electionTimeout << MTBF

Raft can elect and maintain a steady leader as long as the system satisfies the timing requirement broadcastTime << electionTimeout << MTBF.

Evidence: [[https-raft-github-io-raft]].
