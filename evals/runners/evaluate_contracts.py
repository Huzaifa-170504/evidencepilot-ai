from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.schemas import ResearchRequest  # noqa: E402
from app.services.research_graph import execute_research  # noqa: E402


def main() -> int:
    dataset = json.loads((ROOT / "evals" / "datasets" / "research_questions.json").read_text())
    citation_errors = 0
    routing_errors = 0
    for item in dataset:
        run = execute_research(
            ResearchRequest(
                question=item["question"],
                has_documents=item["documents"],
                needs_data_analysis=item["data_analysis"],
            )
        )
        source_ids = {source.id for source in run.sources}
        citation_errors += sum(
            source_id not in source_ids for claim in run.claims for source_id in claim.source_ids
        )
        routing_errors += ("Document Research" in run.selected_agents) != item["documents"]
        routing_errors += ("Data Analyst" in run.selected_agents) != item["data_analysis"]
    print(
        json.dumps(
            {
                "questions": len(dataset),
                "fabricated_citation_ids": citation_errors,
                "routing_errors": routing_errors,
            },
            indent=2,
        )
    )
    return int(bool(citation_errors or routing_errors))


if __name__ == "__main__":
    raise SystemExit(main())
