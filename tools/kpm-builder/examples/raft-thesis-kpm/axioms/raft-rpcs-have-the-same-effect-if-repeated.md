---
id: raft-rpcs-have-the-same-effect-if-repeated
type: axiom
title: "Raft RPCs have the same effect if repeated, so a server that crashes after completing an RPC but before responding can safely receive the same RPC again on restart"
statement: "Raft RPCs have the same effect if repeated, so a server that crashes after completing an RPC but before responding can safely receive the same RPC again on restart."
domain: "distilled"
generativity: 3
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

# Raft RPCs have the same effect if repeated, so a server that crashes after completing an RPC but before responding can safely receive the same RPC again on restart

Raft RPCs have the same effect if repeated, so a server that crashes after completing an RPC but before responding can safely receive the same RPC again on restart.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
