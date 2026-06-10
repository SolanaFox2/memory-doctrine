---
id: followers-can-serve-reads-safely-by-requesting-a
type: axiom
title: "Followers can serve reads safely by requesting a current readIndex from the leader (which executes the leadership-confirmation steps) and then applying the wait-and-query steps on their own state machine"
statement: "Followers can serve reads safely by requesting a current readIndex from the leader (which executes the leadership-confirmation steps) and then applying the wait-and-query steps on their own state machine."
domain: "distilled"
generativity: 3
confidence: 0.5
status: candidate
relations:
  derives-from: [in-the-read-index-procedure-the-leader-saves]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Followers can serve reads safely by requesting a current readIndex from the leader (which executes the leadership-confirmation steps) and then applying the wait-and-query steps on their own state machine

Followers can serve reads safely by requesting a current readIndex from the leader (which executes the leadership-confirmation steps) and then applying the wait-and-query steps on their own state machine.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[in-the-read-index-procedure-the-leader-saves]]
