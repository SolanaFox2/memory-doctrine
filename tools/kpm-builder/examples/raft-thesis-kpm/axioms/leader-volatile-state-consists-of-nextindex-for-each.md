---
id: leader-volatile-state-consists-of-nextindex-for-each
type: axiom
title: "Leader volatile state consists of nextIndex[] (for each server, the index of the next log entry to send, initialized to the leader's last log index + 1) and matchIndex[] (initialized to 0), reinitialized after every election"
statement: "Leader volatile state consists of nextIndex[] (for each server, the index of the next log entry to send, initialized to the leader's last log index + 1) and matchIndex[] (initialized to 0), reinitialized after every election."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [after-an-appendentries-rejection-caused-by-log-inconsistency]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Leader volatile state consists of nextIndex[] (for each server, the index of the next log entry to send, initialized to the leader's last log index + 1) and matchIndex[] (initialized to 0), reinitialized after every election

Leader volatile state consists of nextIndex[] (for each server, the index of the next log entry to send, initialized to the leader's last log index + 1) and matchIndex[] (initialized to 0), reinitialized after every election.

Evidence: [[https-raft-github-io-raft]].
[[after-an-appendentries-rejection-caused-by-log-inconsistency]]
