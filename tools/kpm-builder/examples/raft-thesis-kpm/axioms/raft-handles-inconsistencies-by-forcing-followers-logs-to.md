---
id: raft-handles-inconsistencies-by-forcing-followers-logs-to
type: axiom
title: "Raft handles inconsistencies by forcing followers' logs to duplicate the leader's, so conflicting entries in follower logs are overwritten with entries from the leader's log"
statement: "Raft handles inconsistencies by forcing followers' logs to duplicate the leader's, so conflicting entries in follower logs are overwritten with entries from the leader's log."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: [raft-uses-a-stronger-form-of-leadership-than]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Raft handles inconsistencies by forcing followers' logs to duplicate the leader's, so conflicting entries in follower logs are overwritten with entries from the leader's log

Raft handles inconsistencies by forcing followers' logs to duplicate the leader's, so conflicting entries in follower logs are overwritten with entries from the leader's log.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[raft-uses-a-stronger-form-of-leadership-than]]
