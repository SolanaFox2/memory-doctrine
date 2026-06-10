---
id: to-handle-duplicate-requests-clients-assign-unique-serial
type: axiom
title: "To handle duplicate requests, clients assign unique serial numbers to every command and the state machine tracks the latest serial number processed per client, responding immediately to an already-executed serial number without re-executing"
statement: "To handle duplicate requests, clients assign unique serial numbers to every command and the state machine tracks the latest serial number processed per client, responding immediately to an already-executed serial number without re-executing."
domain: "distilled"
generativity: 4
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [under-linearizability-each-operation-appears-to-execute-instantaneously]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# To handle duplicate requests, clients assign unique serial numbers to every command and the state machine tracks the latest serial number processed per client, responding immediately to an already-executed serial number without re-executing

To handle duplicate requests, clients assign unique serial numbers to every command and the state machine tracks the latest serial number processed per client, responding immediately to an already-executed serial number without re-executing.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[under-linearizability-each-operation-appears-to-execute-instantaneously]]
