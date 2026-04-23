# Calisto AI Demo Runbook

## 1) Setup

```bash
make bootstrap
cp backend/.env.example backend/.env
make db-upgrade
make init
make demo-seed
```

## 2) Start Services

```bash
make run-backend
make run-frontend
```

## 3) Demo Accounts

- admin@calisto.ai / password123
- member@calisto.ai / password123
- viewer@calisto.ai / password123

## 4) Recommended Demo Flow

1. Login as **member** and upload a small text file in Documents.
2. Open Chat and ask: "How does Calisto establish answer trust?"
3. Show citations, answer mode, confidence, and source preview.
4. Login as **admin**, open Settings, and show workspace + audit filtering.
5. Grant viewer access to a document from Documents page.
6. Login as **viewer** and verify restricted document visibility behavior.

## 5) Smoke Validation

```bash
make smoke
```
