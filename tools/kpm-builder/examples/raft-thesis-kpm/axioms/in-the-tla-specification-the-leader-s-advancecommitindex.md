---
id: in-the-tla-specification-the-leader-s-advancecommitindex
type: axiom
title: "In the TLA+ specification, the leader's AdvanceCommitIndex only advances the commit index to the maximum quorum-agreed index when that entry's term equals the leader's current term, matching the paper's log[N]"
statement: "In the TLA+ specification, the leader's AdvanceCommitIndex only advances the commit index to the maximum quorum-agreed index when that entry's term equals the leader's current term, matching the paper's log[N].term == currentTerm restriction."
domain: "distilled"
generativity: 3
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [the-leader-advances-its-commit-index-by-the]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raw-githubusercontent-com-ongardie-raft-tla-master-raft]
provenance: "package-research/distilled"
---

# In the TLA+ specification, the leader's AdvanceCommitIndex only advances the commit index to the maximum quorum-agreed index when that entry's term equals the leader's current term, matching the paper's log[N]

In the TLA+ specification, the leader's AdvanceCommitIndex only advances the commit index to the maximum quorum-agreed index when that entry's term equals the leader's current term, matching the paper's log[N].term == currentTerm restriction.

Evidence: [[https-raw-githubusercontent-com-ongardie-raft-tla-master-raft]].
[[the-leader-advances-its-commit-index-by-the]]
