---
id: the-appendentries-rpc-arguments-are-term-leaderid-prevlogindex
type: axiom
title: "The AppendEntries RPC arguments are term, leaderId, prevLogIndex, prevLogTerm, entries[] (empty for heartbeat), and leaderCommit (the leader's commitIndex)"
statement: "The AppendEntries RPC arguments are term, leaderId, prevLogIndex, prevLogTerm, entries[] (empty for heartbeat), and leaderCommit (the leader's commitIndex)."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [when-sending-an-appendentries-rpc-the-leader-includes]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# The AppendEntries RPC arguments are term, leaderId, prevLogIndex, prevLogTerm, entries[] (empty for heartbeat), and leaderCommit (the leader's commitIndex)

The AppendEntries RPC arguments are term, leaderId, prevLogIndex, prevLogTerm, entries[] (empty for heartbeat), and leaderCommit (the leader's commitIndex).

Evidence: [[https-raft-github-io-raft]].
[[when-sending-an-appendentries-rpc-the-leader-includes]]
