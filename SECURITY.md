# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| latest (`main`) | ✅ |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report them via email to **ryanjbush@gmail.com** with the subject line `[SECURITY] Calisto AI — <brief description>`.

Include:
- A description of the vulnerability and its potential impact
- Steps to reproduce
- Any suggested remediation if known

You can expect an acknowledgement within **48 hours** and a resolution timeline within **7 days** for critical issues.

## Tenant Isolation

This platform implements RBAC-based tenant isolation. If you discover a cross-tenant data leakage vulnerability (a tenant being able to access another tenant’s documents or queries), treat this as a **critical** issue and disclose immediately via the contact above.

## API Key Safety

This project uses LLM API keys and embedding service credentials. **Never commit API keys to this repository.** Use `.env` files excluded via `.gitignore`. If a key has been accidentally committed, rotate it immediately.

## Scope

This project is a portfolio/demonstration platform and is not deployed as a public service.
