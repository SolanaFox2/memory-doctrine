"""Deterministic tests for the ingest stage (TDD — written before impl)."""

from pathlib import Path

from package_research.config import Config
from package_research.ingest import Candidate, ingest


def _cfg(notes_dir: Path) -> Config:
    return Config(input_dir=notes_dir, max_chunk_chars=1500)


def _basename(source: str) -> str:
    return Path(source).name


def test_ingest_returns_candidates(notes_dir):
    cands = ingest(_cfg(notes_dir))
    assert cands, "expected at least one candidate"
    assert all(isinstance(c, Candidate) for c in cands)


def test_source_file_is_a_relative_path_string(notes_dir):
    """source_file is a plain relative-path str (not a Path) — pipeline-consistent."""
    cands = ingest(_cfg(notes_dir))
    assert all(isinstance(c.source_file, str) for c in cands)
    # Nested files keep their relative directory in the posix string.
    nested = [c for c in cands if _basename(c.source_file) == "gamma.md"]
    assert nested and nested[0].source_file == "sub/gamma.md"


def test_only_md_and_txt_are_read(notes_dir):
    cands = ingest(_cfg(notes_dir))
    sources = {_basename(c.source_file) for c in cands}
    assert "ignore.pdf" not in sources  # unsupported extension skipped
    assert {"alpha.md", "beta.txt"} <= sources


def test_recurses_into_subdirectories(notes_dir):
    cands = ingest(_cfg(notes_dir))
    sources = {_basename(c.source_file) for c in cands}
    assert "gamma.md" in sources  # nested file discovered


def test_empty_files_produce_no_candidates(notes_dir):
    cands = ingest(_cfg(notes_dir))
    assert all(_basename(c.source_file) != "empty.md" for c in cands)


def test_char_span_maps_back_to_source_text(notes_dir):
    cands = ingest(_cfg(notes_dir))
    for c in cands:
        raw = (notes_dir / c.source_file).read_text(encoding="utf-8")
        start, end = c.char_span
        assert 0 <= start < end <= len(raw)
        # The stored text is a substring of the original at the recorded span.
        assert raw[start:end] == c.text


def test_chunking_splits_alpha_into_two_passages(notes_dir):
    """alpha.md has two '# ' sections → two passages (frontmatter stripped)."""
    cands = ingest(_cfg(notes_dir))
    alpha = [c for c in cands if _basename(c.source_file) == "alpha.md"]
    assert len(alpha) == 2
    joined = " ".join(c.text for c in alpha)
    assert "Spreading activation" in joined
    assert "Index/store split" in joined
    # YAML frontmatter must not leak into passages.
    assert "title: Alpha note" not in joined


def test_long_passage_respects_max_chunk_chars():
    """A single huge section is split so no chunk exceeds the char cap."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        big = Path(d) / "big.md"
        # One section, many sentences, no extra headings.
        body = "# Big\n\n" + ("This is a sentence. " * 400)
        big.write_text(body, encoding="utf-8")
        cands = ingest(Config(input_dir=Path(d), max_chunk_chars=300))
        assert len(cands) > 1
        assert all(len(c.text) <= 300 for c in cands)


def test_deterministic_across_runs(notes_dir):
    a = ingest(_cfg(notes_dir))
    b = ingest(_cfg(notes_dir))
    assert [(c.source_file, c.char_span, c.text) for c in a] == [(c.source_file, c.char_span, c.text) for c in b]


# --- store preservation: noise detection + per-source passage map ----------

from package_research.ingest import (  # noqa: E402
    is_noise_passage,
    passage_heading,
    passages_by_source,
)


def test_passage_heading_extracts_lowercased_heading():
    assert passage_heading("## Methodology\n\n- ran 8 searches") == "methodology"
    assert passage_heading("###  Follow-Up Searches  \nfoo") == "follow-up searches"
    # No leading heading -> empty (a cap-split tail or preamble).
    assert passage_heading("just some prose with no heading") == ""


def test_is_noise_passage_flags_process_sections():
    assert is_noise_passage("## Methodology\n\n- Agents deployed: 1")
    assert is_noise_passage("## Follow-Up Searches\n\n- 'mem0 vs letta'")
    assert is_noise_passage("## Tool Failure Report\n\n| Tool | Status |")
    # Substantive sections are KEPT (conservative default).
    assert not is_noise_passage("## Evidence Table\n\n| Claim | Source |")
    assert not is_noise_passage("## Findings\n\nBenchmarks: LoCoMo, BEAM")
    assert not is_noise_passage("prose with no heading is never noise")


def test_passages_by_source_keys_by_relative_path_and_dedupes():
    cands = [
        Candidate(text="## Findings\n\nLoCoMo and BEAM", source_file="a/notes.md", char_span=(0, 1)),
        Candidate(
            text="## Findings\n\nLoCoMo and BEAM", source_file="a/notes.md", char_span=(2, 3)
        ),  # exact dup, same file
        Candidate(text="## Methodology\n\nran searches", source_file="a/notes.md", char_span=(4, 5)),
        Candidate(text="## Scores\n\nMem0 91.6", source_file="a/notes.md", char_span=(6, 7)),
    ]
    grouped = passages_by_source(cands)
    # Keyed by relative path; methodology dropped; exact-duplicate removed.
    assert set(grouped) == {"a/notes.md"}
    bodies = grouped["a/notes.md"]
    assert any("Mem0 91.6" in b for b in bodies)
    assert not any("Methodology" in b for b in bodies)
    assert sum("LoCoMo and BEAM" in b for b in bodies) == 1  # deduped


def test_passages_by_source_does_not_merge_same_basename_different_dirs():
    # Distinct files sharing a basename must NOT merge (silent corruption guard).
    cands = [
        Candidate(text="## A\n\nfrom 2025", source_file="2025/notes.md", char_span=(0, 1)),
        Candidate(text="## A\n\nfrom 2026", source_file="2026/notes.md", char_span=(2, 3)),
    ]
    grouped = passages_by_source(cands)
    assert set(grouped) == {"2025/notes.md", "2026/notes.md"}
    assert "from 2025" in grouped["2025/notes.md"][0]
    assert "from 2026" in grouped["2026/notes.md"][0]


# --- path safety, caps, and skip paths (REVIEW.md M5/M6/L2/L7) -------------


def test_symlink_outside_input_dir_is_skipped_with_warning(tmp_path, capsys):
    """REVIEW.md M5: a symlink escaping the input tree must not be ingested."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text("# Secret\n\nleaked content", encoding="utf-8")
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "real.md").write_text("# Real\n\nkept content", encoding="utf-8")
    (notes / "leak.md").symlink_to(outside / "secret.md")

    cands = ingest(Config(input_dir=notes))
    sources = {c.source_file for c in cands}
    assert sources == {"real.md"}
    assert not any("leaked content" in c.text for c in cands)
    err = capsys.readouterr().err
    assert "symlink" in err and "leak.md" in err


def test_symlink_inside_input_dir_is_kept(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "real.md").write_text("# Real\n\ncontent", encoding="utf-8")
    (notes / "alias.md").symlink_to(notes / "real.md")
    cands = ingest(Config(input_dir=notes))
    assert {"real.md", "alias.md"} == {c.source_file for c in cands}


def test_relative_source_never_emits_an_absolute_path(tmp_path):
    """REVIEW.md M5: the fallback locator is the basename, never an abs path."""
    from package_research.ingest import _relative_source

    foreign = tmp_path / "elsewhere" / "note.md"
    assert _relative_source(foreign, tmp_path / "notes") == "note.md"
    assert _relative_source(tmp_path / "notes" / "a" / "b.md", tmp_path / "notes") == "a/b.md"


def test_max_sources_truncation_warns_with_count(tmp_path, capsys):
    """REVIEW.md M6: truncation must say how many files were dropped."""
    for name in ("a.md", "b.md", "c.md"):
        (tmp_path / name).write_text(f"# {name}\n\ncontent of {name}", encoding="utf-8")
    cands = ingest(Config(input_dir=tmp_path, max_sources=2))
    assert {c.source_file for c in cands} == {"a.md", "b.md"}  # alphabetical
    err = capsys.readouterr().err
    assert "3 source files found" in err
    assert "1 file(s) skipped" in err


def test_no_truncation_no_warning(tmp_path, capsys):
    (tmp_path / "a.md").write_text("# A\n\ncontent", encoding="utf-8")
    ingest(Config(input_dir=tmp_path, max_sources=2))
    assert "skipped" not in capsys.readouterr().err


def test_zero_sources_warns_to_stderr(tmp_path, capsys):
    """REVIEW.md L2: an empty corpus must be distinguishable from "all refuted"."""
    assert ingest(Config(input_dir=tmp_path)) == []
    err = capsys.readouterr().err
    assert "no .md/.txt source files" in err


def test_non_utf8_source_is_skipped_with_warning(tmp_path, capsys):
    """REVIEW.md L7: one undecodable note must not abort the run — skip loudly."""
    (tmp_path / "bad.md").write_bytes(b"# Bad\n\xff\xfe broken bytes")
    (tmp_path / "good.md").write_text("# Good\n\nfine content", encoding="utf-8")
    cands = ingest(Config(input_dir=tmp_path))
    assert {c.source_file for c in cands} == {"good.md"}
    err = capsys.readouterr().err
    assert "bad.md" in err and "UTF-8" in err


def test_passages_by_source_can_keep_noise_when_asked():
    cands = [Candidate(text="## Methodology\n\nx", source_file="n.md", char_span=(0, 1))]
    assert passages_by_source(cands, drop_noise=False)["n.md"]
    assert passages_by_source(cands, drop_noise=True) == {}


def test_long_noise_section_does_not_leak_via_cap_split():
    """A process section longer than the cap must be trimmed in FULL — its
    headingless cap-split tails must not leak into the store (reviewer Critical)."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "n.md"
        f.write_text(
            "# Title\n\nKeep this LoCoMo finding.\n\n## Methodology\n\n" + ("ran searches ABCDEF. " * 200),
            encoding="utf-8",
        )
        cands = ingest(Config(input_dir=Path(d), max_chunk_chars=200))
        # The methodology section is large enough to cap-split into many chunks.
        meth = [c for c in cands if c.section_heading == "methodology"]
        assert len(meth) > 1, "expected the noise section to cap-split into tails"
        grouped = passages_by_source(cands)
        joined = "\n".join(grouped.get("n.md", []))
        assert "LoCoMo finding" in joined  # finding kept
        assert "ran searches" not in joined  # ALL methodology trimmed, tails too
