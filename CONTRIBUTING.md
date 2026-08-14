# Contributing

EvidencePilot AI is currently developed as a focused portfolio project. Issues and pull requests are welcome when they preserve the evidence-first design.

## Development workflow

1. Create a focused branch from `main`.
2. Copy `.env.example` to `.env` without adding secrets.
3. Install dependencies with `make install`.
4. Run `make lint`, `make test`, and `make build`.
5. Explain behavioral and architectural changes in the pull request.

## Pull request expectations

- Include tests for new behavior.
- Preserve typed API contracts.
- Document new providers and environment variables.
- Describe citation, data-access, and agent-budget implications.
- Keep unrelated changes out of the pull request.
