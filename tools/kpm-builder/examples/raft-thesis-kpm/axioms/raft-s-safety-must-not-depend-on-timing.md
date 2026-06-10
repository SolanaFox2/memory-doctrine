---
id: raft-s-safety-must-not-depend-on-timing
type: axiom
title: "Raft's safety must not depend on timing (the system must never produce incorrect results because an event is faster or slower than expected), whereas availability inevitably depends on timing"
statement: "Raft's safety must not depend on timing (the system must never produce incorrect results because an event is faster or slower than expected), whereas availability inevitably depends on timing."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Raft's safety must not depend on timing (the system must never produce incorrect results because an event is faster or slower than expected), whereas availability inevitably depends on timing

Raft's safety must not depend on timing (the system must never produce incorrect results because an event is faster or slower than expected), whereas availability inevitably depends on timing.

Evidence: [[https-raft-github-io-raft]].
