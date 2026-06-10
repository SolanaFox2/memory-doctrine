---
id: in-raft-the-log-comparison-check-during-voting
type: axiom
title: "In Raft the log comparison check during voting ensures a new leader already has all committed entries, so no log entries need to be transferred to the new leader"
statement: "In Raft the log comparison check during voting ensures a new leader already has all committed entries, so no log entries need to be transferred to the new leader."
domain: "distilled"
generativity: 5
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [the-election-restriction-prevents-a-candidate-from-winning]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# In Raft the log comparison check during voting ensures a new leader already has all committed entries, so no log entries need to be transferred to the new leader

In Raft the log comparison check during voting ensures a new leader already has all committed entries, so no log entries need to be transferred to the new leader.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[the-election-restriction-prevents-a-candidate-from-winning]]
