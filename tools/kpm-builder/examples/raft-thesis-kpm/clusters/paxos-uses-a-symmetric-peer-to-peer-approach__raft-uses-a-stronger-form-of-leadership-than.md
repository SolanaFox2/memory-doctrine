---
axioms:
- paxos-uses-a-symmetric-peer-to-peer-approach
- raft-uses-a-stronger-form-of-leadership-than
basis: []
confidence: unverified
resolved: '2026-06-05'
status: distinct
type: resolution
---

# Resolution: paxos-uses-a-symmetric-peer-to-peer-approach ↔ raft-uses-a-stronger-form-of-leadership-than

A characterizes Paxos (symmetric peer-to-peer with an optional weak leader); B characterizes Raft (strong leader, log entries flow only from leader to followers). They describe two different algorithms, so there is no conflict; the contrast is the point.

## Positions
- **paxos-uses-a-symmetric-peer-to-peer-approach**: Paxos uses a symmetric peer-to-peer approach at its core, though it also suggests a weak form of leadership as a performance optimization.
- **raft-uses-a-stronger-form-of-leadership-than**: Raft uses a stronger form of leadership than other consensus algorithms: log entries flow only from the leader to other servers.
