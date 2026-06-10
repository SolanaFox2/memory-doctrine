---
id: https-raw-githubusercontent-com-ongardie-raft-tla-master-raft
type: evidence
ref: "https://raw.githubusercontent.com/ongardie/raft.tla/master/raft.tla"
url: "https://raw.githubusercontent.com/ongardie/raft.tla/master/raft.tla"
verified: 2026-06-05
supports: [in-the-raft-tla-specification-a-restart-leaves, raft-has-a-formal-specification-for-the-consensus, the-tla-specification-encodes-quorum-overlap-directly-a, in-the-tla-specification-the-leader-s-advancecommitindex]
---

# Evidence: https://raw.githubusercontent.com/ongardie/raft.tla/master/raft.tla

> "This is the formal specification for the Raft consensus algorithm. ... The set of all quorums [...] the only important property is that every quorum overlaps with every other."

*Paraphrase:* The TLA+ module (Copyright 2014 Diego Ongaro) encodes quorum overlap as `Quorum == {i \in SUBSET(Server) : Cardinality(i) * 2 > Cardinality(Server)}`, defines `Restart(i)` resetting `commitIndex` to 0 while leaving the durable state unchanged, and computes `newCommitIndex` only over agree-indexes whose entry term equals the leader's current term — cited by the axioms in `supports`. Full spec at the source URL above.
