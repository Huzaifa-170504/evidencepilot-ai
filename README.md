# EvidencePilot AI

> Evidence-first research by coordinated AI agents.

[![CI](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/ci.yml)
[![Security](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/security.yml/badge.svg)](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/security.yml)
[![Pages](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/pages.yml/badge.svg)](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/pages.yml)
[![Deployment smoke test](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/deployment-smoke.yml/badge.svg)](https://github.com/Huzaifa-170504/evidencepilot-ai/actions/workflows/deployment-smoke.yml)

EvidencePilot AI is an agentic research intelligence platform built by **Huzaifa Waqar Butt**. It turns a question and optional private PDFs into a traceable technical report using conditional LangGraph agents, function tools, MCP, hybrid PDF RAG, pgvector, memory, criticism, claim verification, and a professional recruiter-facing dashboard.

## Live project

- Dashboard: <https://huzaifa-170504.github.io/evidencepilot-ai/>
- API home: <https://evidencepilot-ai.onrender.com/>
- Health: <https://evidencepilot-ai.onrender.com/health>
- Swagger / OpenAPI: <https://evidencepilot-ai.onrender.com/docs>

The Render free service can take approximately one minute to wake. The browser keeps a clearly labelled cached Mamba-YOLO snapshot available during a cold start.

## What it demonstrates

- Supervisor, Academic, Web, Document, Data Analyst, Critic, Fact Checker, and Report contracts
- Conditional orchestration with fixed budgets and safe event traces
- Supabase Auth, PostgreSQL, private Storage, Realtime, pgvector, and hardened RLS
- PDF signature/page/encryption/checksum validation with page-aware PyMuPDF parsing
- PostgreSQL full-text search + pgvector cosine search + reciprocal-rank fusion
- Stable source IDs, page citations, claim verdicts, limitations, and exports
- arXiv and Crossref tool adapters, optional Gemini/Tavily provider seams, and a deterministic free release
- Read-only `evidencepilot-research-tools` MCP server
- 25-question evaluation dataset, 90%+ backend coverage, CI/CD, Pages, and Render descriptors

## User flow

```mermaid
flowchart TD
    Project["Create project"] --> Upload["Optional private PDFs"]
    Upload --> Question["Ask scoped question"]
    Question --> Plan["Review supervisor plan"]
    Plan --> Agents["Watch conditional agents"]
    Agents --> Verify["Inspect sources and claims"]
    Verify --> Export["Export Markdown or PDF"]
```

The cached Mamba-YOLO workspace works without an account or provider key. The production build is connected to Render and the public Supabase project; authenticated users can create persistent projects and upload private PDFs.

## Architecture

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Supabase JS |
| API | Python 3.12, FastAPI, Pydantic |
| Orchestration | LangGraph |
| Data | Supabase PostgreSQL, Auth, Storage, Realtime, pgvector |
| RAG | PyMuPDF, pypdf, hashing/Gemini embeddings, FTS + vector RRF |
| Tools | Tavily, arXiv, Crossref, MCP |
| Hosting | GitHub Pages + Render Blueprint |
| Quality | pytest, Ruff, Vitest, ESLint, GitHub Actions |

## Quick start

Prerequisites: Python 3.12+, Node.js 20+, npm 10+, and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Huzaifa-170504/evidencepilot-ai.git
cd evidencepilot-ai
cp .env.example .env
make install
make dev
```

Open:

- Dashboard: <http://localhost:5173>
- API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

The cached demo requires no key. Local Auth and PDF uploads require the Supabase URL/publishable key in `.env`. Never expose `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY`, `TAVILY_API_KEY`, or `DATABASE_URL` in a `VITE_*` variable.

## Validate

```bash
make lint
make test
make build
uv run --directory apps/api python ../../evals/runners/evaluate_contracts.py
```

Current deterministic contract baseline:

- 25 evaluation questions
- Zero fabricated source identifiers
- Correct Document/Data Analyst routing
- Critic and Fact Checker included before full reports
- Supabase security advisor: no findings

## Repository map

```text
apps/web/                 React dashboard
apps/api/                 FastAPI, LangGraph, RAG, providers, tests
packages/mcp_server/      Read-only MCP server
packages/*/               Extractable package boundaries
supabase/migrations/      Schema, pgvector, RLS, Storage, hardening
supabase/seed/            Public recruiter seed
evals/                    Dataset, runner, baseline result
scripts/                  Public deployment smoke verification
docs/                     Architecture, RAG, database, security, deployment
render.yaml               Render Blueprint
.github/workflows/        CI, security, Pages, deployment smoke test
```

## Deployment status

GitHub Pages, the Render API, and Supabase project `dsbxndbbpryisxevjjgc` are provisioned. The database contains 16 application tables with RLS enabled on all 16, pgvector, a private PDF bucket, Realtime publication, and hardened policies. The Supabase security advisor reports no findings.

Production-safe frontend defaults contain only public identifiers and may be overridden with GitHub repository variables for forks. Backend secrets remain in Render.

The released public research graph is deterministic for stable, zero-cost recruiter testing. Gemini/Tavily adapters are extension seams and should not be described as active live research until separately integrated and evaluated.

## Documentation

- [Final technical documentation](FINAL_DOCUMENTATION.md)
- [Product requirements](PROJECT_REQUIREMENTS.md)
- [Architecture](docs/architecture.md)
- [Agent contracts](docs/agent-contracts.md)
- [RAG design](docs/rag-design.md)
- [Database and RLS](docs/database.md)
- [Security](docs/security.md)
- [Deployment](docs/deployment.md)
- [Recruiter demo](docs/demo-guide.md)
- [Changelog](CHANGELOG.md)

## Security and privacy

Upload only public or non-sensitive documents to the demo. Retrieved PDFs and webpages are untrusted evidence, not agent instructions. The system stores concise events and rationale summaries rather than private chain-of-thought. See [SECURITY.md](SECURITY.md) for reporting guidance.

## License

MIT - see [LICENSE](LICENSE).
