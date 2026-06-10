---
name: package-research
description: >
  Turn a folder of raw notes into a doctrine-grounded knowledge package (KPM)
  WITHOUT an API key — the agent itself does the distill/score/verify judgment.
  Use when asked to "package research", "build a KPM from these notes", or
  "distill a notes folder into a knowledge package" inside an LLM coding agent.
---

# package-research — keyless skill mode

This tool turns a folder of raw notes into a doctrine-grounded **knowledge
package (KPM)**. It has two ways to run:

- **Auto mode** — `package-research run <dir> --out <dir>` calls the Anthropic
  API to do the distill/score/verify judgment. Needs `ANTHROPIC_API_KEY`.
- **Skill mode (this doc)** — `ingest` then `build`. **No API key.** *You*, the
  LLM agent (Claude Code, etc.), do the distillation that the API would
  otherwise do. This is the recommended way to run it from inside an agent.

The deterministic stages (ingest → split → assemble → validate) always run as
code, so the produced package is guaranteed structurally valid (it self-validates
with a vendored `doctrine_lint.py`).

## The standard it grades against (this lives *inside* the doctrine)

This tool is part of the **Memory Doctrine** stack: the doctrine is the *theory*,
it defines the *standard*, and this tool *implements* it. It is not standalone —
it sits at `memory-doctrine/tools/package-research/` and grades against the **live**
doctrine, not a copy:

- **The standard** (what a valid package is) → the doctrine
  [`README.md`](../../README.md) and its mechanical checker
  [`scripts/doctrine_lint.py`](../../scripts/doctrine_lint.py). This tool's
  `vendor/doctrine_lint.py` is a *symlink* to that canonical checker — no fork,
  no drift. Change the standard and the tool follows automatically.
- **The rubric** your judgment must follow:
  - **E1 (distill to generators)** + **E4 (verify, refute-by-default)** →
    [`clusters/E-method.md`](../../clusters/E-method.md)
  - **C1 (confidence earned from evidence, not fluency)** →
    [`clusters/C-truth.md`](../../clusters/C-truth.md)
  - **B4 (thin index over rich store)** →
    [`clusters/B-retrieval.md`](../../clusters/B-retrieval.md)
  - all axioms → [`axioms/`](../../axioms/)

Read those before you distill — they are the live grading criteria.

## The two-command workflow

### 1. Ingest — read the candidate passages

```bash
package-research ingest ./notes --json
```

This prints a JSON array of candidate passages, deterministically chunked from
the notes folder:

```json
[
  { "index": 1, "source_file": "what-is-caching.md", "text": "A cache is a small, fast store ..." },
  { "index": 2, "source_file": "cache-hits-and-misses.md", "text": "A cache hit happens when ..." }
]
```

Read this. `source_file` is a **relative path string** — use it verbatim as the
locator when you cite a passage. (Without `--json` it prints the same passages in
a human-readable form.)

### 2. Distill the candidates into `ideas.json` (this is your job)

Following the doctrine's rubric, distill the candidates into a small set of
**generative ideas** and write them to an `ideas.json` file. The rubric:

- **E1 — keep the generators, not summaries.** Extract the load-bearing *ideas*
  that the notes generate, not a restatement of the notes. One idea per object.
- **C1 — score confidence ONLY from the evidence present, never from fluency.**
  `confidence` is a float in `[0, 1]` earned from the supporting snippets — not
  from how well-written the statement is.
- **Attach provenance.** For each idea list the `supporting_source_files` (the
  `source_file` strings from ingest) and verbatim `supporting_snippets` copied
  from the candidate text.
- **E4 — drop / penalize unsupported ideas.** If an idea has no real snippet
  backing it, drop it. `build` enforces this too (ideas with no snippet are
  dropped), but you should not propose them in the first place.
- `generativity` is an int in `1..5` (how load-bearing the idea is).
- `rationale` (optional) — one line on why the evidence licenses the score.

`ideas.json` is a JSON list of objects:

```json
[
  {
    "statement": "Caching trades a modest amount of memory for a large reduction in latency on repeated requests.",
    "supporting_source_files": ["what-is-caching.md"],
    "supporting_snippets": [
      "A cache trades a modest amount of memory for a large reduction in latency on repeated requests."
    ],
    "confidence": 0.9,
    "generativity": 5,
    "rationale": "Stated directly in the source; the generative why-caching-works principle."
  },
  {
    "statement": "Hit rate governs average response time: a higher fraction served from cache lowers average latency.",
    "supporting_source_files": ["cache-hits-and-misses.md"],
    "supporting_snippets": [
      "A higher hit rate means more requests avoid the slow path, so the average response time drops as the hit rate rises."
    ],
    "confidence": 0.85,
    "generativity": 4
  }
]
```

`build` coerces defensively: `confidence` is clamped to `[0, 1]`, `generativity`
to `1..5`, and any idea with **no non-empty supporting snippet is dropped**.

### 3. Build — produce the lint-clean KPM package

```bash
package-research build ./notes --ideas ./ideas.json --out ./my-kpm --name @kpm/my-notes
```

This runs `split → assemble → validate` and prints the same summary `run`
prints (candidates / ideas / kept counts, `doctrine lint`, `kpm doctor`). It
exits non-zero only if `doctrine_lint` fails. The output `./my-kpm/` is a
complete, self-validating KPM package (`knowledge.json`, `axioms/`, `evidence/`,
`README.md`, vendored `scripts/doctrine_lint.py`).

Add `--keep-uncited` (to either `run` or `build`) to preserve sources that no
axiom cited into a `reference/` folder, so nothing is silently dropped — useful
when you want a full audit trail of the input notes.

## Why skill mode

Running it this way means **no `ANTHROPIC_API_KEY` is needed** for `ingest` or
`build` — the model judgment (distillation, confidence, refutation) is done by
the agent reading this skill, and the tool handles the deterministic, structure-
guaranteeing work. That makes `package-research` runnable inside any LLM coding
agent with zero secrets.
