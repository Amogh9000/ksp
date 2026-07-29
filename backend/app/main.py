import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, firs, criminals, officers

app = FastAPI(
    title="KSP Intelligence Platform API",
    version="0.1.0",
    description="Karnataka State Police — backend API with JWT auth, RBAC, and audit logging.",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins for local dev; restrict in production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(firs.router, prefix=API_PREFIX)
app.include_router(criminals.router, prefix=API_PREFIX)
app.include_router(officers.router, prefix=API_PREFIX)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
