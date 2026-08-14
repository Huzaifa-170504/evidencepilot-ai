# EvidencePilot AI Repository Guidance

## Scope

- Preserve the evidence-first product direction in `PROJECT_REQUIREMENTS.md`.
- Keep the frontend provider-agnostic and keep secrets in backend environment variables only.
- Every generated claim must eventually map to a stored source or be labelled unsupported.

## Engineering Rules

- Add or update tests with behavioral changes.
- Use typed request and response contracts across API boundaries.
- Keep demo behavior deterministic so CI and recruiter previews remain reproducible.
- Never commit API keys, uploaded user documents, private reports, or production data.
- Do not expose unrestricted SQL, filesystem, shell, or external write actions to an agent.

## Code Review Rules

- Flag any path that can manufacture a citation rather than resolving it from stored evidence.
- Flag frontend access to service-role keys or provider secrets.
- Flag agent loops without explicit budgets, timeouts, and stop conditions.
