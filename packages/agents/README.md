# Agents package boundary

The executable LangGraph workflow currently lives in `apps/api/app/services/research_graph.py` so the deployable API remains a single Python package. This directory documents the extraction boundary for a future independently versioned agents package: typed state, node contracts, prompts, budgets, and routing policies.
