---
axioms:
- the-authors-recommend-a-conservative-election-timeout-such
- to-prevent-split-votes-election-timeouts-are-chosen
basis: []
confidence: unverified
resolved: '2026-06-05'
status: dispute
type: resolution
---

# Resolution: the-authors-recommend-a-conservative-election-timeout-such ↔ to-prevent-split-votes-election-timeouts-are-chosen

[downgraded from reconciled — proposed truth over-claimed its passage] Both refer to the identical 150-300 ms interval: the paper frames it as the recommended conservative timeout; the thesis frames the same interval as the range timeouts are randomized over to prevent split votes. Same value, two descriptions of its purpose. | proposed (unverified) reconciliation: The recommended conservative election-timeout range of 150-300 ms is the same fixed interval from which timeouts are randomly chosen to prevent split votes.

## Positions
- **the-authors-recommend-a-conservative-election-timeout-such**: The authors recommend a conservative election timeout such as 150 to 300 ms, which is unlikely to cause unnecessary leader changes while still providing good availability.
- **to-prevent-split-votes-election-timeouts-are-chosen**: To prevent split votes, election timeouts are chosen randomly from a fixed interval, for example 150–300 ms.
