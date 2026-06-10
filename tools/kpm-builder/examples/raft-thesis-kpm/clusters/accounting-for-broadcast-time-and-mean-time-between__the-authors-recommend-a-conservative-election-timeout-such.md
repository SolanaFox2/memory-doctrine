---
axioms:
- accounting-for-broadcast-time-and-mean-time-between
- the-authors-recommend-a-conservative-election-timeout-such
basis: []
confidence: partial
resolved: '2026-06-05'
status: reconciled
truth: Raft's recommended conservative election timeout of 150-300 ms falls within
  the broadly feasible 10-500 ms range that broadcast-time and MTBF constraints imply.
truth_passage_id: https-raft-github-io-raft
type: resolution
---

# Resolution: accounting-for-broadcast-time-and-mean-time-between ↔ the-authors-recommend-a-conservative-election-timeout-such

A states the full feasible/likely range the parameter could take (10-500 ms); B is the specific conservative value the authors recommend within that envelope. 150-300 ms is a subset of 10-500 ms, so they agree.
