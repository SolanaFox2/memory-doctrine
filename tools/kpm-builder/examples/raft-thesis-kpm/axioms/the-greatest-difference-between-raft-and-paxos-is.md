---
id: the-greatest-difference-between-raft-and-paxos-is
type: axiom
title: "The greatest difference between Raft and Paxos is Raft's strong leadership"
statement: "The greatest difference between Raft and Paxos is Raft's strong leadership: Raft uses leader election as an essential part of consensus, whereas in Paxos leader election is orthogonal to the basic protocol and serves only as a performance optimization."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [raft-uses-a-stronger-form-of-leadership-than]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# The greatest difference between Raft and Paxos is Raft's strong leadership

The greatest difference between Raft and Paxos is Raft's strong leadership: Raft uses leader election as an essential part of consensus, whereas in Paxos leader election is orthogonal to the basic protocol and serves only as a performance optimization.

Evidence: [[https-raft-github-io-raft]].
[[raft-uses-a-stronger-form-of-leadership-than]]
