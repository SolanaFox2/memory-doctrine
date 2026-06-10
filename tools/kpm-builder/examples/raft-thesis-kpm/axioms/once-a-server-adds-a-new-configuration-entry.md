---
id: once-a-server-adds-a-new-configuration-entry
type: axiom
title: "Once a server adds a new configuration entry to its log it uses that configuration for all future decisions, regardless of whether the entry is committed (a server always uses the latest configuration in its log)"
statement: "Once a server adds a new configuration entry to its log it uses that configuration for all future decisions, regardless of whether the entry is committed (a server always uses the latest configuration in its log)."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [a-log-entry-for-a-configuration-change-can]
  generalizes: []
  contradicts: [in-the-paper-s-approach-raft-first-switches]
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Once a server adds a new configuration entry to its log it uses that configuration for all future decisions, regardless of whether the entry is committed (a server always uses the latest configuration in its log)

Once a server adds a new configuration entry to its log it uses that configuration for all future decisions, regardless of whether the entry is committed (a server always uses the latest configuration in its log).

Evidence: [[https-raft-github-io-raft]].
[[a-log-entry-for-a-configuration-change-can]]
[[in-the-paper-s-approach-raft-first-switches]]
