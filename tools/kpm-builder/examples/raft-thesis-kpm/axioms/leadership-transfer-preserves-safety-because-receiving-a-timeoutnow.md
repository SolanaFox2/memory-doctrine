---
id: leadership-transfer-preserves-safety-because-receiving-a-timeoutnow
type: axiom
title: "Leadership transfer preserves safety because receiving a TimeoutNow request is equivalent to the target server's clock jumping forward quickly, which Raft already tolerates"
statement: "Leadership transfer preserves safety because receiving a TimeoutNow request is equivalent to the target server's clock jumping forward quickly, which Raft already tolerates."
domain: "distilled"
generativity: 3
confidence: 0.5
status: candidate
relations:
  derives-from: [raft-maintains-the-consistency-of-its-logs-without]
  supports: []
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]
provenance: "package-research/distilled"
---

# Leadership transfer preserves safety because receiving a TimeoutNow request is equivalent to the target server's clock jumping forward quickly, which Raft already tolerates

Leadership transfer preserves safety because receiving a TimeoutNow request is equivalent to the target server's clock jumping forward quickly, which Raft already tolerates.

Evidence: [[https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd]].
[[raft-maintains-the-consistency-of-its-logs-without]]
