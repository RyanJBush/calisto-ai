# Contributing to Calisto AI

Thank you for your interest in contributing.

## Development workflow

1. Fork and clone the repository.
2. Create a feature branch from `main`.
3. Run `make bootstrap`.
4. Run quality checks with `make lint && make test`.
5. Open a pull request with context, screenshots (if UI changes), and test output.

## Commit conventions

Use clear, imperative commit messages:

- `feat(backend): add tenant-aware document ingestion`
- `fix(frontend): handle expired sessions`
- `docs: update architecture decision record`

## Code quality expectations

- Backend: type hints, pytest coverage for core behavior, ruff-clean.
- Frontend: linted with ESLint, formatted with Prettier.
- Keep business logic in service modules and keep route handlers thin.

## Security notes

- Never commit real credentials.
- Treat uploaded customer documents as sensitive data.
- Follow least privilege for service roles and API tokens.
