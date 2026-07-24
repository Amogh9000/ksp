import datetime
import logging
import uvicorn
import os
import json
import re
import urllib.parse
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from detect_lang import identify_language
from translate import translate_kn_to_en, translate_en_to_kn

app = FastAPI(title="Intelligence Gateway API")

# 🔓 Enable CORS for Frontend Wiring
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev/hackathon testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# Import your rock-solid RAG generator
from generate import generate_report

# Import the intent router - aliased to the name specified by the API contract
from intent_router import route_query as classify_intent

# NOTE: app is already initialised above with CORS middleware attached.
# Defining it again here would silently drop the middleware — kept as a comment only.
# app = FastAPI(title="GridSentinel/Pulse Intelligence Gateway", version="1.0")

# ---------------------------------------------------------
# PYDANTIC CONTRACT: Defines exactly what the frontend must send
# ---------------------------------------------------------
class IntelligenceQuery(BaseModel):
    query: str
    filters_dict: Optional[Dict[str, Any]] = None
    officer_id: Optional[str] = None  # Added for Track 1 Auth pass-through

@app.post("/query")
def process_investigative_query(request: IntelligenceQuery):
    print(f"\n📡 [API ENTRY] Gateway received query: '{request.query}'")

    try:
        detected_language = identify_language(request.query)
        search_query_en = translate_kn_to_en(request.query) if detected_language == "kn" else request.query
        
        # ── Step 1: Classify intent ──────────────────────────────────────────
        intent = classify_intent(search_query_en)
        print(f"🧭 [ROUTER] Detected intent: {intent} | officer={request.officer_id}")

        # ── Step 2: Route by intent ──────────────────────────────────────────

        # LOOKUP → RAG pipeline (existing path, unchanged)
        if intent == "LOOKUP":
            print("✅ [ROUTER] LOOKUP → dispatching to RAG pipeline")
            
            # --- EXACT FIR MATCH DETECTION ---
            exact_fir_context = None
            fir_match = re.search(r'(?:FIR\s*#?)\s*(\d{10,})', request.query, re.IGNORECASE)
            if fir_match:
                fir_id_to_find = fir_match.group(1)
                print(f"🔍 [ROUTER] Detected exact FIR ID in query: {fir_id_to_find}")
                if os.path.exists(TRACK1_DATASET_PATH):
                    try:
                        with open(TRACK1_DATASET_PATH, "r", encoding="utf-8") as f:
                            dataset = json.load(f)
                        for item in dataset:
                            if str(item.get("fir_id", "")) == str(fir_id_to_find):
                                exact_fir_context = item
                                print(f"✅ [ROUTER] Found exact FIR record for {fir_id_to_find}")
                                break
                    except Exception as e:
                        logger.error(f"[API] Error reading dataset for exact match: {e}")

            json_string_payload = generate_report(request.query, request.filters_dict, exact_fir_context)
            payload_dict = json.loads(json_string_payload)
            
            payload_dict["detected_language"] = detected_language
            answer_text = payload_dict.get("answer_text", "")
            
            if detected_language == "kn":
                translated_text = payload_dict.get("answer_text_english") or translate_kn_to_en(answer_text)
            else:
                translated_text = translate_en_to_kn(answer_text)
                
            payload_dict["translated_text"] = translated_text
            
            return JSONResponse(content=payload_dict, status_code=200)

        # PATTERN / PREDICT / NETWORK → Track 4 mocked handoff stub
        print(f"🚧 [ROUTER] {intent} → Track 4 handoff stub (external model pending)")

        route_payload = {
            "target_module": intent,
            "officer_id": request.officer_id,
            "raw_query": request.query,
            "translated_query": search_query_en,  # English query after translation
            "timestamp": datetime.datetime.now().isoformat()
        }

        answer_text_en = (
            f"🚧 **Track 4 Handoff:** Query routed to the {intent} module. "
            "External models are pending integration."
        )
        
        if detected_language == "kn":
            answer_text = translate_en_to_kn(answer_text_en)
            translated_text = answer_text_en
        else:
            answer_text = answer_text_en
            translated_text = translate_en_to_kn(answer_text_en)

        track4_stub = {
            "confidence_band": "N/A",
            "language_path": "TRANSLATED_KANNADA" if detected_language == "kn" else "DIRECT_ENGLISH",
            "intent": intent,
            "telemetry": {
                "top_score": 0.0,
                "valid_results_count": 0,
                "confidence_band": "N/A"
            },
            "answer_text": answer_text,
            "translated_text": translated_text,
            "detected_language": detected_language,
            "citations": [],
            "route_payload": route_payload
        }
        return JSONResponse(content=track4_stub, status_code=200)

    except Exception as exc:
        logger.error("[API] Unhandled exception for query=%r: %s", request.query, exc, exc_info=True)
        fallback = {
            "confidence_band": "LOW",
            "telemetry": {
                "top_score": 0.0,
                "valid_results_count": 0,
                "confidence_band": "LOW",
                "performance_ms": {}
            },
            "answer_text": f"**System error — pipeline unavailable.**\n\n{type(exc).__name__}: {exc}",
            "translated_text": f"**ಸಿಸ್ಟಮ್ ದೋಷ — ಪೈಪ್ಲೈನ್ ಲಭ್ಯವಿಲ್ಲ.**\n\n{type(exc).__name__}: {exc}",
            "detected_language": "en",
            "citations": []
        }
        return JSONResponse(content=fallback, status_code=200)

# ---------------------------------------------------------
# MOCK FALLBACK DATASETS
# ---------------------------------------------------------
MOCK_FIRS = [
    {
        "fir_id": "FIR-2023-MOCK-001",
        "district": "Bengaluru Urban",
        "crime_type": "Robbery",
        "status": "OPEN",
        "date_filed": "2023-04-12",
        "summary": "A mock incident report generated due to missing dataset files.",
        "suspects_named": ["Unknown"]
    }
]

MOCK_SUSPECTS = [
    {
        "id": "SUS-1001",
        "name": "Raja 'Bhai' Kumar",
        "alias": "Bhai",
        "risk_score": "87%",
        "firs_linked": ["FIR-2023-MOCK-001"],
        "primary_district": "Bengaluru Urban",
        "status": "AT LARGE",
        "known_affiliations": ["Local Syndicate"]
    }
]

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
TRACK1_DATASET_PATH = os.path.join(ROOT_DIR, "track1_dataset.json")

@app.get("/firs")
def get_firs(limit: int = 100, search: Optional[str] = None):
    print("📡 [API ENTRY] Gateway received request for /firs")
    try:
        data = None
        if os.path.exists(TRACK1_DATASET_PATH):
            try:
                with open(TRACK1_DATASET_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"[API] Failed to parse track1_dataset.json: {e}")
                
        if data is None:
            logger.warning("[API] FIR dataset not found or failed to load. Returning mock data.")
            data = MOCK_FIRS
            
        # Search logic
        if search:
            search_lower = search.lower()
            filtered_data = []
            for item in data:
                # Search across fir_id, district, crime_type, and text/summary
                if (search_lower in item.get("fir_id", "").lower() or 
                    search_lower in item.get("district", "").lower() or 
                    search_lower in item.get("crime_type", "").lower() or
                    search_lower in item.get("text", item.get("summary", "")).lower()):
                    filtered_data.append(item)
            data = filtered_data
            
        total_records = len(data)
        data = data[:limit]
            
        formatted_data = []
        for item in data:
            # Parse suspects if needed for the display, or just return empty
            suspects = item.get("suspects_named", [])
            text = item.get("text", item.get("summary", ""))
            if not suspects and text:
                match = re.search(r"The accused identified in this case are:\s*([^.]+)\.", text)
                if match:
                    suspects = [n.strip() for n in match.group(1).split(",") if n.strip() and n.strip() != "Unidentified"]

            formatted_data.append({
                "fir_id": item.get("fir_id", ""),
                "district": item.get("district", ""),
                "crime_type": item.get("crime_type", ""),
                "status": str(item.get("status", "OPEN")).upper(),
                "date_filed": item.get("date_filed", ""),
                "summary": text,
                "suspects_named": suspects
            })
        return JSONResponse(content={"total_records": total_records, "records": formatted_data}, status_code=200)
        
    except Exception as exc:
        logger.error(f"[API] Error loading FIRs: {exc}")
        return JSONResponse(content={"error": "Failed to load FIRs", "details": str(exc)}, status_code=500)

@app.get("/firs/{fir_id}")
def get_fir_by_id(fir_id: str):
    print(f"📡 [API ENTRY] Gateway received request for /firs/{fir_id}")
    try:
        data = None
        if os.path.exists(TRACK1_DATASET_PATH):
            try:
                with open(TRACK1_DATASET_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"[API] Failed to parse track1_dataset.json: {e}")
                
        if data is None:
            data = MOCK_FIRS

        # Search for the exact fir_id (cast to string to handle numeric/string IDs safely)
        for item in data:
            if str(item.get("fir_id", "")) == str(fir_id):
                return JSONResponse(content=item, status_code=200)
                
        return JSONResponse(content={"error": "Case File not found"}, status_code=404)
        
    except Exception as exc:
        logger.error(f"[API] Error loading FIR {fir_id}: {exc}")
        return JSONResponse(content={"error": "Failed to load FIR", "details": str(exc)}, status_code=500)

@app.get("/suspects")
def get_suspects(limit: int = 100, search: Optional[str] = None):
    print("📡 [API ENTRY] Gateway received request for /suspects")
    try:
        data = None
        if os.path.exists(TRACK1_DATASET_PATH):
            try:
                with open(TRACK1_DATASET_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"[API] Failed to parse track1_dataset.json: {e}")
                
        if data is None:
            logger.warning("[API] Suspects dataset not found. Returning mock data.")
            suspects_list = MOCK_SUSPECTS
        else:
            suspects_dict = {}
            # Parse suspects from FIRs
            for item in data:
                text = item.get("text", item.get("summary", ""))
                match = re.search(r"The accused identified in this case are:\s*([^.]+)\.", text)
                if match:
                    names = [n.strip() for n in match.group(1).split(",") if n.strip()]
                    for name in names:
                        if name == "Unidentified" or name.lower() == "unknown":
                            continue
                        if name not in suspects_dict:
                            # Generate an ID based on name hash or just incremental
                            suspect_id = f"SUS-{abs(hash(name)) % 100000}"
                            suspects_dict[name] = {
                                "id": suspect_id,
                                "name": name,
                                "alias": "",
                                "risk_score": "75%",
                                "firs_linked": [],
                                "primary_district": item.get("district", ""),
                                "status": "AT LARGE",
                                "known_affiliations": []
                            }
                        if item.get("fir_id") not in suspects_dict[name]["firs_linked"]:
                            suspects_dict[name]["firs_linked"].append(item.get("fir_id"))
            suspects_list = list(suspects_dict.values())
            
        if search:
            search_lower = search.lower()
            filtered_suspects = [
                s for s in suspects_list 
                if search_lower in s.get("name", "").lower() or 
                   search_lower in s.get("alias", "").lower() or 
                   search_lower in s.get("primary_district", "").lower()
            ]
            suspects_list = filtered_suspects
            
        total_records = len(suspects_list)
        suspects_list = suspects_list[:limit]
            
        formatted_data = []
        for item in suspects_list:
            formatted_data.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "alias": item.get("alias", ""),
                "risk_score": item.get("risk_score", "0%"),
                "firs_linked": item.get("firs_linked", []),
                "primary_district": item.get("primary_district", ""),
                "status": item.get("status", "UNKNOWN"),
                "known_affiliations": item.get("known_affiliations", [])
            })
        return JSONResponse(content={"total_records": total_records, "records": formatted_data}, status_code=200)
        
    except Exception as exc:
        logger.error(f"[API] Error loading Suspects: {exc}")
        return JSONResponse(content={"error": "Failed to load Suspects", "details": str(exc)}, status_code=500)

@app.get("/suspects/{suspect_id}")
def get_suspect_by_id(suspect_id: str):
    print(f"📡 [API ENTRY] Gateway received request for /suspects/{suspect_id}")
    try:
        search_id_or_name = urllib.parse.unquote(suspect_id).lower()

        data = None
        if os.path.exists(TRACK1_DATASET_PATH):
            try:
                with open(TRACK1_DATASET_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"[API] Failed to parse track1_dataset.json: {e}")
                
        if data is None:
            # Fallback to mock data if no dataset
            for s in MOCK_SUSPECTS:
                if str(s.get("id", "")).lower() == search_id_or_name or str(s.get("name", "")).lower() == search_id_or_name:
                    mock_fir = MOCK_FIRS[0]
                    return JSONResponse(content={
                        "id": s.get("id"),
                        "name": s.get("name"),
                        "alias": s.get("alias", ""),
                        "status": s.get("status", "AT LARGE"),
                        "risk_score": s.get("risk_score", "75% - HIGH"),
                        "primary_district": s.get("primary_district", ""),
                        "gang_affiliation": s.get("known_affiliations", ["Unknown"])[0] if s.get("known_affiliations") else "Unknown",
                        "associated_firs": [{
                            "fir_id": mock_fir["fir_id"],
                            "crime_type": mock_fir["crime_type"],
                            "date": mock_fir["date_filed"],
                            "summary": mock_fir["summary"]
                        }],
                        "known_crimes": [mock_fir["crime_type"]]
                    }, status_code=200)
            return JSONResponse(content={"error": "Suspect dossier not found"}, status_code=404)

        target_name = None
        target_id = None
        associated_firs = []
        known_crimes = set()
        districts = {}

        # First pass to find if suspect exists and get their name
        for item in data:
            text = item.get("text", item.get("summary", ""))
            match = re.search(r"The accused identified in this case are:\s*([^.]+)\.", text)
            if match:
                names = [n.strip() for n in match.group(1).split(",") if n.strip()]
                for name in names:
                    if name == "Unidentified" or name.lower() == "unknown":
                        continue
                    curr_id = f"SUS-{abs(hash(name)) % 100000}"
                    
                    if curr_id.lower() == search_id_or_name or name.lower() == search_id_or_name:
                        target_name = name
                        target_id = curr_id
                        break
            if target_name:
                break
                
        if not target_name:
            return JSONResponse(content={"error": "Suspect dossier not found"}, status_code=404)
            
        # Second pass to gather all FIRs for the found suspect
        for item in data:
            text = item.get("text", item.get("summary", ""))
            match = re.search(r"The accused identified in this case are:\s*([^.]+)\.", text)
            if match:
                names = [n.strip() for n in match.group(1).split(",") if n.strip()]
                if target_name in names:
                    crime_type = item.get("crime_type", "Unknown")
                    known_crimes.add(crime_type)
                    
                    dist = item.get("district", "Unknown")
                    districts[dist] = districts.get(dist, 0) + 1
                    
                    associated_firs.append({
                        "fir_id": item.get("fir_id", ""),
                        "crime_type": crime_type,
                        "date": item.get("date_filed", ""),
                        "summary": text
                    })
                    
        primary_district = "Unknown"
        if districts:
            primary_district = max(districts.items(), key=lambda x: x[1])[0]
            
        parts = target_name.split()
        alias = parts[0][0] + parts[-1][0] if len(parts) >= 2 else (target_name[0] if target_name else "")
        
        suspect_obj = {
            "id": target_id,
            "name": target_name,
            "alias": alias,
            "status": "AT LARGE",
            "risk_score": "75% - HIGH",
            "primary_district": primary_district,
            "gang_affiliation": "Unknown",
            "associated_firs": associated_firs,
            "known_crimes": list(known_crimes)
        }
        
        return JSONResponse(content=suspect_obj, status_code=200)

    except Exception as exc:
        logger.error(f"[API] Error loading Suspect details for {suspect_id}: {exc}")
        return JSONResponse(content={"error": "Failed to load Suspect dossier", "details": str(exc)}, status_code=500)

@app.get("/telemetry")
def get_telemetry():
    print("📡 [API ENTRY] Gateway received request for /telemetry")
    try:
        data = None
        if os.path.exists(TRACK1_DATASET_PATH):
            with open(TRACK1_DATASET_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                
        if not data:
            return JSONResponse(content={"active_entities": 0, "identified_edges": 0, "critical_anomalies": 0}, status_code=200)

        entities = set()
        edges = 0
        suspect_districts = {}

        for item in data:
            text = item.get("text", item.get("summary", ""))
            dist = item.get("district", "")
            
            # Extract complainant
            comp_match = re.search(r'^([A-Za-z\s]+) reported that', text)
            if comp_match:
                entities.add(comp_match.group(1).strip())
                
            # Extract suspects
            susp_match = re.search(r'The accused identified in this case are:\s*([^.]+)\.', text)
            if susp_match:
                names = [n.strip() for n in susp_match.group(1).split(',')]
                valid_suspects = []
                for n in names:
                    if n and n.lower() != 'unidentified':
                        entities.add(n)
                        valid_suspects.append(n)
                        if n not in suspect_districts:
                            suspect_districts[n] = set()
                        suspect_districts[n].add(dist)
                
                n_suspects = len(valid_suspects)
                if n_suspects > 1:
                    edges += (n_suspects * (n_suspects - 1)) // 2

        anomalies = sum(1 for dists in suspect_districts.values() if len(dists) > 1)

        return JSONResponse(content={
            "active_entities": len(entities),
            "identified_edges": edges,
            "critical_anomalies": anomalies
        }, status_code=200)

    except Exception as exc:
        logger.error(f"[API] Error loading telemetry: {exc}")
        return JSONResponse(content={"error": "Failed to load telemetry", "details": str(exc)}, status_code=500)

@app.get("/incidents/recent")
def get_recent_incidents():
    print("📡 [API ENTRY] Gateway received request for /incidents/recent")
    try:
        data = None
        if os.path.exists(TRACK1_DATASET_PATH):
            with open(TRACK1_DATASET_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                
        if not data:
            return JSONResponse(content=[], status_code=200)

        data_sorted = sorted(data, key=lambda x: x.get('date_filed', ''), reverse=True)
        
        recent = []
        for item in data_sorted[:8]:
            text = item.get('text', item.get('summary', ''))
            snippet = text[:100] + ('...' if len(text) > 100 else '')
            recent.append({
                'fir_id': item.get('fir_id', ''),
                'crime_type': item.get('crime_type', ''),
                'district': item.get('district', ''),
                'date_filed': item.get('date_filed', ''),
                'summary_snippet': snippet
            })

        return JSONResponse(content=recent, status_code=200)

    except Exception as exc:
        logger.error(f"[API] Error loading recent incidents: {exc}")
        return JSONResponse(content={"error": "Failed to load recent incidents", "details": str(exc)}, status_code=500)

if __name__ == "__main__":
    print("🚀 Firing up the Intelligence Gateway on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)