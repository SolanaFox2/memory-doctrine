---
id: the-appendentries-rpc-results-are-term-currentterm-for
type: axiom
title: "The AppendEntries RPC results are term (currentTerm, for the leader to update itself) and success (true if the follower contained an entry matching prevLogIndex and prevLogTerm)"
statement: "The AppendEntries RPC results are term (currentTerm, for the leader to update itself) and success (true if the follower contained an entry matching prevLogIndex and prevLogTerm)."
domain: "distilled"
generativity: 3
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [appendentries-receiver-rule-reply-false-if-the-log]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# The AppendEntries RPC results are term (currentTerm, for the leader to update itself) and success (true if the follower contained an entry matching prevLogIndex and prevLogTerm)

The AppendEntries RPC results are term (currentTerm, for the leader to update itself) and success (true if the follower contained an entry matching prevLogIndex and prevLogTerm).

Evidence: [[https-raft-github-io-raft]].
[[appendentries-receiver-rule-reply-false-if-the-log]]
