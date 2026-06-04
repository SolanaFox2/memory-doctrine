# package-research — backlog

Implementation tasks. The *standard-level* questions these connect to live in the
doctrine's [`OPEN-QUESTIONS.md`](../../OPEN-QUESTIONS.md) (Q1, Q2).

## Done
- Rich store — evidence notes preserve the source content, not just the cited line.
- Coverage report — every run names the sources no axiom cited (no silent loss).
- `--keep-uncited` → `reference/` bucket preserving un-cited sources (doctrine Q1, tool half).
- Single-source linter — `vendor/doctrine_lint.py` symlinks the doctrine's canonical checker.

## Todo
- **Source-quality pre-filter** (doctrine Q2, tool half): drop sources that are
  mostly link-lists, or whose content is near-duplicated boilerplate across many
  files. Heuristic, tool-level — surfaced by a corpus that was ~85% failed scrapes.
- **Batch / raise the ingest cap**: past `max_sources` (200) files are dropped at
  ingest and `--keep-uncited` can't save them (never ingested). Either batch large
  corpora or make the cap configurable; the truncation warning already flags it.
- Web citation-verification (stretch): verify, don't just check citation presence.
