---
id: each-server-persists-new-log-entries-before-they
type: axiom
title: "Each server persists new log entries before they are counted toward commitment, which prevents committed entries from being lost or uncommitted when servers restart"
statement: "Each server persists new log entries before they are counted toward commitment, which prevents committed entries from being lost or uncommitted when servers restart."
domain: "distilled"
generativity: 5
confidence: 0.5
status: candidate
relations:
  derives-from: [raft-s-persistent-state-on-every-server-is]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Each server persists new log entries before they are counted toward commitment, which prevents committed entries from being lost or uncommitted when servers restart

Each server persists new log entries before they are counted toward commitment, which prevents committed entries from being lost or uncommitted when servers restart.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[raft-s-persistent-state-on-every-server-is]]
