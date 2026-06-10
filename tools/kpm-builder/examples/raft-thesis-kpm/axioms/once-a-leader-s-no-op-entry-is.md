---
id: once-a-leader-s-no-op-entry-is
type: axiom
title: "Once a leader's no-op entry is committed, the leader's commit index is at least as large as any other server's during its term"
statement: "Once a leader's no-op entry is committed, the leader's commit index is at least as large as any other server's during its term."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [each-leader-commits-a-blank-no-op-entry]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Once a leader's no-op entry is committed, the leader's commit index is at least as large as any other server's during its term

Once a leader's no-op entry is committed, the leader's commit index is at least as large as any other server's during its term.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[each-leader-commits-a-blank-no-op-entry]]
