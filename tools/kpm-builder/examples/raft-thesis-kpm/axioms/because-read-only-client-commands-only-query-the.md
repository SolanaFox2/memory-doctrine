---
id: because-read-only-client-commands-only-query-the
type: axiom
title: "Because read-only client commands only query the replicated state machine and do not change it, it is natural to ask whether they can bypass the Raft log, which would offer a performance advantage since the synchronous disk writes needed to append entries are time-consuming"
statement: "Because read-only client commands only query the replicated state machine and do not change it, it is natural to ask whether they can bypass the Raft log, which would offer a performance advantage since the synchronous disk writes needed to append entries are time-consuming."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Because read-only client commands only query the replicated state machine and do not change it, it is natural to ask whether they can bypass the Raft log, which would offer a performance advantage since the synchronous disk writes needed to append entries are time-consuming

Because read-only client commands only query the replicated state machine and do not change it, it is natural to ask whether they can bypass the Raft log, which would offer a performance advantage since the synchronous disk writes needed to append entries are time-consuming.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
