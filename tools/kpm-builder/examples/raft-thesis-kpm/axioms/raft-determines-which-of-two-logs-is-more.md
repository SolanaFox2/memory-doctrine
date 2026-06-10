---
id: raft-determines-which-of-two-logs-is-more
type: axiom
title: "Raft determines which of two logs is more up-to-date by comparing the index and term of the last entries"
statement: "Raft determines which of two logs is more up-to-date by comparing the index and term of the last entries: the log with the later last-entry term is more up-to-date, and if the terms are equal the longer log is more up-to-date."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [the-election-restriction-prevents-a-candidate-from-winning]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Raft determines which of two logs is more up-to-date by comparing the index and term of the last entries

Raft determines which of two logs is more up-to-date by comparing the index and term of the last entries: the log with the later last-entry term is more up-to-date, and if the terms are equal the longer log is more up-to-date.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[the-election-restriction-prevents-a-candidate-from-winning]]
