# Style Guide

## Backend (Python)

- Follow PEP 8 and Ruff defaults
- Prefer explicit typing in service and schema layers
- Keep routers thin; business logic belongs in services

## Frontend (React)

- Component-first structure with pages + shared UI components
- Use consistent utility class ordering with Tailwind
- Keep API integrations in `src/services` and avoid direct fetch logic in page components

## General

- Use professional, descriptive names
- Keep comments minimal and only where they add value
- Maintain clear separation of concerns across modules
