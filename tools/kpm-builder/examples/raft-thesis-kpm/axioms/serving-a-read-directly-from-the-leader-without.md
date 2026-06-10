---
id: serving-a-read-directly-from-the-leader-without
type: axiom
title: "Serving a read directly from the leader without extra measures risks returning stale data, because the leader responding might have been superseded by a newer leader of which it is unaware"
statement: "Serving a read directly from the leader without extra measures risks returning stale data, because the leader responding might have been superseded by a newer leader of which it is unaware."
domain: "distilled"
generativity: 5
confidence: 0.9
status: candidate
relations:
  derives-from: []
  supports: [before-answering-a-read-only-request-the-leader]
  generalizes: []
  contradicts: []
  applies-to-kpm: []
evidence: [https-raft-github-io-raft]
provenance: "package-research/distilled"
---

# Serving a read directly from the leader without extra measures risks returning stale data, because the leader responding might have been superseded by a newer leader of which it is unaware

Serving a read directly from the leader without extra measures risks returning stale data, because the leader responding might have been superseded by a newer leader of which it is unaware.

Evidence: [[https-raft-github-io-raft]].
[[before-answering-a-read-only-request-the-leader]]
