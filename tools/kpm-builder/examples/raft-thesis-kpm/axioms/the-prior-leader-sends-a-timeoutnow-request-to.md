---
id: the-prior-leader-sends-a-timeoutnow-request-to
type: axiom
title: "The prior leader sends a TimeoutNow request to the target server, which has the same effect as the target's election timer firing, causing it to immediately start a new election without waiting for its election timeout"
statement: "The prior leader sends a TimeoutNow request to the target server, which has the same effect as the target's election timer firing, causing it to immediately start a new election without waiting for its election timeout."
domain: "distilled"
generativity: 4
confidence: 0.5
status: candidate
relations:
  derives-from: []
  supports: [leadership-transfer-preserves-safety-because-receiving-a-timeoutnow]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# The prior leader sends a TimeoutNow request to the target server, which has the same effect as the target's election timer firing, causing it to immediately start a new election without waiting for its election timeout

The prior leader sends a TimeoutNow request to the target server, which has the same effect as the target's election timer firing, causing it to immediately start a new election without waiting for its election timeout.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[leadership-transfer-preserves-safety-because-receiving-a-timeoutnow]]
