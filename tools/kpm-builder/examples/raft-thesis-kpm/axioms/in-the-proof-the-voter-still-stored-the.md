---
id: in-the-proof-the-voter-still-stored-the
type: axiom
title: "In the proof, the voter still stored the committed entry when it voted for leaderU, because every intervening leader contained the entry, leaders never remove entries, and followers only remove entries that conflict with the leader"
statement: "In the proof, the voter still stored the committed entry when it voted for leaderU, because every intervening leader contained the entry, leaders never remove entries, and followers only remove entries that conflict with the leader."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [in-the-proof-the-voter-must-have-accepted]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# In the proof, the voter still stored the committed entry when it voted for leaderU, because every intervening leader contained the entry, leaders never remove entries, and followers only remove entries that conflict with the leader

In the proof, the voter still stored the committed entry when it voted for leaderU, because every intervening leader contained the entry, leaders never remove entries, and followers only remove entries that conflict with the leader.

Evidence: [[https-raft-github-io-raft]].
[[in-the-proof-the-voter-must-have-accepted]]
