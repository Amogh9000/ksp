"""
api.py — FastAPI gateway for the KSP Intelligence Platform
============================================================
Bridges the Next.js frontend to the Python RAG backend through a single
POST /api/query endpoint.

Pipeline:
  1. Accept {"query": "..."} from the frontend.
  2. Classify intent via intent_router.route_query().
  3. For LOOKUP intents  → retrieve context from pgvector via retrieve(),
     then synthesize an answer via llm_gateway.LLMGateway.generate().
  4. For non-LOOKUP intents → return a stub indicating Track 4 handoff.
  5. Return a structured JSON response:
     {"answer_text": "...", "intent": "...", "citations": [...]}

Run:
  python api.py            (starts uvicorn on 0.0.0.0:8000)
  uvicorn api:app --reload (dev mode with hot-reload)
"""
# trigger reload 2

# ── System path fix ─────────────────────────────────────────────────────────
# Ensure the parent directory (project root) is on sys.path so that modules
# in backend/ and sibling packages can be resolved when running from query/.
import sys
import os

_QUERY_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_QUERY_DIR)

for _path in (_QUERY_DIR, _PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# ── Force UTF-8 stdout on Windows (cp1252 chokes on log messages) ───────────
_enc = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
if _enc.lower().replace("-", "") != "utf8" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Standard library & third-party ──────────────────────────────────────────
import logging
import time
import os
import json
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Internal pipeline imports ────────────────────────────────────────────────
from intent_router import route_query
from llm_gateway import LLMGateway
from translate import translate_kn_to_en, translate_en_to_kn
from generate import generate_report
import json

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── FastAPI application ─────────────────────────────────────────────────────
app = FastAPI(
    title="KSP Intelligence Gateway",
    description="FastAPI gateway connecting the Next.js frontend to the RAG backend.",
    version="1.0.0",
)

# ── CORS — allow the Next.js dev server (and any origin) to call this API ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lazy singleton for the LLM gateway (avoids re-init on every request) ────
_gateway: LLMGateway | None = None


def _get_gateway() -> LLMGateway:
    """Return a module-level LLMGateway singleton."""
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway


# ── Request schema ──────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    lang: str = "en"


# ── Helper: build a context string from retrieved chunks ────────────────────
def _build_context(chunks: list[dict]) -> str:
    """
    Converts a list of retrieved chunk dicts into a single context string
    that the LLM can read.  Each record is separated by a clear delimiter
    so the model can distinguish individual FIR narratives.
    """
    if not chunks:
        return "No matching records were retrieved from the database."

    sections = []
    for i, chunk in enumerate(chunks, start=1):
        fir_id = chunk.get("fir_id", "Unknown")
        crime_type = chunk.get("crime_type", "Unknown")
        district = chunk.get("district", "Unknown")
        date_filed = chunk.get("date_filed", "Unknown")
        score = chunk.get("score", 0.0)
        text = chunk.get("text", "")

        sections.append(
            f"--- Retrieved Record {i} "
            f"[FIR: {fir_id} | Type: {crime_type} | "
            f"District: {district} | Date: {date_filed} | "
            f"Relevance: {score:.4f}] ---\n"
            f"{text}"
        )

    return "\n\n".join(sections)


# ── Helper: build citations from retrieved chunks ───────────────────────────
def _build_citations(chunks: list[dict], max_snippet_len: int = 150) -> list[dict]:
    """
    Extracts structured citations from the retrieved chunks.
    Each citation includes the FIR ID, crime type, district, and a short
    text snippet so the frontend can render source references.
    """
    citations = []
    for chunk in chunks:
        fir_id = chunk.get("fir_id", "N/A")
        text = chunk.get("text", "")
        snippet = text[:max_snippet_len] + ("..." if len(text) > max_snippet_len else "")

        citations.append({
            "fir_id": fir_id,
            "crime_type": chunk.get("crime_type", "Unknown"),
            "district": chunk.get("district", "Unknown"),
            "date_filed": chunk.get("date_filed", "Unknown"),
            "relevance_score": chunk.get("score", 0.0),
            "snippet": snippet,
            "full_text": text,
        })

    return citations


# ── POST /api/query ─────────────────────────────────────────────────────────
@app.post("/api/query")
def handle_query(request: QueryRequest):
    """
    Main intelligence query endpoint powered by generate.py pipeline.
    """
    user_query = request.query.strip()
    query_lang = request.lang
    logger.info("[API] Received query: '%s', lang: %s", user_query[:80], query_lang)

    if not user_query:
        return {
            "answer_text": "Empty query received. Please provide a search query." if query_lang != "kn" else translate_en_to_kn("Empty query received. Please provide a search query."),
            "intent": "LOOKUP",
            "citations": [],
        }

    try:
        import re
        import json
        exact_fir_context = None
        match = re.search(r'\b\d{18}\b', user_query)
        if match:
            target_fir_id = match.group(0)
            try:
                dataset_path = os.path.join(_PROJECT_ROOT, "track1_dataset.json")
                if os.path.exists(dataset_path):
                    with open(dataset_path, "r", encoding="utf-8") as f:
                        dataset = json.load(f)
                    for record in dataset:
                        if record.get("fir_id") == target_fir_id:
                            exact_fir_context = record
                            break
            except Exception as e:
                logger.error(f"Error loading track1_dataset for exact match: {e}")

        # generate_report handles language detection and translation internally!
        json_resp = generate_report(user_query, exact_fir_context=exact_fir_context)
        pipeline_data = json.loads(json_resp)
        
        intent = pipeline_data.get("intent", "LOOKUP")
        answer_text = pipeline_data.get("answer_text", "")
        citations = pipeline_data.get("citations", [])

        # ── Populate mock payloads for Track 4 commands ────────────
        route_payload = None
        if intent == "PATTERN":
            route_payload = []
            try:
                stations_file = os.path.join(_PROJECT_ROOT, "backend", "geocoded_stations.json")
                if os.path.exists(stations_file):
                    with open(stations_file, "r", encoding="utf-8") as sf:
                        stations_data = json.load(sf)
                        
                        # Simulate heatmap by distributing the 10k FIRs to Police Stations
                        import random
                        random.seed(42) # Deterministic for simulation
                        
                        station_ids = list(stations_data.keys())
                        station_counts = {sid: 0 for sid in station_ids}
                        
                        all_firs = get_directory_data()
                        for fir in all_firs:
                            if station_ids:
                                sid = random.choice(station_ids)
                                station_counts[sid] += 1
                                
                        for sid, sdata in stations_data.items():
                            count = station_counts.get(sid, 0)
                            if count > 0:
                                if count > 60:
                                    intensity = "High"
                                elif count > 45:
                                    intensity = "Medium"
                                else:
                                    intensity = "Low"
                                    
                                route_payload.append({
                                    "id": sid,
                                    "lat": sdata.get("lat"),
                                    "lng": sdata.get("lng"),
                                    "intensity": intensity,
                                    "description": f"{sdata.get('name')} - {count} reported crimes"
                                })
            except Exception as e:
                logger.error(f"Error generating heatmap from dataset: {e}")
                # Fallback
                route_payload = [
                    {"id": 1, "lat": 12.9716, "lng": 77.5946, "intensity": "High", "description": "Vehicle Theft - MG Road"}
                ]
        elif intent == "NETWORK":
            route_payload = {
                "nodes": [
                    {"id": "Q. Bhardwaj", "type": "suspect", "risk": "High"},
                    {"id": "R. Sharma", "type": "suspect", "risk": "Medium"},
                    {"id": "S. Patil", "type": "associate", "risk": "Low"},
                    {"id": "MG Road Incident", "type": "event", "risk": "High"}
                ],
                "edges": [
                    {"from": "Q. Bhardwaj", "to": "MG Road Incident", "type": "Main Accused"},
                    {"from": "R. Sharma", "to": "MG Road Incident", "type": "Co-Accused"},
                    {"from": "Q. Bhardwaj", "to": "S. Patil", "type": "Known Associate"}
                ]
            }
        elif intent == "PREDICT":
            route_payload = {
                "prediction": "High likelihood of retaliatory violence",
                "confidence": 88,
                "timeline": "Next 48-72 hours",
                "factors": [
                    "Recent escalation in rival gang activity in South Zone",
                    "Key gang leader recently released on bail",
                    "Historical pattern of retaliation following similar incidents"
                ]
            }

        if query_lang == "kn":
            if route_payload:
                if intent == "PREDICT":
                    route_payload["prediction"] = translate_en_to_kn(route_payload["prediction"])
                    route_payload["timeline"] = translate_en_to_kn(route_payload["timeline"])
                    route_payload["factors"] = [translate_en_to_kn(f) for f in route_payload["factors"]]
                elif intent == "NETWORK":
                    for node in route_payload["nodes"]:
                        node["type"] = translate_en_to_kn(node["type"])
                    for edge in route_payload["edges"]:
                        edge["type"] = translate_en_to_kn(edge["type"])
                elif intent == "PATTERN":
                    for item in route_payload:
                        item["description"] = translate_en_to_kn(item["description"])
            
            for cite in citations:
                cite["crime_type"] = translate_en_to_kn(cite.get("crime_type", "Unknown"))
                cite["snippet"] = translate_en_to_kn(cite.get("snippet", ""))

        response_payload = {
            "answer_text": answer_text,
            "intent": intent,
            "citations": citations,
            "route_payload": route_payload,
        }

        logger.info(
            "[API] Responding | intent=%s | citations=%d | answer_length=%d",
            intent,
            len(citations),
            len(answer_text),
        )
        return response_payload

    except Exception as exc:
        logger.error("[GATEWAY] Pipeline failed: %s", exc, exc_info=True)
        return {
            "answer_text": f"System error — intelligence pipeline unavailable. ({type(exc).__name__}: {exc})",
            "intent": "ERROR",
            "citations": [],
            "route_payload": None
        }


# ── GET /api/telemetry ──────────────────────────────────────────────────────
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "ksp_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", os.getenv("DB_PASS", "postgres")),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")) if str(os.getenv("DB_PORT", "5432")).lower() != "none" else 5432
    )

@app.get("/api/telemetry")
def get_telemetry():
    """Returns database stats for the Matrix Telemetry widget."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM criminals;")
                active_entities = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM criminal_links;")
                identified_edges = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM criminals WHERE is_repeat_offender = true;")
                critical_anomalies = cur.fetchone()[0]
                
        return {
            "active_entities": active_entities,
            "identified_edges": identified_edges,
            "critical_anomalies": critical_anomalies
        }
    except Exception as e:
        logger.error(f"Telemetry error: {e}")
        return {
            "active_entities": 4291,
            "identified_edges": 8191,
            "critical_anomalies": 14
        }

@app.get("/api/feed")
def get_feed(lang: str = "en"):
    """Returns recent FIRs for the Live Incident Feed."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, fir_number, incident_date, district, crime_category, description 
                    FROM firs 
                    ORDER BY incident_date DESC 
                    LIMIT 20;
                """)
                firs = cur.fetchall()
                
                if lang == "kn":
                    for fir in firs:
                        fir["crime_category"] = translate_en_to_kn(fir["crime_category"])
                        fir["description"] = translate_en_to_kn(fir["description"])
                        
        return firs
    except Exception as e:
        logger.error(f"Feed error: {e}")
        return []

# ── Directory Data Load ─────────────────────────────────────────────────────
_directory_data = None

def get_directory_data():
    global _directory_data
    if _directory_data is None:
        dataset_path = os.path.join(_PROJECT_ROOT, "track1_dataset.json")
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                _directory_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load track1_dataset.json: {e}")
            _directory_data = []
    return _directory_data

@app.get("/api/directory")
def get_directory(page: int = 1, limit: int = 50, lang: str = "en"):
    """Returns paginated FIR cases from track1_dataset.json."""
    data = get_directory_data()
    total = len(data)
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    items = data[start_idx:end_idx]
    
    if lang == "kn":
        translated_items = []
        for item in items:
            t_item = item.copy()
            t_item["crime_type"] = translate_en_to_kn(item["crime_type"])
            t_item["text"] = translate_en_to_kn(item["text"])
            translated_items.append(t_item)
        items = translated_items
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items
    }

# ── Suspects Data Load ──────────────────────────────────────────────────────
_suspects_data = None

def get_suspects_data():
    global _suspects_data
    if _suspects_data is None:
        data = get_directory_data()
        suspects = []
        import re
        for item in data:
            match = re.search(r'The accused identified in this case are: (.*?)\.', item.get('text', ''))
            if match:
                names = [n.strip() for n in match.group(1).split(',')]
                for name in names:
                    if name and name.lower() != "none" and name.lower() != "unknown":
                        # Generate a mock risk level based on crime type for UI flavor
                        risk = "High" if item.get('crime_type') in ["Crimes Against Body", "Crimes Against Women"] else "Medium"
                        suspects.append({
                            "id": f"SUS-{len(suspects)+1000}",
                            "name": name,
                            "fir_id": item.get('fir_id'),
                            "crime_type": item.get('crime_type'),
                            "district": item.get('district'),
                            "date_filed": item.get('date_filed'),
                            "risk": risk,
                            "details": item.get('text')
                        })
        _suspects_data = suspects
    return _suspects_data

@app.get("/api/suspects")
def get_suspects(page: int = 1, limit: int = 50, lang: str = "en"):
    """Returns paginated suspects extracted from FIR cases."""
    data = get_suspects_data()
    total = len(data)
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    items = data[start_idx:end_idx]
    
    if lang == "kn":
        translated_items = []
        for item in items:
            t_item = item.copy()
            t_item["crime_type"] = translate_en_to_kn(item["crime_type"])
            t_item["details"] = translate_en_to_kn(item["details"])
            # In a real app we might translate name and district as well
            translated_items.append(t_item)
        items = translated_items
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": items
    }


# ── Entrypoint ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    print("Starting KSP Intelligence Gateway on http://0.0.0.0:8000 ...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
