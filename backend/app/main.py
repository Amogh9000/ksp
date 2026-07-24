from fastapi import FastAPI
from .routers import graph, risk, maps
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="KSP Track 4 API", version="1.0.0")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(risk.router, prefix="/risk", tags=["risk"])
app.include_router(maps.router, prefix="/map", tags=["maps"])

@app.get("/")
def read_root():
    return {"message": "Track 4 API is running"}
