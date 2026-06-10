---
axioms:
- adding-5-ms-of-randomness-to-the-election
- to-prevent-split-votes-election-timeouts-are-chosen
basis: []
confidence: unverified
resolved: '2026-06-05'
status: distinct
type: resolution
---

# Resolution: adding-5-ms-of-randomness-to-the-election ↔ to-prevent-split-votes-election-timeouts-are-chosen

A is the paper's measured effect of adding randomness (5/50 ms) on downtime/election completion; B is the thesis's example interval (150-300 ms) from which timeouts are randomly drawn to prevent split votes. The numbers measure different things (randomness magnitude/resulting downtime vs the base interval width), so there is no real conflict.

## Positions
- **adding-5-ms-of-randomness-to-the-election**: Adding 5 ms of randomness to the election timeout produced a median downtime of 287 ms, and with 50 ms of randomness the worst-case election completion time over 1,000 trials was 513 ms.
- **to-prevent-split-votes-election-timeouts-are-chosen**: To prevent split votes, election timeouts are chosen randomly from a fixed interval, for example 150–300 ms.
