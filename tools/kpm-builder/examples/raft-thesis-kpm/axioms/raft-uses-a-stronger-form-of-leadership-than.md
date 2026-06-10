---
id: raft-uses-a-stronger-form-of-leadership-than
type: axiom
title: "Raft uses a stronger form of leadership than other consensus algorithms"
statement: "Raft uses a stronger form of leadership than other consensus algorithms: log entries flow only from the leader to other servers."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: [paxos-uses-a-symmetric-peer-to-peer-approach]
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Raft uses a stronger form of leadership than other consensus algorithms

Raft uses a stronger form of leadership than other consensus algorithms: log entries flow only from the leader to other servers.

Evidence: [[https-raft-github-io-raft]].
[[paxos-uses-a-symmetric-peer-to-peer-approach]]
