# Security Policy

## Supported version

Security fixes target the latest `main` branch while the project is pre-1.0.

## Reporting

Do not create a public issue for a suspected vulnerability. Contact the repository owner through the private contact method listed on the owner's GitHub profile and include reproduction steps, impact, and affected paths.

## Security boundaries

- No provider secret belongs in the browser or repository.
- Uploaded documents and retrieved webpages are untrusted content.
- Agent tools must be allowlisted, schema-validated, bounded, and logged.
- Citations must resolve to stored evidence records.
- Public demo data must not contain confidential information.
