---
id: under-checkquorum-a-leader-in-raft-steps-down
type: axiom
title: "Under CheckQuorum, a leader in Raft steps down if an election timeout elapses without a successful round of heartbeats to a majority of its cluster, so that clients can retry their requests with another server"
statement: "Under CheckQuorum, a leader in Raft steps down if an election timeout elapses without a successful round of heartbeats to a majority of its cluster, so that clients can retry their requests with another server."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [before-answering-a-read-only-request-the-leader]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Under CheckQuorum, a leader in Raft steps down if an election timeout elapses without a successful round of heartbeats to a majority of its cluster, so that clients can retry their requests with another server

Under CheckQuorum, a leader in Raft steps down if an election timeout elapses without a successful round of heartbeats to a majority of its cluster, so that clients can retry their requests with another server.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[before-answering-a-read-only-request-the-leader]]
