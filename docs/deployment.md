# Deployment guide

EvidencePilot AI is deployed as three cooperating services:

- GitHub Pages: <https://huzaifa-170504.github.io/evidencepilot-ai/>
- Render API: <https://evidencepilot-ai.onrender.com>
- Supabase: project `dsbxndbbpryisxevjjgc`

## GitHub Pages

The `pages.yml` workflow builds `apps/web` with the repository base path and publishes `apps/web/dist`. Production-safe defaults connect the build to the Render API and the public Supabase project. Repository variables with the same names may override these defaults for forks:

- `VITE_API_BASE_URL`
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`

Only the Supabase publishable key may be used in a `VITE_*` variable.

## Render

The backend uses `apps/api/Dockerfile` and `render.yaml`. Required production values:

- `APP_ENV=production`
- `DEMO_MODE=true`
- `FRONTEND_ORIGINS=https://huzaifa-170504.github.io`
- `SUPABASE_URL=https://dsbxndbbpryisxevjjgc.supabase.co`
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `LLM_PROVIDER=deterministic`
- `EMBEDDING_PROVIDER=hashing`

Keep `LIVE_RESEARCH_ENABLED=false` for the released deterministic demo. Gemini and Tavily keys are optional backend-only values.

## Supabase Auth

Set the site URL to the GitHub Pages URL and add both the Pages URL and `http://localhost:5173` to allowed redirect URLs. The `research-documents` bucket must remain private.

## Verification

The `Deployment smoke test` workflow automatically runs after a successful Pages deployment and weekly. It verifies:

- frontend HTTP response and repository base path;
- Render health and CORS;
- readiness with Supabase storage;
- demo sources, claims, and report;
- Swagger UI.

Manual endpoints:

- <https://evidencepilot-ai.onrender.com/>
- <https://evidencepilot-ai.onrender.com/health>
- <https://evidencepilot-ai.onrender.com/ready>
- <https://evidencepilot-ai.onrender.com/docs>
