from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.logging import configure_logging, log_requests
from app.core.metrics import metrics_store
from app.core.rate_limit import InMemoryRateLimiter
from app.db.seed import seed_demo_data
from app.db.session import SessionLocal, init_db
from app.routers import admin, auth, chat, documents, health, search

settings = get_settings()
configure_logging()
rate_limiter = InMemoryRateLimiter(limit_per_minute=settings.rate_limit_per_minute)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
        yield
    finally:
        db.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    rate_limit_key = request.headers.get("authorization") or (request.client.host if request.client else "anonymous")
    if not rate_limiter.is_allowed(rate_limit_key):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please retry in a minute."})

    metrics_store.increment()
    return await log_requests(request, call_next)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(search.router)
