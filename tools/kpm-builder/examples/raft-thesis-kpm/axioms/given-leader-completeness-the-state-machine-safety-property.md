---
id: given-leader-completeness-the-state-machine-safety-property
type: axiom
title: "Given Leader Completeness, the State Machine Safety property follows"
statement: "Given Leader Completeness, the State Machine Safety property follows: at the lowest term in which any server applies a given log index, Leader Completeness guarantees leaders of all higher terms store that same entry, so servers applying that index later apply the same value."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: [leader-completeness-if-a-log-entry-is-committed]
  supports: [state-machine-safety-if-a-server-has-applied]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Given Leader Completeness, the State Machine Safety property follows

Given Leader Completeness, the State Machine Safety property follows: at the lowest term in which any server applies a given log index, Leader Completeness guarantees leaders of all higher terms store that same entry, so servers applying that index later apply the same value.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[leader-completeness-if-a-log-entry-is-committed]]
[[state-machine-safety-if-a-server-has-applied]]
