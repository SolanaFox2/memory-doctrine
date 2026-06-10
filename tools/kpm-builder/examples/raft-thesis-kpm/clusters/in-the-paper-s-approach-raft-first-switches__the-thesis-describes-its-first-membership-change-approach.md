---
axioms:
- in-the-paper-s-approach-raft-first-switches
- the-thesis-describes-its-first-membership-change-approach
basis: []
confidence: unverified
resolved: '2026-06-05'
status: dispute
type: resolution
---

# Resolution: in-the-paper-s-approach-raft-first-switches ↔ the-thesis-describes-its-first-membership-change-approach

[downgraded from reconciled — proposed truth over-claimed its passage] There is no factual conflict: joint consensus (A) is a valid, safe approach, and the thesis (B) simply states it was the first approach and now prefers the simpler single-server method. Both mechanisms are correct; the thesis recommends the simpler one. | proposed (unverified) reconciliation: Joint consensus is the paper's original (and safe) membership-change mechanism, which the thesis retains for completeness but supersedes with the simpler single-server-at-a-time approach it now recommends.

## Positions
- **in-the-paper-s-approach-raft-first-switches**: In the paper's approach, Raft first switches to a transitional joint-consensus configuration, and only after it is committed does the system transition to the new configuration.
- **the-thesis-describes-its-first-membership-change-approach**: The thesis describes its first membership-change approach only for completeness and recommends the simpler single-server approach instead, since handling arbitrary changes requires extra complexity.
