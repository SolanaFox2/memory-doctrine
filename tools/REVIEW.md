# Tools review — `package-research` & `kpm-builder`

A review of the two tools under `tools/`, covering **effectiveness** (do they
accomplish their stated goals?) and **code quality / correctness**. Findings are
prioritized; each carries a `file:line` reference and a concrete fix so the team
can triage and pick up threads independently.

> Scope: `tools/package-research` (the doctrine's consuming tool — notes → KPM)
> and `tools/kpm-builder` (research-from-scratch KPM skill). Line numbers reflect
> the state of the branch at review time.

## How this was assessed

- Ran both test suites: **package-research 27 passed**; **kpm-builder 267 passed,
  1 skipped** — but only after `pip install -e tools/package-research` and adding
  it to `PYTHONPATH` (kpm-builder has no installable packaging; see INF‑1).
- Built a package with each tool and inspected the output against the doctrine's
  own headline claims (keyless `build` for package-research on
  `examples/notes`; the committed `examples/raft-thesis-kpm` for kpm-builder).
- Read every source file in both tools, the prompts, the vendored linter, the
  shared `validate` seam, the docs, and the CI workflow.

---

## 1 · Effectiveness — do the tools accomplish their goals?

**Verdict:** both reliably produce a package that passes `doctrine_lint`, but the
linter is a *weak proxy* for the doctrine. The output is doctrine‑**shaped**
without being doctrine‑**embodying**, and the gap sits in exactly the claims the
README leads with. The tools optimize to the lint; the lint under‑specifies the
doctrine.

### EFF‑1 — The #1 thesis ("value lives in the connections, not the nodes") is the least delivered. **[High]**
- `package-research` emits **zero** inter‑axiom connections — every axiom's
  `relations:` block is hardcoded to five empty lists (`assemble.py:100`).
  Confirmed on a fresh build: 0/3 axioms had any edge. It produces a bag of
  disconnected nodes — the exact thing the doctrine calls least valuable.
- `kpm-builder` does materially better (its `relate`/`resolve`/`apply_relations`
  subsystem is real): **43 of 150** axioms in its own example carry a typed edge
  (~29%). Still 0% in the flagship tool.
- The lint passes regardless because it only checks that declared edges
  *resolve* (`scripts/doctrine_lint.py:94-99`), never that any edge *exists*.

*Fix:* package-research needs a relate pass (it can reuse kpm-builder's
`relate.py` once the shared seam is extracted — see INF‑3). At minimum, the lint
should warn when a multi‑axiom package has an edge density of ~0.

### EFF‑2 — "Lock only after an adversarial challenge" never happens. **[High]**
The README sells a belief‑state machine: `candidate → locked` after a challenge +
citation check. Both tools emit `status: candidate` for **100%** of axioms
(150/150 kpm-builder, 3/3 package-research). package-research's `verify` stage and
kpm-builder's `refute.py` *drop* losers but never *promote* survivors;
`render_axiom` hardcodes `status: candidate` (`assemble.py:112`). `provisional`
is never emitted. The entire adversarial apparatus produces no visible state
change.

*Fix:* have `verify`/`refute` return a survived‑challenge signal and map it to
`status: locked` (or `provisional` for weak‑evidence survivors); thread it through
`split`/`strip` into `render_axiom`.

### EFF‑3 — Thin‑index / rich‑store degrades toward thin‑index / thin‑store. **[High]**
kpm-builder's 150 axioms cite just **3 distinct evidence notes** — spans are
whole‑document (`orchestrate.py:240-247`, `cli.py:184-189` build
`SpanRef(0, len(text), text)`) and deduped by URL (`strip.py:67`), so 150 claims
collapse onto 3 document dumps. Its own SKILL.md calls passage‑scoping the biggest
quality lever, yet the engine never records which passage entailed the claim.
package-research is better (one evidence note per source, real snippets) but in
skill mode `split._enrich_evidence_bodies` (`split.py:243-270`) *replaces* the
agent's cited snippet with re‑ingested passages, discarding the exact cited line.

*Fix:* carry `supporting_passage` through to the `SpanRef` and ship `span.text` =
the passage, not the document; in package-research, append (don't replace) the
cited snippet.

### EFF‑4 — No theme clustering. **[Medium]**
The doctrine organizes axioms into seven themes and the repo has `clusters/`;
neither tool sets a `cluster:` pointer on a single axiom (0/150, 0/3). kpm-builder
*writes* pairwise cluster files but never points axioms at them.

*Fix:* emit a `cluster:` field and ensure it resolves (the lint already validates
it at `scripts/doctrine_lint.py:81-83`).

### EFF‑5 — Confidence is mostly pass‑through, not earned. **[Medium]**
Doctrine: "confidence earned from evidence, not from how it sounds." In keyless
mode confidence is whatever number the agent wrote, only clamped
(`cli.py:350-355`). With an API key package-research *does* score — but see H1
(single‑prompt truncation) which silently breaks scoring on real inputs.
kpm-builder's `confidence.py` is more principled (tiers + corroboration counts)
but its live MVP path hardcodes `n_independent_corroborations=1`
(`orchestrate.py:170-173`), making the SUPPORTED tier unreachable there.

### What works well
- Deterministic, reproducible assembly that always passes the structural gate
  (`run_date` injected, never `datetime.now()`).
- A clean keyless "skill mode" seam — the agent does judgment, the tool does
  structure + checks. Good separation.
- kpm-builder's relate/resolve/refute machinery is substantial and real; the
  bones for a connected, adversarially‑tested graph are already there.

---

## 2 · `package-research` — code quality & correctness

### High
- **H1 — Distill sends the entire corpus in one prompt; silent truncation on real
  inputs.** `distill.py:124` + `distill.py:78-81` concatenate every candidate into
  one message; `llm.py:64` caps the response at `max_tokens=4096` and
  `complete_json` never inspects `stop_reason`. With `max_sources=200` /
  `max_chunk_chars=1500` the response routinely truncates → `_extract_json`
  (`llm.py:25`) either raises (retried identically, then hard‑fails) or succeeds on
  a `{...}` substring that drops ideas. *Fix:* batch candidates and union via the
  existing `_dedupe`; detect `stop_reason == "max_tokens"`; make `max_tokens`
  configurable.
- **H2 — Retries are useless for transient failures and treat all errors alike.**
  `llm.py:88-100`: no backoff/jitter, catches every `Exception` identically, so a
  429/529 is retried instantly (2 immediate retries → near‑instant exhaustion)
  while a deterministic parse error is retried with the identical prompt. *Fix:*
  rely on the SDK's built‑in backoff or add exponential backoff with jitter;
  distinguish `RateLimitError`/`APIStatusError` from `JSONDecodeError`; on parse
  failure send a corrective follow‑up, not the same prompt.
- **H3 — Note content is interpolated into prompts with no isolation
  (prompt‑injection surface).** `distill.py:74`, `score.py:57-67`,
  `verify.py:69-80` embed raw note text/snippets with no delimiting. Untrusted
  scrapes (the BACKLOG notes "~85% failed scrapes") can steer score/verify. *Fix:*
  wrap untrusted content in delimited blocks the system prompt declares as
  data‑not‑instructions.
- **H4 — "Model returned garbage" is silent and handled three different ways.**
  `verify.py:120-123` → drop; `distill.py:127` → no ideas; `score.py:104-105` →
  confidence 0.0. None warns. An all‑malformed run yields an empty/zero package
  that *passes* lint and is indistinguishable from a legitimate "nothing
  survived". *Fix:* centralize, warn to stderr, surface a count in the summary.

### Medium
- **M1 — Re‑running over an existing output dir leaves stale notes.**
  `assemble.py:290-293` does `mkdir(exist_ok=True)` and writes in place; ids that
  no longer exist are never deleted → orphan notes. *Fix:* clear
  `axioms/`/`evidence/`/`reference/` first, or write to a temp dir and swap; add a
  `--force` guard.
- **M2 — Skill‑mode snippets discarded (EFF‑3) and numeric‑string generativity
  collapses to 1.** `cli._clamp_generativity` (`cli.py:358-363`) does `int(value)`
  so `"4.0"` → `ValueError` → 1. *Fix:* `int(float(value))` with rounding.
- **M3 — Three near‑identical clamp helpers** (`score.py:76-97`, `verify.py:89-98`,
  `cli.py:350-363`) that differ subtly — which is how M2 crept in. *Fix:* hoist one
  `clamp_confidence`/`clamp_generativity` into a shared module.
- **M4 — `_extract_json` can return the wrong object** from prose containing
  braces (`llm.py:43-46`, first `{` … last `}`). *Fix:* prefer SDK tool/JSON mode;
  failing that, balanced‑brace scan + schema‑validate.
- **M5 — Ingest follows symlinks and can leak absolute paths.** `ingest.py:163`
  follows symlinks; `_relative_source` (`ingest.py:119-129`) falls back to absolute
  paths, which land in `ref:`/`url:` (`assemble.py:137-138`). *Fix:* skip symlinks
  resolving outside `input_dir`; never emit absolute paths.
- **M6 — `max_sources` truncates by alphabetical order with no CLI flag.**
  `ingest.py:243-251`; cap only settable via `PR_MAX_SOURCES` env
  (`config.py:92`). *Fix:* add `--max-sources` to `run`/`build`.
- **M7 — `validate` scrapes the linter's stdout format** (`validate.py:53-59`),
  tightly coupled to the print format. *Fix:* call `check()` in‑process and capture
  structured `errs`, or add a `--format json` to the linter.
- **M8 — No subprocess timeouts** (`validate.py:45-49`, `:111-117`). A hung `kpm`
  hangs the whole run. *Fix:* pass `timeout=` and report `TimeoutExpired`.

### Low
- **L1** — `run`/`build` flag sets diverge (`--model` vs `--description`); README
  doesn't cover `build`'s shared flags (`cli.py:50-68`).
- **L2** — Empty‑input UX is silent: "0 sources found" vs "all refuted" are
  indistinguishable (exit 0, no hint). Warn at `ingest.py:242`.
- **L3** — `Config.from_env` casts `PR_MAX_SOURCES` with bare `int()`
  (`config.py:93`) → opaque `ValueError`.
- **L4** — `_title_from_statement` splits on `.;:` (`split.py:67`) so "e.g. …"
  truncates the title at "e".
- **L5** — `_yaml_str` doesn't normalize `\t`/`\r` (`assemble.py:63-66`).
- **L6** — `default_confidence`/`default_generativity` in `Config`
  (`config.py:46-57`) are **unused** dead config.
- **L7** — Test gaps (no API key needed): `llm.py` is essentially untested
  (`_extract_json` fenced/prose/brace‑span, `_response_text`, retry exhaustion);
  non‑UTF‑8 skip path; `max_sources` truncation warning; re‑run orphan‑note
  behavior (M1); `validate`'s failure‑parsing path.
- **L8** — `_response_text` returns `""` for an all‑non‑text response
  (`llm.py:115`) → burns retries with no diagnostic.

---

## 3 · `kpm-builder` — code quality & correctness

### High
- **H1 — No `pyproject.toml`; not installable; undeclared hard dependency on
  `package_research`.** Only `requirements.txt` (pyyaml, pydantic) exists;
  `orchestrate.py:62-64`, `cli.py:43-45`, `strip.py:27`, `apply_relations.py:32`,
  `run_mvp.py:124` all `import package_research`, yet it's never declared. Clean
  installs fail with `ModuleNotFoundError`. *Fix:* add a `pyproject.toml`
  mirroring the sibling (setuptools, `requires-python>=3.10`, `[project.scripts]`
  for the four CLIs), and declare `package-research` + pydantic/pyyaml as deps.
  (Also tracked as INF‑1.)
- **H2 — `extract_json` mis‑parses multi‑object and truncated responses.**
  `providers.py:86-92` falls back to `text[find("{"):rfind("}")+1]` — reproduced
  failures: `'{"a":1} junk {"b":2}'` → `Extra data`; truncation at
  `max_tokens=1024` → `Unterminated string`, raised raw. Every provider caps at
  1024 (`providers.py:127,148,163`); the `relate` propose call (`relate.py:165`)
  returns an array over *all* axioms and will routinely exceed it. *Fix:* raise/
  parameterize `max_tokens`; use `JSONDecoder().raw_decode()` at the first `{`;
  raise a typed `ProviderJSONError` with a snippet.
- **H3 — No retry/timeout/error handling anywhere in the provider layer.**
  `providers.py:124-171` call the SDK once and return; no `except`/backoff/timeout
  across the file. A single transient blip kills a build that may have spent
  hundreds of thousands of tokens (`relate_kpm` calls per edge,
  `relate.py:383-386`; `resolve` 2‑3 per contradiction). *Fix:* bounded retry +
  backoff on retryable errors, request timeout, typed error after exhaustion;
  consider checkpointing verified relations/resolutions to disk.
- **H4 — `relate_kpm`/`resolve_kpm` have no partial‑failure isolation.**
  `relate.py:383-386` (list comp per edge) and `resolve.py:373-377` (loop per
  contradiction): one failure aborts the stage and discards prior work. *Fix:*
  try/except per item, log‑and‑skip (matches "default false on doubt"), return a
  skipped count.
- **H5 — Shipped axioms attach the entire snapshot as the evidence span**
  (`orchestrate.py:240-247`, `cli.py:184-189`), defeating passage‑scoping (see
  EFF‑3). *Fix:* carry `supporting_passage` into the `SpanRef` via `make_span`
  (`snapshot.py:106`).

### Medium
- **M1 — `over_claims` claims inflate "quality sources" / ANSWERED.**
  `cli.py:136-140` increments `n_quality_sources` for any verdict `!= "reject"`,
  and `claim_buckets` (`cli.py:134`) includes dropped claims; `orchestrate.py:180-182`
  has the analogous issue. A beat with one real `entails` + one `over_claims` can
  report ANSWERED with two "quality sources". *Fix:* count only `entails`; don't
  let dropped claims drive the coverage bucket.
- **M2 — Malformed input beats crash with bare `KeyError`** (`cli.py:95,104-106`);
  `research_log.json` echoes raw input unvalidated. *Fix:* validate the input
  shape up front (pydantic is already a dep but unused here).
- **M3 — Bare `KeyError` on missing fetch URL** (`orchestrate.py:74-77`);
  `is_relevant` collapses malformed judge output to "not relevant"
  (`gate.py:181`). *Fix:* validate the fetcher key set; distinguish "judge said no"
  from "no parseable answer".
- **M4 — Heavy duplication with package-research** (see INF‑3); plus three
  in‑module frontmatter splitters (`_util.py:11`, `relate.py:31`,
  `apply_relations.py:38`).
- **M5 — `resolve._default_ground` fabricates a throwaway snapshot** with
  `internal://passage` + hardcoded `fetched_at` (`resolve.py:257-263`), so
  resolution‑truth provenance is disconnected from real evidence. *Fix:* thread the
  real evidence snapshot/date.
- **M6 — `apply_relations` doesn't drop dangling endpoints** like `apply_guards`
  does; a single bad hand‑built `to_id` aborts the whole apply via lint rollback
  (`apply_relations.py:120-138`, validate at `:145`). *Fix:* drop relations whose
  endpoints aren't in `id_to_file` before planning.
- **M7 — `build_mvp` hardcodes `n_independent_corroborations=1`**
  (`orchestrate.py:170-173`) → SUPPORTED unreachable (see EFF‑5). *Fix:* accept
  corroboration counts or document the single‑source demo limitation.

### Low
- **L1** — `make_provider` raises bare `KeyError` for a missing API key
  (`providers.py:121,138,157`); use `_ENV_KEY[family]` + a clear `RuntimeError`.
- **L2** — CLI `main()` bodies leak tracebacks on lint rollback
  (`relate.py:409-421`, `resolve.main`, `graph_index.main`); wrap + `sys.exit(1)`.
- **L3** — `concepts.STOPWORDS` lists `any`/`while` twice (`concepts.py:27-30`).
- **L4** — `singularize`'s "shorter strip first" comment over‑promises
  (`concepts.py:63-70`).
- **L5** — Stringly‑typed verdicts duplicated across `ground.py:66`,
  `confidence.py:73`, `orchestrate.py:181-182`, `cli.py:137-140`; an enum would
  make them checkable.
- **L6** — `idf` is 0 when a concept appears in every axiom (`concepts.py:90-93`),
  silently dropping universal concepts from the derived adjacency.

### Test gaps & security
- **T1** — Provider failure modes untested (truncation, multi‑object prose, SDK
  exceptions, retry) — `test_providers.py:42-67` covers only happy paths.
- **T2** — No test that `relate_kpm`/`resolve_kpm` survive a per‑item failure (H4).
- **T3** — No e2e test pinning the `over_claims` counting behavior (M1).
- **T4** — Prompt‑injection boundary unguarded: web text flows verbatim into
  prompts (`gate.py:178`, `ground.py:88`, `relate.py:147`, `resolve.py:245-247`).
- **T5** — No token/call‑budget guardrails despite SKILL.md stressing cost
  discipline; `relate_kpm` can fan out to hundreds of calls.

---

## 4 · Cross‑cutting / packaging / infra

- **INF‑1 — kpm-builder isn't a real package** (kpm-builder H1). Without a
  `pyproject.toml` it works only via PYTHONPATH juggling (see the CI workflow's
  `PYTHONPATH=tools/kpm-builder:tools/package-research/src`). Add packaging so
  `pip install -e tools/kpm-builder` is self‑sufficient.
- **INF‑2 — The "single‑source linter" is a silent copy, not a symlink.**
  `scripts/doctrine_lint.py` and
  `tools/package-research/src/package_research/vendor/doctrine_lint.py` are two
  regular files (git mode `100644`, currently identical blob) — BACKLOG.md claims
  a symlink. Nothing enforces they stay in sync; the canonical one can drift from
  the vendored one silently. *Fix:* make the vendored path a real symlink (git
  supports mode `120000`) **or** add a CI step asserting the two are byte‑identical.
- **INF‑3 — The LLM seam is duplicated and has already diverged.** Both tools
  implement the same `complete_json(prompt, schema) -> dict` seam
  (`package_research/llm.py` vs `kpm_builder/providers.py`) with *different*
  `max_tokens`, JSON‑extraction, and retry behavior — so H‑level bugs must be
  fixed twice. Since kpm-builder already hard‑depends on package_research, extract
  the shared seam (provider factory + JSON extraction + retry/backoff) into one
  module both import.
- **INF‑4 — Stale default model.** `config.py:33` and `llm.py:61` default to
  `claude-sonnet-4-5`; bump to the current Sonnet.
- **CI** — `.github/workflows/kpm-builder-tests.yml` already runs the lint, both
  test suites, and self‑validates the doctrine. Good baseline; add the INF‑2
  drift‑check here.

---

## 5 · Recommended order of work

1. **Doctrine fidelity (EFF‑1, EFF‑2, EFF‑3, EFF‑4)** — the tools' reason to
   exist. Populate inter‑axiom relations in package-research, promote survivors to
   `locked`/`provisional`, scope evidence to passages in kpm-builder, and emit
   `cluster:` pointers. Tighten the lint to *require* (or at least warn on) what
   these produce, so the standard and the tools advance together.
2. **LLM robustness (PR‑H1/H2/H3/H4, KPM‑H2/H3/H4)** — batch the distill call,
   real retry/backoff, robust JSON parsing, partial‑failure isolation, prompt
   isolation of untrusted content. Do this in the **shared seam (INF‑3)** so it's
   fixed once.
3. **Packaging/infra (INF‑1, INF‑2, INF‑4)** — make kpm-builder installable, kill
   the linter‑drift risk, bump the model default.
4. **Cleanups (the M/L items and test gaps)** — unify the clamp helpers, add the
   `llm.py`/provider failure‑mode tests, stale‑output handling, CLI flag parity.
