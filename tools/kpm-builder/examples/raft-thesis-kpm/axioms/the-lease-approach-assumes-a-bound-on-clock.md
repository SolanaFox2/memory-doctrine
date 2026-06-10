---
id: the-lease-approach-assumes-a-bound-on-clock
type: axiom
title: "The lease approach assumes a bound on clock drift across servers, and if that assumption is violated the system could return arbitrarily stale information"
statement: "The lease approach assumes a bound on clock drift across servers, and if that assumption is violated the system could return arbitrarily stale information."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: []
  generalizes: []
  contradicts: [raft-maintains-the-consistency-of-its-logs-without]
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# The lease approach assumes a bound on clock drift across servers, and if that assumption is violated the system could return arbitrarily stale information

The lease approach assumes a bound on clock drift across servers, and if that assumption is violated the system could return arbitrarily stale information.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[raft-maintains-the-consistency-of-its-logs-without]]
