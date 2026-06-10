---
axioms:
- raft-maintains-the-consistency-of-its-logs-without
- the-lease-approach-assumes-a-bound-on-clock
basis: []
confidence: unverified
resolved: '2026-06-05'
status: dispute
type: resolution
---

# Resolution: raft-maintains-the-consistency-of-its-logs-without ↔ the-lease-approach-assumes-a-bound-on-clock

[downgraded from reconciled — proposed truth over-claimed its passage] No conflict: A is about Raft's core consensus, which maintains safety under an asynchronous model regardless of clocks; B is about the lease optimization, an opt-in alternative for read-only queries that trades the timing-independence of the core for performance. The lease's clock-drift assumption is a property of that optional optimization, not of Raft's core. | proposed (unverified) reconciliation: Raft's core log-consistency safety does not depend on timing, whereas the optional lease approach for read-only requests is an explicitly weaker mechanism that does assume a bound on clock drift and can return stale data if that assumption is violated.

## Positions
- **raft-maintains-the-consistency-of-its-logs-without**: Raft maintains the consistency of its logs without depending on timing, preserving safety under an asynchronous model in which faulty clocks and extreme message delays can at worst cause availability problems.
- **the-lease-approach-assumes-a-bound-on-clock**: The lease approach assumes a bound on clock drift across servers, and if that assumption is violated the system could return arbitrarily stale information.
