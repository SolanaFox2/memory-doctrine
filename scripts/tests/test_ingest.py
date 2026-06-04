import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ingest_doctrine_to_kg as ing

AX = {
    "id": "B1-spreading-activation", "type": "axiom", "cluster": "B-retrieval",
    "title": "Spreading activation is Hopfield is attention",
    "statement": "Retrieval is energy-descent pattern completion.",
    "confidence": 0.95, "generativity": 5, "status": "locked",
    "relations": {"supports": ["B4-index-store-split"], "derives-from": ["A1-fan-budgeted-edges"],
                  "applies-to-kpm": ["recall-mechanism"]},
    "provenance": "2026-06-03-memory-semantic-networks",
}

def test_maps_axiom_to_entity_schema():
    ent = ing.axiom_to_entity(AX)
    assert ent["id"] == "doctrine-B1-spreading-activation"
    assert ent["type"] == "axiom"
    assert ent["confidence"] == 0.95
    assert ent["name"] == AX["title"]
    assert "memory-doctrine" in ent["tags"]
    assert "doctrine-B4-index-store-split" in ent["relations"]
    assert "doctrine-A1-fan-budgeted-edges" in ent["relations"]

def test_applies_to_kpm_is_not_an_edge():
    # applies-to-kpm values are free tags, NOT entity edges
    ent = ing.axiom_to_entity(AX)
    assert "doctrine-recall-mechanism" not in ent["relations"]

def test_summary_is_the_statement():
    ent = ing.axiom_to_entity(AX)
    assert ent["summary"].startswith("Retrieval is energy-descent")
