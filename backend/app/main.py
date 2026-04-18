from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging import configure_logging, log_requests
from app.core.metrics import metrics_store
from app.db.seed import seed_demo_data
from app.db.session import SessionLocal, init_db
from app.routers import auth, chat, documents, health

settings = get_settings()
configure_logging()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    metrics_store.increment()
    return await log_requests(request, call_next)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
