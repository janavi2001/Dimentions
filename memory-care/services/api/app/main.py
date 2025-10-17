from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import settings
from .core.logging import setup_logging

from .routes.identify import router as identify_router
from .routes.register import router as register_router
from .routes.ingest import router as ingest_router
from .routes.ask import router as ask_router
from .routes.health import router as health_router
from .routes.faces import router as faces_router          # <-- add
from .routes.feedback import router as feedback_router    # <-- add

setup_logging()
app = FastAPI(title="Memory Care API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identify_router, prefix="/api")
app.include_router(register_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")
app.include_router(ask_router, prefix="/api")
app.include_router(faces_router, prefix="/api")          # <-- add
app.include_router(feedback_router, prefix="/api")       # <-- add
app.include_router(health_router, prefix="")
