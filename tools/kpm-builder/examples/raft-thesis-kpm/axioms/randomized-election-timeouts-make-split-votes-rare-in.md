---
id: randomized-election-timeouts-make-split-votes-rare-in
type: axiom
title: "Randomized election timeouts make split votes rare"
statement: "Randomized election timeouts make split votes rare; in the absence of randomness leader election consistently took longer than 10 seconds due to many split votes."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [to-prevent-split-votes-election-timeouts-are-chosen]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Randomized election timeouts make split votes rare

Randomized election timeouts make split votes rare; in the absence of randomness leader election consistently took longer than 10 seconds due to many split votes.

Evidence: [[https-raft-github-io-raft]].
[[to-prevent-split-votes-election-timeouts-are-chosen]]
