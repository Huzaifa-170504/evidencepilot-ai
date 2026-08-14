# Security model

- No provider or service-role secrets in frontend code or Git history.
- Supabase Auth validates protected API calls; RLS independently enforces ownership.
- Private PDF Storage with user/project path policies and PDF-only limits.
- Magic-byte, MIME, size, page, encryption, checksum, and parser validation.
- Retrieved evidence is untrusted and cannot override agent policy.
- No unrestricted SQL, shell, filesystem, arbitrary URL fetch, or write-capable MCP tool.
- CORS allowlist, public quota, bounded retries, and safe event summaries.
- User-controlled project, document, and memory deletion.

Supabase's security advisor returned no findings after the hardening migration.
