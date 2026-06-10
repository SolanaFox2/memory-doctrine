---
id: the-disruptive-server-problem-a-server-not-in
type: axiom
title: "The disruptive-server problem"
statement: "The disruptive-server problem: a server not in the new configuration stops receiving heartbeats, times out, and sends RequestVote RPCs with higher term numbers that force the current leader to revert to follower state, repeating and causing poor availability."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# The disruptive-server problem

The disruptive-server problem: a server not in the new configuration stops receiving heartbeats, times out, and sends RequestVote RPCs with higher term numbers that force the current leader to revert to follower state, repeating and causing poor availability.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
