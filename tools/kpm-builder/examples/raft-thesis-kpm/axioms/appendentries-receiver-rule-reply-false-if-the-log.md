---
id: appendentries-receiver-rule-reply-false-if-the-log
type: axiom
title: "AppendEntries receiver rule"
statement: "AppendEntries receiver rule: reply false if the log does not contain an entry at prevLogIndex whose term matches prevLogTerm."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [when-sending-an-appendentries-rpc-the-leader-includes]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# AppendEntries receiver rule

AppendEntries receiver rule: reply false if the log does not contain an entry at prevLogIndex whose term matches prevLogTerm.

Evidence: [[https-raft-github-io-raft]].
[[when-sending-an-appendentries-rpc-the-leader-includes]]
