---
id: to-begin-an-election-a-follower-increments-its
type: axiom
title: "To begin an election a follower increments its current term, transitions to candidate state, votes for itself, and issues RequestVote RPCs in parallel to the other servers"
statement: "To begin an election a follower increments its current term, transitions to candidate state, votes for itself, and issues RequestVote RPCs in parallel to the other servers."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: [if-a-follower-receives-no-communication-over-a]
  supports: [each-term-begins-with-an-election-in-which]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# To begin an election a follower increments its current term, transitions to candidate state, votes for itself, and issues RequestVote RPCs in parallel to the other servers

To begin an election a follower increments its current term, transitions to candidate state, votes for itself, and issues RequestVote RPCs in parallel to the other servers.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[each-term-begins-with-an-election-in-which]]
[[if-a-follower-receives-no-communication-over-a]]
