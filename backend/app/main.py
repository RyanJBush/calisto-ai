from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import Base, SessionLocal, engine
import app.models  # noqa: F401
from app.routers import auth, chat, documents, health
from app.services.auth_service import ensure_demo_seed_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_demo_seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix=settings.api_prefix, tags=["auth"])
app.include_router(documents.router, prefix=settings.api_prefix, tags=["documents"])
app.include_router(chat.router, prefix=settings.api_prefix, tags=["chat"])
