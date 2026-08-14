# Development Guide

## Commands

| Command | Result |
|---|---|
| `make install` | Install Python and Node dependencies |
| `make dev` | Run API and web development servers |
| `make api` | Run only FastAPI |
| `make web` | Run only Vite |
| `make lint` | Run Ruff and ESLint |
| `make test` | Run pytest and Vitest |
| `make build` | Create the production frontend bundle |

## Configuration

Copy `.env.example` to `.env`. The cached recruiter demo needs only `VITE_API_BASE_URL`, `FRONTEND_ORIGINS`, and `DEMO_MODE`. Supabase public values enable Auth/uploads; backend-only provider keys enable live model and web research.

## Design principle

The deterministic provider is a production fallback and contract test double. Live orchestration satisfies the same response schema, so the interface and evaluation harness do not depend on one LLM or provider.
