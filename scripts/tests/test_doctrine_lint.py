import subprocess
import sys
import textwrap
from pathlib import Path

LINT = Path(__file__).resolve().parents[1] / "doctrine_lint.py"

GOOD_CLUSTER = """\
    ---
    id: B-retrieval
    type: cluster
    title: B · Retrieval
    ---
    Cluster note.
    """


def _pkg(tmp_path, axioms=None, evidence=None, clusters=None):
    (tmp_path / "axioms").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "clusters").mkdir()
    for name, body in (clusters or {"B-retrieval": GOOD_CLUSTER}).items():
        (tmp_path / "clusters" / f"{name}.md").write_text(textwrap.dedent(body))
    for name, body in (axioms or {}).items():
        (tmp_path / "axioms" / f"{name}.md").write_text(textwrap.dedent(body))
    for name, body in (evidence or {}).items():
        (tmp_path / "evidence" / f"{name}.md").write_text(textwrap.dedent(body))
    return tmp_path


GOOD_AX = """\
    ---
    id: B1-x
    type: axiom
    cluster: B-retrieval
    title: t
    statement: s
    domain: d
    generativity: 5
    confidence: 0.9
    status: locked
    relations: {derives-from: [], supports: [], generalizes: [], contradicts: [], applies-to-kpm: []}
    evidence: [src-1]
    provenance: p
    verification: {challenged: true, citations_checked: true, gate: g}
    ---
    Body cites [[src-1]].
    """
GOOD_EV = """\
    ---
    id: src-1
    type: evidence
    ref: r
    url: https://example.com
    verified: 2026-06-03
    supports: [B1-x]
    proves: p
    limits: l
    ---
    Note.
    """


def run(pkg):
    return subprocess.run([sys.executable, str(LINT), str(pkg)], capture_output=True, text=True)


def test_clean_package_passes(tmp_path):
    pkg = _pkg(tmp_path, {"B1-x": GOOD_AX}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 0, r.stdout + r.stderr


def test_confidence_out_of_range_fails(tmp_path):
    bad = GOOD_AX.replace("confidence: 0.9", "confidence: 1.7")
    pkg = _pkg(tmp_path, {"B1-x": bad}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "confidence" in r.stdout


def test_missing_evidence_fails(tmp_path):
    bad = GOOD_AX.replace("evidence: [src-1]", "evidence: []")
    pkg = _pkg(tmp_path, {"B1-x": bad}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "evidence" in r.stdout


def test_dangling_relation_fails(tmp_path):
    bad = GOOD_AX.replace("supports: []", "supports: [does-not-exist]")
    pkg = _pkg(tmp_path, {"B1-x": bad}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "does-not-exist" in r.stdout


def test_relation_not_wikilinked_fails(tmp_path):
    other = GOOD_AX.replace("id: B1-x", "id: B-other")
    bad = GOOD_AX.replace("supports: []", "supports: [B-other]")
    pkg = _pkg(tmp_path, {"B1-x": bad, "B-other": other}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "wikilink" in r.stdout.lower()


def test_contradicts_among_locked_fails_F2(tmp_path):
    other = GOOD_AX.replace("id: B1-x", "id: B-other")
    bad = GOOD_AX.replace("contradicts: []", "contradicts: [B-other]").replace(
        "Body cites [[src-1]].", "Body cites [[src-1]] vs [[B-other]]."
    )
    pkg = _pkg(tmp_path, {"B1-x": bad, "B-other": other}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "F2" in r.stdout


def test_evidence_missing_url_fails(tmp_path):
    bad_ev = GOOD_EV.replace("url: https://example.com\n", "")
    pkg = _pkg(tmp_path, {"B1-x": GOOD_AX}, {"src-1": bad_ev})
    r = run(pkg)
    assert r.returncode == 1 and "url" in r.stdout


def test_evidence_missing_verified_fails(tmp_path):
    bad_ev = GOOD_EV.replace("verified: 2026-06-03\n", "")
    pkg = _pkg(tmp_path, {"B1-x": GOOD_AX}, {"src-1": bad_ev})
    r = run(pkg)
    assert r.returncode == 1 and "verified" in r.stdout


def test_unknown_cluster_fails(tmp_path):
    bad = GOOD_AX.replace("cluster: B-retrieval", "cluster: Z-nonexistent")
    pkg = _pkg(tmp_path, {"B1-x": bad}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "cluster" in r.stdout and "Z-nonexistent" in r.stdout


def test_missing_cluster_passes(tmp_path):
    # cluster is optional in the general standard (tool-built KPMs may be flat);
    # only a *declared* cluster that doesn't resolve is an error.
    ok = GOOD_AX.replace("    cluster: B-retrieval\n", "")
    pkg = _pkg(tmp_path, {"B1-x": ok}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 0, r.stdout + r.stderr


def test_bad_status_fails(tmp_path):
    bad = GOOD_AX.replace("status: locked", "status: lokced")
    pkg = _pkg(tmp_path, {"B1-x": bad}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "status" in r.stdout


def test_duplicate_id_fails(tmp_path):
    # Two files, same declared id — the second must not silently overwrite the first.
    dup = GOOD_AX  # both files declare id: B1-x
    pkg = _pkg(tmp_path, {"B1-x": GOOD_AX, "B1-x-copy": dup}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "duplicate id" in r.stdout


def test_malformed_yaml_fails(tmp_path):
    broken = "---\nid: B1-x\ncluster: [unclosed\n---\nBody cites [[src-1]].\n"
    pkg = _pkg(tmp_path, {"B1-x": broken}, {"src-1": GOOD_EV})
    r = run(pkg)
    assert r.returncode == 1 and "YAML parse error" in r.stdout


def test_orphan_evidence_fails(tmp_path):
    # src-2 exists but no axiom cites it.
    orphan = GOOD_EV.replace("id: src-1", "id: src-2").replace("supports: [B1-x]", "supports: []")
    pkg = _pkg(tmp_path, {"B1-x": GOOD_AX}, {"src-1": GOOD_EV, "src-2": orphan})
    r = run(pkg)
    assert r.returncode == 1 and "orphan evidence" in r.stdout
