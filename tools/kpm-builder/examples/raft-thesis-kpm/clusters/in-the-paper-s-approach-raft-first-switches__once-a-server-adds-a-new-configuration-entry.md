---
axioms:
- in-the-paper-s-approach-raft-first-switches
- once-a-server-adds-a-new-configuration-entry
basis: []
confidence: unverified
resolved: '2026-06-05'
status: distinct
type: resolution
---

# Resolution: in-the-paper-s-approach-raft-first-switches ↔ once-a-server-adds-a-new-configuration-entry

Both are from the paper and both are true of joint consensus: A describes the cluster-level two-phase transition (switch to joint consensus, then transition to the new configuration only after joint consensus is committed); B describes the per-server rule that an individual server applies a configuration as soon as it appends the entry to its log, regardless of commit. One is about when the cluster transitions, the other about when an individual server adopts a config entry; they are complementary, not contradictory.

## Positions
- **in-the-paper-s-approach-raft-first-switches**: In the paper's approach, Raft first switches to a transitional joint-consensus configuration, and only after it is committed does the system transition to the new configuration.
- **once-a-server-adds-a-new-configuration-entry**: Once a server adds a new configuration entry to its log it uses that configuration for all future decisions, regardless of whether the entry is committed (a server always uses the latest configuration in its log).
