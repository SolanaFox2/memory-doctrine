---
axioms:
- commitindex-and-lastapplied-are-volatile-state-on-all
- figure-2-lists-lastapplied-as-volatile-but-the
basis: []
confidence: partial
resolved: '2026-06-05'
status: reconciled
truth: Figure 2 lists lastApplied as volatile for the default (volatile) state machine,
  but for a persistent state machine the last-applied index must also be persistent
  so that already-applied entries are not reapplied after a restart.
truth_passage_id: https-web-stanford-edu-ouster-cgi-bin-papers-ongarophd
type: resolution
---

# Resolution: commitindex-and-lastapplied-are-volatile-state-on-all ↔ figure-2-lists-lastapplied-as-volatile-but-the

The paper's Figure 2 specifies the baseline design where the state machine is rebuilt from the log, so lastApplied is volatile; the thesis refines this for the special case of a persistent state machine, where lastApplied must be persisted to avoid reapplying entries. A is the general rule, B the persistent-SM refinement.
