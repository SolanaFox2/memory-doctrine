---
id: each-raft-server-takes-snapshots-independently-covering-just
type: axiom
title: "Each Raft server takes snapshots independently, covering just the committed entries in its log"
statement: "Each Raft server takes snapshots independently, covering just the committed entries in its log."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: [committed-entries-are-durable-and-will-eventually-be]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Each Raft server takes snapshots independently, covering just the committed entries in its log

Each Raft server takes snapshots independently, covering just the committed entries in its log.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[committed-entries-are-durable-and-will-eventually-be]]
