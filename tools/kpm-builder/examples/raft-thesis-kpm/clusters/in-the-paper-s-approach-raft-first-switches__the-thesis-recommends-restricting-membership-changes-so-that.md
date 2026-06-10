---
axioms:
- in-the-paper-s-approach-raft-first-switches
- the-thesis-recommends-restricting-membership-changes-so-that
basis: []
confidence: unverified
resolved: '2026-06-05'
status: dispute
type: resolution
---

# Resolution: in-the-paper-s-approach-raft-first-switches ↔ the-thesis-recommends-restricting-membership-changes-so-that

[downgraded from reconciled — proposed truth over-claimed its passage] These are two valid, safe ways to change membership: joint consensus (paper) handles arbitrary changes via a transitional config; the single-server restriction (thesis) avoids disjoint majorities by allowing only one addition/removal at a time. The thesis recommends the simpler single-server approach but both are correct, so they reconcile rather than conflict. | proposed (unverified) reconciliation: Both the paper's joint-consensus mechanism and the thesis's recommended single-server-at-a-time restriction are safe membership-change methods, with the thesis preferring the single-server approach because it avoids disjoint majorities without a transitional joint configuration.

## Positions
- **in-the-paper-s-approach-raft-first-switches**: In the paper's approach, Raft first switches to a transitional joint-consensus configuration, and only after it is committed does the system transition to the new configuration.
- **the-thesis-recommends-restricting-membership-changes-so-that**: The thesis recommends restricting membership changes so that only one server can be added or removed from the cluster at a time.
