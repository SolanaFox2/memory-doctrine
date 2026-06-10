---
axioms:
- adding-5-ms-of-randomness-to-the-election
- the-authors-recommend-a-conservative-election-timeout-such
basis: []
confidence: unverified
resolved: '2026-06-05'
status: distinct
type: resolution
---

# Resolution: adding-5-ms-of-randomness-to-the-election ↔ the-authors-recommend-a-conservative-election-timeout-such

A reports experimental downtime results for different amounts of *randomness added to* the election timeout (5 ms -> 287 ms median; 50 ms -> 513 ms worst case); B is the recommended *base* election-timeout range (150-300 ms). One is about randomness magnitude and measured downtime; the other is the recommended timeout setting. Different quantities, no conflict.

## Positions
- **adding-5-ms-of-randomness-to-the-election**: Adding 5 ms of randomness to the election timeout produced a median downtime of 287 ms, and with 50 ms of randomness the worst-case election completion time over 1,000 trials was 513 ms.
- **the-authors-recommend-a-conservative-election-timeout-such**: The authors recommend a conservative election timeout such as 150 to 300 ms, which is unlikely to cause unnecessary leader changes while still providing good availability.
