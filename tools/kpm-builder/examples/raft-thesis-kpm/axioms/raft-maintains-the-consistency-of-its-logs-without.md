---
id: raft-maintains-the-consistency-of-its-logs-without
type: axiom
title: "Raft maintains the consistency of its logs without depending on timing, preserving safety under an asynchronous model in which faulty clocks and extreme message delays can at worst cause availability problems"
statement: "Raft maintains the consistency of its logs without depending on timing, preserving safety under an asynchronous model in which faulty clocks and extreme message delays can at worst cause availability problems."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [raft-s-safety-must-not-depend-on-timing]
  generalizes: []
  contradicts: [the-lease-approach-assumes-a-bound-on-clock]
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Raft maintains the consistency of its logs without depending on timing, preserving safety under an asynchronous model in which faulty clocks and extreme message delays can at worst cause availability problems

Raft maintains the consistency of its logs without depending on timing, preserving safety under an asynchronous model in which faulty clocks and extreme message delays can at worst cause availability problems.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[raft-s-safety-must-not-depend-on-timing]]
[[the-lease-approach-assumes-a-bound-on-clock]]
