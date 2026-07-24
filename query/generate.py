import sys
import io
import logging
import json
import re
import datetime
import time
from intent_router import route_query

# Force UTF-8 output on Windows terminals
_stdout_encoding = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'
if _stdout_encoding.lower() != 'utf-8' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = logging.getLogger(__name__)

from detect_lang import identify_language
from translate import translate_kn_to_en, translate_en_to_kn
from retrieve import retrieve
from confidence import evaluate_confidence

def log_transaction(
    query: str, 
    language: str, 
    translated_query: str, # 👈 1. ADD THIS PARAMETER
    chunks: list, 
    confidence_level: str, 
    final_answer: str, 
    timing_metrics: dict, 
    officer_id: str = "SYSTEM"
):
    log_file = "audit_log.jsonl"
    
    retrieved_data = [
        {
            "chunk_id": chunk.get("fir_id", "unknown"),
            "score": float(chunk.get("score", 0.0))
        }
        for chunk in chunks
    ]
    
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "officer_id": officer_id,
        "raw_query": query,
        "detected_language": language,
        "translated_query": translated_query if language == "kn" else None, # 👈 2. ADD THIS KEY
        "retrieved_chunks": retrieved_data,
        "confidence_level": confidence_level,
        "final_answer": final_answer,
        "performance_ms": timing_metrics
    }
    
    # 👈 3. ADD ensure_ascii=False TO RENDER NATIVE KANNADA CHARACTERS
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    # --- Secondary clean log: only entries with a real English translation ---
    # translated_audit_log.jsonl stores the English translated_query so it can
    # be queried / audited without needing to re-run the translation model.
    _is_valid_translation = (
        language == "kn"
        and isinstance(translated_query, str)
        and translated_query.strip()
        and translated_query.strip() != query.strip()          # not the raw fallback
        and not all(c in ". -" for c in translated_query)      # not garbage dots
    )
    if _is_valid_translation:
        translated_log_entry = {
            "timestamp":        log_entry["timestamp"],
            "officer_id":       officer_id,
            "raw_query_kn":     query,
            "translated_query_en": translated_query,
            "retrieved_chunks": retrieved_data,
            "confidence_level": confidence_level,
            "final_answer":     final_answer,
            "performance_ms":   timing_metrics,
        }
        with open("translated_audit_log.jsonl", "a", encoding="utf-8") as tf:
            tf.write(json.dumps(translated_log_entry, ensure_ascii=False) + "\n")

def generate_report(query: str, filters_dict: dict = None, exact_fir_context: dict = None) -> str:
    pipeline_start = time.perf_counter()
    print(f"\n🔍 [PHASE 1] Fetching intelligence for: '{query}'...")
    
    # 1. Detect Language
    detected_lang = identify_language(query)
    
    # 2. Intercept and Translate (if Kannada)
    search_query = query
    trans_ms = 0.0
    if detected_lang == "kn":
        print("🌍 [TRANSLATE] Kannada detected. Booting IndicTrans2...")
        trans_start = time.perf_counter()
        search_query = translate_kn_to_en(query) 
        trans_ms = round((time.perf_counter() - trans_start) * 1000, 2)
        print(f"🌍 [TRANSLATE] English Output: '{search_query}' (took {trans_ms}ms)")


    # ---------------------------------------------------------
    # 🚦 NEW: INTENT ROUTING INTERCEPT
    # ---------------------------------------------------------
    route_start = time.perf_counter()
    intent = route_query(search_query)
    route_ms = round((time.perf_counter() - route_start) * 1000, 2)
    print(f"🚦 [ROUTER] Query classified as: {intent} (took {route_ms}ms)")

    if intent != "LOOKUP":
        print(f"🚧 [ROUTER] Handoff required. Bypassing LOOKUP pipeline...")
        
        language_path = "TRANSLATED_KANNADA" if detected_lang == "kn" else "DIRECT_ENGLISH"
        handoff_message = f"🚧 **{intent} Module Handoff:** This query requires advanced analysis. Routing to Track 4 predictive/graph models..."
        
        if detected_lang == "kn":
            print("🌍 [TRANSLATE] Translating Track 4 handoff message to Kannada...")
            handoff_message = translate_en_to_kn(handoff_message)
            
        bypass_payload = {
            "confidence_band": "N/A",
            "language_path": language_path,
            "intent": intent, 
            "telemetry": {
                "top_score": 0.0,
                "valid_results_count": 0,
                "confidence_band": "N/A",
                "performance_ms": {"routing_ms": route_ms}
            },
            "answer_text": handoff_message,
            "citations": []
        }
        
        # Log this handoff to the audit trail
        log_transaction(query, detected_lang, search_query, [], "N/A", handoff_message, {"routing_ms": route_ms})
        
        return json.dumps(bypass_payload, indent=2)
    
    # --- TIMING BLOCK 1: EMBEDDING ---
    embedding_ms = 0.0 
    
    # --- TIMING BLOCK 2: VECTOR RETRIEVAL ---
    retrieve_start = time.perf_counter()
    
    # 🚨 THE FIX: Extract the dictionary payload, then isolate the chunks list
    retrieval_payload = retrieve(search_query, top_k=6, filters_dict=filters_dict)
    chunks = retrieval_payload.get("chunks", [])

    # Inject exact match if found
    if exact_fir_context:
        print(f"💉 [INJECTION] Injecting exact FIR record into context for {exact_fir_context.get('fir_id')}")
        exact_chunk = {
            "fir_id": exact_fir_context.get("fir_id", "Unknown"),
            "text": f"EXACT MATCHING FIR RECORD:\n{json.dumps(exact_fir_context, indent=2)}",
            "score": 1.0 # High confidence
        }
        chunks.insert(0, exact_chunk)
    
    retrieval_ms = round((time.perf_counter() - retrieve_start) * 1000, 2)
    
    conf_analysis = evaluate_confidence(chunks, threshold=0.40)
    level = conf_analysis["level"]
    matching_records = conf_analysis["matching_records"]
    
    top_score = max([c.get("score", 0.0) for c in chunks]) if chunks else 0.0
    
    generation_ms = 0.0 
    
    # --- EXIT PATH 1: GUARDRAIL FALLBACK ---
    if matching_records == 0:
        print("🛑 [GUARDRAIL] Zero records cleared relevance threshold.")
        clean_answer = "**Low confidence — limited data.**\n\nNo matching records found."
        
    # --- EXIT PATH 2: LLM GENERATION ---
    else:
        print(f"🧠 [PHASE 2] Synthesizing report via Zoho Catalyst QuickML...")
        
        gen_start = time.perf_counter()
        import requests
        import os
        
        url = "https://api.catalyst.zoho.in/quickml/v1/project/53326000000013024/rag/answer"
        headers = {
            "CATALYST-ORG": "60079693511",
            "Authorization": f"Zoho-oauthtoken {os.getenv('CATALYST_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        # Pass the retrieved context Document IDs (Catalyst requires IDs, not full text)
        payload = {
            "query": search_query,
            "documents": [str(c.get("fir_id", "")) for c in chunks]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                # Default to an answer key, fallback to a response key if needed
                raw_answer_text = data.get("answer", data.get("response", "No answer returned by Catalyst."))
            else:
                print(f"🛑 [CATALYST ERROR] {response.status_code}: {response.text}")
                print(f"🔄 [FALLBACK] Triggering Groq Gateway Fallback...")
                from llm_gateway import LLMGateway
                gateway = LLMGateway()
                context_string = "\n".join([c.get("text", "") for c in chunks])
                raw_answer_text = gateway.generate(prompt=search_query, context=context_string)
        except Exception as e:
            print(f"🛑 [CATALYST EXCEPTION] {e}")
            print(f"🔄 [FALLBACK] Triggering Groq Gateway Fallback...")
            from llm_gateway import LLMGateway
            gateway = LLMGateway()
            context_string = "\n".join([c.get("text", "") for c in chunks])
            raw_answer_text = gateway.generate(prompt=search_query, context=context_string)

        generation_ms = round((time.perf_counter() - gen_start) * 1000, 2)
        
        clean_answer = raw_answer_text.strip()
        if "Insufficient intelligence" in clean_answer:
            print("🛑 [GUARDRAIL] LLM refused to hallucinate.")
            
    # ---------------------------------------------------------
    # 🌍 THE FINAL LOOP: TRANSLATE ANSWER BACK TO NATIVE SCRIPT
    # ---------------------------------------------------------
    english_answer = None
    if detected_lang == "kn":
        english_answer = clean_answer
        print("🌍 [TRANSLATE] Translating final English answer back to Kannada...")
        clean_answer = translate_en_to_kn(clean_answer)
        print(f"🌍 [TRANSLATE] Final Kannada Output: '{clean_answer[:50]}...'")
        
    # Calculate Total Pipeline Latency
    total_ms = round((time.perf_counter() - pipeline_start) * 1000, 2)
    timing_metrics = {
        "translation_ms": trans_ms,
        "embedding_ms": embedding_ms,
        "retrieval_ms": retrieval_ms,
        "generation_ms": generation_ms,
        "total_pipeline_ms": total_ms
    }

    citations = [
        {"fir_id": c.get("fir_id", "N/A"), "snippet": c.get("text", "")[:120]} 
        for c in chunks[:matching_records]
    ]

    language_path = "TRANSLATED_KANNADA" if detected_lang == "kn" else "DIRECT_ENGLISH"
    
    telemetry_payload = {
        "top_score": top_score,
        "valid_results_count": matching_records,
        "confidence_band": level,
        "language_path": language_path,
        "performance_ms": timing_metrics
    }
    
    final_payload = {
        "confidence_band": level,
        "language_path": language_path,
        "telemetry": telemetry_payload,
        "answer_text": clean_answer,
        "answer_text_english": english_answer,
        "citations": citations
    }
    log_transaction(query, detected_lang, search_query, chunks, level, clean_answer, timing_metrics)    
    return json.dumps(final_payload, indent=2)

if __name__ == "__main__":
    print("🚀 Initializing Abstracted RAG Pipeline...")
    q_validate = "Give me the intelligence summary on the cyber crime in Hassan involving an unauthorized bank transaction where Aashi Yogi was listed as the victim."
    json_response = generate_report(q_validate)
    print("\n📦 FINAL API-READY JSON CONTRACT PAYLOAD:")
    print(json_response)