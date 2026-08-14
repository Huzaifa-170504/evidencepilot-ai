from __future__ import annotations

import json
from pathlib import Path


def test_evaluation_dataset_has_25_unique_questions() -> None:
    root = Path(__file__).resolve().parents[3]
    dataset = json.loads((root / "evals" / "datasets" / "research_questions.json").read_text())
    assert len(dataset) == 25
    assert len({item["id"] for item in dataset}) == 25
    assert {item["category"] for item in dataset} >= {
        "document",
        "web",
        "academic",
        "conflict",
        "insufficient",
        "routing",
        "security",
    }
