---
id: upon-receiving-a-client-command-the-leader-appends
type: axiom
title: "Upon receiving a client command, the leader appends it to its log as a new entry, then issues AppendEntries RPCs in parallel to the other servers to replicate the entry"
statement: "Upon receiving a client command, the leader appends it to its log as a new entry, then issues AppendEntries RPCs in parallel to the other servers to replicate the entry."
domain: "distilled"
generativity: 5
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

# Upon receiving a client command, the leader appends it to its log as a new entry, then issues AppendEntries RPCs in parallel to the other servers to replicate the entry

Upon receiving a client command, the leader appends it to its log as a new entry, then issues AppendEntries RPCs in parallel to the other servers to replicate the entry.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[raft-uses-a-stronger-form-of-leadership-than]]
