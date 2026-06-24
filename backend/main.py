from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import upload, simulate, explain
from app.core.config import settings

app = FastAPI(
    title="Financial Simulation Dashboard API",
    version="1.0.0",
    description="Parses Excel financial models, runs what-if simulations, and explains metrics via Claude.",
)

_origins = ["*"] if settings.DEV_MODE else settings.origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")
app.include_router(explain.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
