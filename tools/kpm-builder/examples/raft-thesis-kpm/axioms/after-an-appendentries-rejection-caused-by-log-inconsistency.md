---
id: after-an-appendentries-rejection-caused-by-log-inconsistency
type: axiom
title: "After an AppendEntries rejection caused by log inconsistency, the leader decrements nextIndex and retries until nextIndex reaches a point where the leader and follower logs match"
statement: "After an AppendEntries rejection caused by log inconsistency, the leader decrements nextIndex and retries until nextIndex reaches a point where the leader and follower logs match."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: [appendentries-receiver-rule-reply-false-if-the-log]
  supports: [raft-handles-inconsistencies-by-forcing-followers-logs-to]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# After an AppendEntries rejection caused by log inconsistency, the leader decrements nextIndex and retries until nextIndex reaches a point where the leader and follower logs match

After an AppendEntries rejection caused by log inconsistency, the leader decrements nextIndex and retries until nextIndex reaches a point where the leader and follower logs match.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[appendentries-receiver-rule-reply-false-if-the-log]]
[[raft-handles-inconsistencies-by-forcing-followers-logs-to]]
