---
id: the-requestvote-receiver-grants-its-vote-only-if
type: axiom
title: "The RequestVote receiver grants its vote only if votedFor is null or equals candidateId and the candidate's log is at least as up-to-date as the receiver's log, and replies false if term < currentTerm"
statement: "The RequestVote receiver grants its vote only if votedFor is null or equals candidateId and the candidate's log is at least as up-to-date as the receiver's log, and replies false if term < currentTerm."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [raft-determines-which-of-two-logs-is-more, the-election-restriction-prevents-a-candidate-from-winning]
  supports: [each-server-will-vote-for-at-most-one, the-requestvote-rpc-arguments-are-term-candidate-s]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# The RequestVote receiver grants its vote only if votedFor is null or equals candidateId and the candidate's log is at least as up-to-date as the receiver's log, and replies false if term < currentTerm

The RequestVote receiver grants its vote only if votedFor is null or equals candidateId and the candidate's log is at least as up-to-date as the receiver's log, and replies false if term < currentTerm.

Evidence: [[https-raft-github-io-raft]].
[[each-server-will-vote-for-at-most-one]]
[[raft-determines-which-of-two-logs-is-more]]
[[the-election-restriction-prevents-a-candidate-from-winning]]
[[the-requestvote-rpc-arguments-are-term-candidate-s]]
