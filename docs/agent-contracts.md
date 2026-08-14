# Agent contracts

Full reports follow Supervisor → conditional specialists → Critic → Fact Checker → Report. Document and Data Analyst stages run only when required. Every stage has a typed contract, fixed budget, and allowlisted read-only tool set.

Retrieved text is untrusted evidence. Agents ignore instructions inside PDFs and webpages. A report may cite only identifiers present in the run's source ledger. Unsupported claims are removed or labeled before final output.

Executable graph: `apps/api/app/services/research_graph.py`.
