# Deployment Notes

## Local Production-like Compose

```bash
docker compose up --build
```

## Required Environment Variables

- `DATABASE_URL`
- `JWT_SECRET` (must not be default in production)
- `CORS_ORIGINS`
- `LLM_PROVIDER`
- `LLM_MODEL`

## Pre-deploy Checklist

1. Run `make lint`
2. Run `make test`
3. Run `make smoke`
4. Confirm migrations applied (`make db-upgrade`)
5. Verify admin and member login in target environment
