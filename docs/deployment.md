# Deployment guide

1. Merge the validated PR to `main`.
2. Add GitHub variables `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, and `VITE_SUPABASE_PUBLISHABLE_KEY`.
3. Set Pages source to GitHub Actions.
4. Create a Render Blueprint from `render.yaml` and add backend-only secrets.
5. Point `VITE_API_BASE_URL` to Render.
6. Add the Pages origin to Render `FRONTEND_ORIGINS` and Supabase Auth URL configuration.
7. Keep `LIVE_RESEARCH_ENABLED=false` until Gemini/Tavily keys are configured and tested.
8. Verify health, OpenAPI, Auth, private upload, ingestion, research, citations, and exports.
