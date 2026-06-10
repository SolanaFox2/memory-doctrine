---
id: when-sending-an-appendentries-rpc-the-leader-includes
type: axiom
title: "When sending an AppendEntries RPC the leader includes the index and term of the entry immediately preceding the new entries"
statement: "When sending an AppendEntries RPC the leader includes the index and term of the entry immediately preceding the new entries; if the follower does not find a matching entry it refuses the new entries."
domain: "distilled"
generativity: 5
confidence: 0.9
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

# When sending an AppendEntries RPC the leader includes the index and term of the entry immediately preceding the new entries

When sending an AppendEntries RPC the leader includes the index and term of the entry immediately preceding the new entries; if the follower does not find a matching entry it refuses the new entries.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[log-matching-if-two-logs-contain-an-entry]]
