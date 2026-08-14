# evidencepilot-research-tools MCP server

This read-only server demonstrates the difference between direct Python tools and MCP. It exposes the same permission-filtered EvidencePilot capabilities through a standardized protocol, without exposing SQL, arbitrary URLs, filesystem access, or external writes.

Set `EVIDENCEPILOT_API_URL` and a short-lived `EVIDENCEPILOT_ACCESS_TOKEN`, then run:

```bash
uv run --directory packages/mcp_server evidencepilot-mcp
```

Available tools:

- `search_project_documents`
- `fetch_source`
- `search_academic_metadata`
- `get_saved_project_findings`
