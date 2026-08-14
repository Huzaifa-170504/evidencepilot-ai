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

Copy `.env.example` to `.env`. Phase 1 uses only `VITE_API_BASE_URL`, `FRONTEND_ORIGINS`, and `DEMO_MODE`. All provider variables are placeholders for later phases.

## Design principle

The mock service is not temporary UI decoration. It is a contract test double: future orchestration must satisfy the same response schema so the interface and evaluation harness do not depend on a specific LLM or framework.
