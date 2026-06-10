---
id: a-new-leader-in-raft-transfers-just-the
type: axiom
title: "A new leader in Raft transfers just the minimal number of entries needed to make other servers' logs match its own, and entries are never renumbered, so the same entry keeps the same index and term across logs for all time"
statement: "A new leader in Raft transfers just the minimal number of entries needed to make other servers' logs match its own, and entries are never renumbered, so the same entry keeps the same index and term across logs for all time."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [log-matching-if-two-logs-contain-an-entry]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# A new leader in Raft transfers just the minimal number of entries needed to make other servers' logs match its own, and entries are never renumbered, so the same entry keeps the same index and term across logs for all time

A new leader in Raft transfers just the minimal number of entries needed to make other servers' logs match its own, and entries are never renumbered, so the same entry keeps the same index and term across logs for all time.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[log-matching-if-two-logs-contain-an-entry]]
