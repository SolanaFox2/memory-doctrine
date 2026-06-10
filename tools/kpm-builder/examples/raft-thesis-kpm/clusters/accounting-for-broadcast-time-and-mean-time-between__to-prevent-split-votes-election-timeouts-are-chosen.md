---
axioms:
- accounting-for-broadcast-time-and-mean-time-between
- to-prevent-split-votes-election-timeouts-are-chosen
basis: []
confidence: partial
resolved: '2026-06-05'
status: reconciled
truth: Choosing election timeouts randomly from the example 150-300 ms interval to
  prevent split votes is consistent with the broader 10-500 ms range that the election
  timeout is likely to fall within.
truth_passage_id: https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd
type: resolution
---

# Resolution: accounting-for-broadcast-time-and-mean-time-between ↔ to-prevent-split-votes-election-timeouts-are-chosen

Both come from the thesis: A is the wide likely range derived from constraints; B is a concrete example interval (150-300 ms) from which timeouts are randomized to avoid split votes. The example interval sits inside the likely range, so they are compatible.
