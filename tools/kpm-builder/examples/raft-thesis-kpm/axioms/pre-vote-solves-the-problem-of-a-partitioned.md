---
id: pre-vote-solves-the-problem-of-a-partitioned
type: axiom
title: "Pre-Vote solves the problem of a partitioned server disrupting the cluster when it rejoins, because while partitioned it cannot increment its term and after rejoining the other servers are still receiving heartbeats from the leader"
statement: "Pre-Vote solves the problem of a partitioned server disrupting the cluster when it rejoins, because while partitioned it cannot increment its term and after rejoining the other servers are still receiving heartbeats from the leader."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [in-the-pre-vote-algorithm-a-candidate-only]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Pre-Vote solves the problem of a partitioned server disrupting the cluster when it rejoins, because while partitioned it cannot increment its term and after rejoining the other servers are still receiving heartbeats from the leader

Pre-Vote solves the problem of a partitioned server disrupting the cluster when it rejoins, because while partitioned it cannot increment its term and after rejoining the other servers are still receiving heartbeats from the leader.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[in-the-pre-vote-algorithm-a-candidate-only]]
