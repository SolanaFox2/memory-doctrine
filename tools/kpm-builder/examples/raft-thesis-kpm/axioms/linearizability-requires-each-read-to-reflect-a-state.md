---
id: linearizability-requires-each-read-to-reflect-a-state
type: axiom
title: "Linearizability requires each read to reflect a state of the system after the read was initiated and to at least return the latest committed write"
statement: "Linearizability requires each read to reflect a state of the system after the read was initiated and to at least return the latest committed write; a system allowing stale reads would only provide the weaker guarantee of serializability."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [under-linearizability-each-operation-appears-to-execute-instantaneously]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Linearizability requires each read to reflect a state of the system after the read was initiated and to at least return the latest committed write

Linearizability requires each read to reflect a state of the system after the read was initiated and to at least return the latest committed write; a system allowing stale reads would only provide the weaker guarantee of serializability.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[under-linearizability-each-operation-appears-to-execute-instantaneously]]
