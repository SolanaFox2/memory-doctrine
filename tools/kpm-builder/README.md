# KPM Builder — `/kpm-build`

Research a topic **from scratch** into a doctrine-conformant knowledge package (KPM): scope it
once, and the skill dispatches research subagents, grounds every claim against its source with an
independent isolated check, scores confidence from evidence, relates the axioms into a web,
resolves contradictions, and assembles a labeled package — honestly reporting what it answered,
what's thin, and what it couldn't reach. Runs on a Claude subscription alone; an optional
DeepSeek/Gemini key upgrades grounding to cross-family.

**This is the Builder.** The companion **Organizer** (`tools/package-research`) packages notes you
*already have*; the Builder researches from scratch. The Builder depends on the Organizer.

## Install
```bash
git clone https://github.com/Treibs/memory-doctrine && cd memory-doctrine
python3 -m venv .venv && source .venv/bin/activate        # recommended (avoids PEP 668 on Debian/Homebrew)
pip install -r tools/kpm-builder/requirements.txt         # pyyaml, pydantic
pip install -e tools/package-research                      # the Organizer (the Builder imports package_research)
export PYTHONPATH=tools/kpm-builder:tools/package-research/src
# optional cross-family grounding: pip install anthropic   # then: export DEEPSEEK_API_KEY=…  (or GOOGLE_GENAI_API_KEY)
```
Python 3.10+. Paths are repo-relative — run from the repo root.

## Use
Invoke the `/kpm-build` skill and give it a goal. It walks you through a short Scope Contract
(the one upfront step), then runs the autonomous build (research → ground → confidence → relate →
graph → resolve → assemble) and delivers the package with an honest coverage label.

## Example
See `examples/raft-thesis-kpm/` (and its `ABOUT.md`) — a 150-axiom thesis-depth package built
from public sources.

## Cost & autonomy
A standard build is many subagents over several beats (~0.5–1.5M tokens; minutes to tens of
minutes). The human is in exactly two places: the scope intake and reading the result.

## License
Code: see `LICENSE`. The Memory Doctrine corpus has its own license at the repo root.
