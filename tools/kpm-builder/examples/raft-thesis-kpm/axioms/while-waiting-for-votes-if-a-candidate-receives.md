---
id: while-waiting-for-votes-if-a-candidate-receives
type: axiom
title: "While waiting for votes, if a candidate receives an AppendEntries RPC from a server whose term is at least as large as its own, it recognizes the leader as legitimate and returns to follower state"
statement: "While waiting for votes, if a candidate receives an AppendEntries RPC from a server whose term is at least as large as its own, it recognizes the leader as legitimate and returns to follower state."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: [at-any-given-time-each-raft-server-is]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# While waiting for votes, if a candidate receives an AppendEntries RPC from a server whose term is at least as large as its own, it recognizes the leader as legitimate and returns to follower state

While waiting for votes, if a candidate receives an AppendEntries RPC from a server whose term is at least as large as its own, it recognizes the leader as legitimate and returns to follower state.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[at-any-given-time-each-raft-server-is]]
