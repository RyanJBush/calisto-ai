# Engineering Style Guide

## General principles

- Prioritize readability and maintainability over cleverness.
- Keep HTTP handlers thin and move logic into services.
- Prefer explicit typing and clear naming.
- Use small, composable modules.

## Backend conventions

- Python 3.11+
- Lint with Ruff
- Test with Pytest
- Group by domain (`routers`, `services`, `schemas`, `models`)
- Use dependency injection for database/session access

## Frontend conventions

- React function components
- Route-centric pages under `src/pages`
- Shared layout components under `src/components/layout`
- Tailwind utility-first styling
- Lint with ESLint and format with Prettier

## Git and PR hygiene

- Small focused commits
- Include test/lint output in PR description
- Link architecture changes in `docs/ARCHITECTURE.md`
