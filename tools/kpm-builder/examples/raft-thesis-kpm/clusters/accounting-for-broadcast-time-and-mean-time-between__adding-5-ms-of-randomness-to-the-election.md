---
axioms:
- accounting-for-broadcast-time-and-mean-time-between
- adding-5-ms-of-randomness-to-the-election
basis: []
confidence: unverified
resolved: '2026-06-05'
status: distinct
type: resolution
---

# Resolution: accounting-for-broadcast-time-and-mean-time-between ↔ adding-5-ms-of-randomness-to-the-election

A is the thesis's derived *likely range* of the election-timeout setting (10-500 ms, from broadcast-time/MTBF bounds); B is the paper's experimental result on how much *randomness added on top of* an election timeout reduces downtime (287 ms median at 5 ms randomness, 513 ms worst case at 50 ms). They describe different quantities (a parameter range vs measured downtimes), so there is no conflict.

## Positions
- **accounting-for-broadcast-time-and-mean-time-between**: Accounting for broadcast time and mean-time-between-failures constraints, the election timeout is likely to be somewhere between 10–500 ms.
- **adding-5-ms-of-randomness-to-the-election**: Adding 5 ms of randomness to the election timeout produced a median downtime of 287 ms, and with 50 ms of randomness the worst-case election completion time over 1,000 trials was 513 ms.
