---
id: snapshots-include-the-lastincludedindex-and-lastincludedterm-to-support
type: axiom
title: "Snapshots include the lastIncludedIndex and lastIncludedTerm to support the AppendEntries consistency check for the first entry following the snapshot, and also include the latest configuration as of the last included index to enable membership changes"
statement: "Snapshots include the lastIncludedIndex and lastIncludedTerm to support the AppendEntries consistency check for the first entry following the snapshot, and also include the latest configuration as of the last included index to enable membership changes."
domain: "distilled"
generativity: 3
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [a-snapshot-s-metadata-includes-the-last-included]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Snapshots include the lastIncludedIndex and lastIncludedTerm to support the AppendEntries consistency check for the first entry following the snapshot, and also include the latest configuration as of the last included index to enable membership changes

Snapshots include the lastIncludedIndex and lastIncludedTerm to support the AppendEntries consistency check for the first entry following the snapshot, and also include the latest configuration as of the last included index to enable membership changes.

Evidence: [[https-raft-github-io-raft]].
[[a-snapshot-s-metadata-includes-the-last-included]]
