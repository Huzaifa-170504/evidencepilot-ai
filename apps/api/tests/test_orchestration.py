from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.config import Settings
from app.rate_limit import SlidingWindowLimiter
from app.schemas import ResearchRequest
from app.services.providers import DeterministicProvider, get_model_provider
from app.services.research_graph import execute_research


def test_conditional_data_agent_and_citation_integrity() -> None:
    run = execute_research(
        ResearchRequest(
            question="Calculate and compare numeric latency trends for Mamba detectors",
            needs_data_analysis=True,
        )
    )
    assert "Data Analyst" in run.selected_agents
    assert all(
        source_id in {source.id for source in run.sources}
        for claim in run.claims
        for source_id in claim.source_ids
    )
    assert any(
        event.agent == "Data Analyst" and event.status == "completed" for event in run.events
    )


def test_rate_limiter_rejects_second_event() -> None:
    limiter = SlidingWindowLimiter()
    limiter.check("test-key", 1, timedelta(minutes=1))
    with pytest.raises(HTTPException) as exc:
        limiter.check("test-key", 1, timedelta(minutes=1))
    assert exc.value.status_code == 429
    with pytest.raises(HTTPException):
        limiter.check("disabled", 0, timedelta(minutes=1))


def test_deterministic_provider_contract() -> None:
    provider = get_model_provider(Settings())
    assert isinstance(provider, DeterministicProvider)
    result = asyncio.run(provider.generate_json("Plan research", {"question": "Mamba"}))
    assert result["mode"] == "deterministic"
