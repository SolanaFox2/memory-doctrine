# package-research — architecture

How the tool turns a folder of notes into a doctrine-conformant knowledge
package. For *using* it (install, run, modes), see [README.md](README.md).

## Overall shape

Input is a directory; output is a directory. In between, the notes pass through
seven stages. Four are **mechanical** (pure code — deterministic and tested);
three are **judgment** (reading and deciding).

```
ingest → distill → score → verify → split → assemble → validate
 mech     judg     judg     judg     mech     mech       mech
```

All judgment goes through one function with a fixed output schema, so the records
that come out are structured the same way no matter who does the judging.

## Data flow — what goes in and out of each stage

| Stage | Input | Output | Kind |
|---|---|---|---|
| **ingest** | folder of `.md`/`.txt` | passages — each with its text, source path, exact character span, and section heading | mechanical |
| **distill** | all passages | a few candidate ideas, each with the source files + snippets that back it | judgment |
| **score** | each idea | the same idea + a confidence (0–1) + a generativity (1–5) + a one-line rationale | judgment |
| **verify** | each scored idea | a filtered set — unsupported ideas dropped, shaky ones down-scored | judgment |
| **split** | surviving ideas + the per-source passages | two linked sets of notes: an axiom index and an evidence store | mechanical |
| **assemble** | the two sets | files on disk: `knowledge.json`, `axioms/`, `evidence/`, `README.md`, the vendored linter | mechanical |
| **validate** | the written package | pass/fail from two checkers | mechanical |

The mechanical stages take no clock or randomness — the one date (each evidence
note's `verified` stamp) is computed once at the entry point and passed in — so
the same input yields a byte-identical package.

## The judgment seam

The three judgment stages never touch files or formats. They call one function — the single point where a model or agent plugs in:

```
complete_json(prompt, schema)  →  a JSON object that matches schema
```

- **Auto mode** wires that seam to a model (Anthropic SDK). Needs an API key.
- **Keyless ("skill") mode** makes the seam an AI agent: `ingest` prints the
  passages, the agent writes an `ideas.json`, and `build` runs the mechanical
  tail. No key. See [SKILL.md](SKILL.md).

Validity is enforced by the mechanical stages, so a sloppy judgment still yields
either a well-formed package or a hard failure — never a silently broken one.
Quality of *content* depends on the judge; correctness of *form* does not.

## The records (in memory)

A passage after **ingest**:

```
text:            "## The benchmark landscape\nLoCoMo ... BEAM ..."
source_file:     "decay-benchmarks.md"   # relative path
char_span:       (4120, 4980)            # raw[start:end] == text — exact provenance
section_heading: "the benchmark landscape"
```

An idea after **verify**:

```
statement:               "The bottleneck is the memory design, not model scale."
confidence:              0.70            # earned from the evidence present
generativity:            5               # 1–5
supporting_source_files: ["decay-benchmarks.md"]
supporting_snippets:     ["AMA-Bench ... 8B to 32B gave only marginal gains ..."]
rationale:               "single benchmark; held below the conceptual claims"
```

## On-disk format

A plain directory of Markdown + one JSON manifest:

```
my-kpm/
  knowledge.json        # the manifest (the only JSON)
  README.md             # a generated index of the axioms
  axioms/<id>.md        # the index — one note per idea
  evidence/<id>.md      # the store — one note per source, preserved content
  reference/<id>.md     # (only with --keep-uncited) un-cited sources, preserved
  scripts/doctrine_lint.py   # vendored so the package validates itself
```

An **axiom note** (the index) — a structured header over a short body:

```yaml
id: the-bottleneck-is-the-memory-design
type: axiom
title: "The bottleneck is the memory design, not model scale"
generativity: 5
confidence: 0.7
status: locked        # challenge survivors promote: locked >= 0.7, else provisional
relations: { derives-from: [], supports: [decay-is-a-feature], generalizes: [], contradicts: [], applies-to-kpm: [] }
evidence: [decay-benchmarks]          # → into the store
provenance: "package-research/distilled"
```

An **evidence note** (the store) records the source (`ref`, `url`, `verified`)
and which axioms rest on it (`supports`), and its body is the **preserved source
passages** for that file — not just the one line an axiom quoted.

## Identity & linking

- An axiom's id is a slug of its statement; an evidence note's id is a slug of
  the source's full relative path (so two files that share a basename in
  different folders stay distinct). Colliding slugs are disambiguated `-2/-3`,
  checked against the set of ids already used, so a clash is impossible.
- **Index → store:** each axiom's `evidence: [ids]` (mirrored by a `[[id]]`
  wikilink in the body).
- **Store → index:** each evidence note's `supports: [ids]`. The graph is
  bidirectional.
- **Sources are de-duplicated:** two ideas that cite the same file share one
  evidence note.
- An axiom is written only if at least one evidence id it cites resolves to a
  real note — so every link resolves.

## Keeping the details (the store)

The evidence body is the source file's passages, grouped by file, with process
sections (methodology, follow-up lists, tool-failure reports) trimmed by their
heading. So the package keeps findings, not just the headlines.

## Coverage — nothing dropped silently

Every run reports which sources no axiom cited. With `--keep-uncited`, those go
into `reference/` (clearly marked, ignored by the linter) so no file disappears
without being named.

## Skill-mode interchange — `ideas.json`

In keyless mode this is the hand-off from judge to machine — one array entry per
idea:

```json
{ "statement": "...", "supporting_source_files": ["..."],
  "supporting_snippets": ["..."], "confidence": 0.85,
  "generativity": 5, "rationale": "..." }
```

An entry with no snippet is rejected; confidence is clamped to 0–1, generativity
to 1–5.

## Validation — the two gates

1. **`doctrine_lint`** (always): required header fields present and well-typed,
   every axiom cites at least one resolving evidence note, every link resolves,
   every evidence note carries a source and a verification date. It is vendored
   into each package so the package validates itself.
2. **`kpm doctor`** (best-effort): the package manager's structural check —
   manifest valid, entrypoint exists. Skipped cleanly when `kpm` isn't
   installed; resolved portably via `PATH`/env, no hardcoded paths.

A run prints a one-screen summary: passages ingested, ideas kept, source
coverage, output path, and each gate's result.
