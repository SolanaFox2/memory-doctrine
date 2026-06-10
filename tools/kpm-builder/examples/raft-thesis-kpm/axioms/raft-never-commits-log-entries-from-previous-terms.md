---
id: raft-never-commits-log-entries-from-previous-terms
type: axiom
title: "Raft never commits log entries from previous terms by counting replicas"
statement: "Raft never commits log entries from previous terms by counting replicas; only entries from the leader's current term are committed by counting replicas, after which all prior entries are committed indirectly via the Log Matching Property."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [committing-an-entry-also-commits-all-preceding-entries]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Raft never commits log entries from previous terms by counting replicas

Raft never commits log entries from previous terms by counting replicas; only entries from the leader's current term are committed by counting replicas, after which all prior entries are committed indirectly via the Log Matching Property.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[committing-an-entry-also-commits-all-preceding-entries]]
