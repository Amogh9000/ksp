from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, firs, criminals, officers, maps, graph, risk

app = FastAPI(
    title="KSP Intelligence Platform API",
    version="0.1.0",
    description="Karnataka State Police — backend API with JWT auth, RBAC, RAG analytics, geospatial mapping, and graph network analysis.",
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js dev server during development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
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
app.include_router(maps.router, prefix=API_PREFIX)
app.include_router(graph.router, prefix=API_PREFIX)
app.include_router(risk.router, prefix=API_PREFIX)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
