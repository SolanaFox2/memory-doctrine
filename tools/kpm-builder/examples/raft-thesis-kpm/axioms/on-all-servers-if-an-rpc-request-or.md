---
id: on-all-servers-if-an-rpc-request-or
type: axiom
title: "On all servers, if an RPC request or response contains a term T greater than currentTerm, the server sets currentTerm to T and converts to follower"
statement: "On all servers, if an RPC request or response contains a term T greater than currentTerm, the server sets currentTerm to T and converts to follower."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: [current-terms-are-exchanged-whenever-servers-communicate-if]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# On all servers, if an RPC request or response contains a term T greater than currentTerm, the server sets currentTerm to T and converts to follower

On all servers, if an RPC request or response contains a term T greater than currentTerm, the server sets currentTerm to T and converts to follower.

Evidence: [[https-raft-github-io-raft]].
[[current-terms-are-exchanged-whenever-servers-communicate-if]]
