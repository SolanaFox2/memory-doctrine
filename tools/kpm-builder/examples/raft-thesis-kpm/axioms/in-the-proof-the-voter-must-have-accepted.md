---
id: in-the-proof-the-voter-must-have-accepted
type: axiom
title: "In the proof, the voter must have accepted the committed entry from leaderT before voting for leaderU, otherwise it would have rejected leaderT's AppendEntries because its current term would have been higher than T"
statement: "In the proof, the voter must have accepted the committed entry from leaderT before voting for leaderU, otherwise it would have rejected leaderT's AppendEntries because its current term would have been higher than T."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: [current-terms-are-exchanged-whenever-servers-communicate-if]
  supports: [the-contradiction-hinges-on-majority-overlap-because-leadert]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# In the proof, the voter must have accepted the committed entry from leaderT before voting for leaderU, otherwise it would have rejected leaderT's AppendEntries because its current term would have been higher than T

In the proof, the voter must have accepted the committed entry from leaderT before voting for leaderU, otherwise it would have rejected leaderT's AppendEntries because its current term would have been higher than T.

Evidence: [[https-raft-github-io-raft]].
[[current-terms-are-exchanged-whenever-servers-communicate-if]]
[[the-contradiction-hinges-on-majority-overlap-because-leadert]]
