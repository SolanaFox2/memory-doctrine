# package-research

The Memory Doctrine's **consuming tool**. It turns a folder of raw notes /
research into a doctrine-grounded **knowledge package (KPM)** — proving the
doctrine is something tools can *run*, not just read.

*How it works inside — data flow, record shapes, on-disk formats: [ARCHITECTURE.md](ARCHITECTURE.md).*

The full pipeline is:

```
ingest → distill → score → verify → split → assemble → validate
```

Each stage maps to a doctrine axiom: distill the *generators* not the notes
(E1), score confidence from the evidence actually present never from fluency
(C1), refute-by-default + citation-presence on every idea (E4), and split a thin
index of axioms over a fat store of evidence (B4). The deterministic gates
(`doctrine_lint.py` + `kpm doctor`) guarantee the **output is structurally
valid** even when the model's judgment varies.

## Two ways to run

| Mode | Command(s) | API key | Who does the judgment |
|------|-----------|---------|-----------------------|
| **Auto** | `package-research run` | **Required** (`ANTHROPIC_API_KEY`) | The Anthropic API (distill/score/verify stages call out). |
| **Keyless skill mode** | `package-research ingest` → `package-research build` | **None** | *You* — the LLM agent (Claude Code, etc.) distills the candidates into an `ideas.json`. |

Skill mode exists so an agent can drive the whole pipeline with no secrets: the
deterministic stages run as code and the model judgment is supplied by the agent.
See [`SKILL.md`](SKILL.md) for the full keyless agent workflow. The rest of this
README documents **auto mode**.

## Install

This is a `src`-layout package. Install it (editable) into a virtualenv:

```bash
cd tools/package-research
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

That puts the `package-research` command on your `PATH`.

> Heads-up: on Homebrew / Debian "externally-managed" Pythons, install into a
> venv as shown above (or pass `--break-system-packages` if you know what you're
> doing). The tests need no install — see [Running the tests](#running-the-tests).

## Set your API key

The three LLM-backed stages (distill / score / verify) call the Anthropic API,
so a key is **required to actually run the pipeline**. It is read from the
environment and never stored on the config object or in any output:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Without it, `package-research run` exits with a clear error before making any
network call.

## Run it

Point the tool at a folder of `.md` / `.txt` notes and tell it where to write
the package. A ready-made sample corpus lives in [`examples/notes/`](examples/notes/)
(a few plain notes on the basics of caching):

```bash
package-research run ./examples/notes --out ./example-kpm
```

Options (shared by `run` and `build` unless noted):

| Flag | Meaning |
|------|---------|
| `--out DIR` | **Required.** Where the KPM package is written. |
| `--model MODEL` | `run` only. Anthropic model for the LLM stages (default: `claude-sonnet-4-6`). |
| `--name NAME` | Package name in `knowledge.json` (e.g. `@kpm/caching-basics`). |
| `--description TEXT` | Package description in `knowledge.json`. |
| `--keep-uncited` | Preserve sources no axiom cited into `reference/`, so nothing is silently dropped. |
| `--max-sources N` | Cap on source files ingested (alphabetical; truncation warns to stderr). Default 200. |
| `--force` | Write into a non-empty `--out` dir even when it is not a package this tool produced. |

Re-running into the same `--out` is safe: a directory that already holds a
package (has a `knowledge.json`) gets its `axioms/`, `evidence/`, `reference/`
and `clusters/` notes cleared first, so no stale notes from a previous run
survive. A non-empty directory that is *not* a recognizable package is refused
unless you pass `--force` — the tool never silently deletes your data.

On success it prints a summary like:

```
package-research run complete
  candidates ingested : 8
  ideas distilled     : 5
  ideas scored        : 5
  kept after verify   : 4
  output package      : example-kpm
  doctrine lint       : OK (0 violations)
  kpm doctor          : OK
```

The process exits **non-zero if `doctrine_lint` fails** (a structurally invalid
package is a hard error). `kpm doctor` is best-effort: it runs if the `kpm` CLI
is installed and is reported as `skipped` otherwise.

### Keyless skill mode (no API key)

To run inside an LLM agent with no `ANTHROPIC_API_KEY`, use the two skill
subcommands — the agent supplies the distillation judgment:

```bash
# 1. read the candidate passages
package-research ingest ./examples/notes --json

# 2. (agent distills the candidates into ideas.json per SKILL.md's rubric)

# 3. build the package from the agent-written ideas.json
package-research build ./examples/notes --ideas ./ideas.json --out ./example-kpm
```

`build` prints the same summary as `run` and produces an identical, lint-clean
package. It takes the same output flags as `run` (`--name`, `--description`,
`--keep-uncited`, `--max-sources`, `--force` — see the table above). Full
rubric + a worked `ideas.json` example are in [`SKILL.md`](SKILL.md).

## What comes out

A complete, self-validating KPM package in `--out`:

```
example-kpm/
  knowledge.json          # the kpm manifest
  README.md               # generated overview listing the axioms
  axioms/<id>.md          # the INDEX: thin claims + scores, one per surviving idea
  evidence/<id>.md        # the STORE: verbatim snippets, one per source, cross-linked
  scripts/doctrine_lint.py  # the vendored validator (the package self-validates)
```

Every axiom carries doctrine-schema frontmatter (confidence 0–1, generativity
1–5, relations, cited evidence ids) and wikilinks to the evidence it rests on.
The package passes the doctrine's own `doctrine_lint.py` and, if `kpm` is
installed, `kpm doctor`:

```bash
kpm doctor          # run from inside ./example-kpm
```

## Running the tests

The tests require **no API key** — the LLM stages are mocked, so the full
pipeline (including the real `doctrine_lint`) runs offline:

```bash
python3 -m pytest -q
```

(`tests/conftest.py` puts the `src/` layout on the path, so no install is needed
for tests.)

## Scope (v1 honesty)

- **Verify** = adversarial self-critique + citation-*presence* (does each idea
  cite a real snippet from your sources?). Full **web** citation-verification is
  a later stretch goal, not v1.
- Distillation quality depends on the model. The tool ships sensible defaults +
  doctrine-grounded prompts, and the deterministic gates guarantee a
  structurally valid package regardless.

## Project layout

```
package-research/
  pyproject.toml
  src/package_research/
    config.py    # typed pydantic config (input/output dirs, model, caps)
    cli.py       # `package-research run` — wires the full pipeline
    llm.py       # mockable Anthropic wrapper (complete_json)
    ingest.py    # deterministic read + chunk -> Candidate[]
    distill.py   # LLM: candidates -> Idea[]      (E1)
    score.py     # LLM: confidence + generativity (C1)
    verify.py    # LLM adversarial + citation-presence (E4)
    split.py     # deterministic index/store split (B4)
    assemble.py  # write the kpm package (knowledge.json, axioms/, evidence/)
    validate.py  # run doctrine_lint + kpm doctor
  prompts/       # the doctrine-grounded distill/score/verify rubrics
  examples/notes/  # a small, public-safe sample corpus (caching basics)
  tests/         # fixture-based tests; LLM mocked, no API key needed
```
