import os
from dotenv import load_dotenv
load_dotenv()

# 1. Ban TensorFlow from loading entirely
os.environ['USE_TF'] = '0'
# 2. Force HuggingFace to strictly use PyTorch
os.environ['USE_TORCH'] = '1'
# 3. Prevent multithreading DLL collisions
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# 4. Suppress the C++ logging spam
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import json

_embed_model = None
_index = None
HAS_LLAMA_INDEX = False

# Safe optional vector store loader
if os.getenv("ENABLE_VECTOR_STORE", "0") == "1":
    try:
        import torch
        from llama_index.core import VectorStoreIndex
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.vector_stores.postgres import PGVectorStore
        from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator

        print("   -> [STARTUP] Loading LaBSE embedding model (CPU)...")
        _embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/LaBSE",
            device="cpu"
        )
        _vector_store = PGVectorStore.from_params(
            database=os.getenv("DB_NAME", "ksp_db"),
            host=os.getenv("DB_HOST", "localhost"),
            password=os.getenv("DB_PASSWORD", os.getenv("DB_PASS", "postgres")),
            port=int(os.getenv("DB_PORT", "5432")) if str(os.getenv("DB_PORT", "5432")).lower() != "none" else 5432,
            user=os.getenv("DB_USER", "postgres"),
            table_name="fir_embeddings_labse",
            embed_dim=768
        )
        _index = VectorStoreIndex.from_vector_store(
            vector_store=_vector_store,
            embed_model=_embed_model
        )
        HAS_LLAMA_INDEX = True
        print("   -> [STARTUP] Vector retrieval engine ready.")
    except Exception as _e:
        print(f"   -> [STARTUP] VectorStore initialization bypassed ({_e}). Using dataset fallback.")


def _dataset_fallback_search(query: str, top_k: int = 3, filters_dict: dict = None):
    """Instant in-memory dataset search using track1_dataset.json (<1ms)."""
    root_dir = os.path.dirname(os.path.dirname(__file__))
    dataset_path = os.path.join(root_dir, "track1_dataset.json")
    
    results = []
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)
            
            keywords = [k.lower() for k in query.split() if len(k) > 2]
            scored_items = []
            
            for item in dataset:
                text = item.get("text", "")
                text_lower = text.lower()
                matches = sum(1 for kw in keywords if kw in text_lower)
                score = round(min(0.5 + (matches * 0.1), 0.95), 4) if matches > 0 else 0.3
                
                # Apply optional metadata filter
                if filters_dict:
                    match_filter = all(str(item.get(fk, "")).lower() == str(fv).lower() for fk, fv in filters_dict.items())
                    if not match_filter:
                        continue
                        
                scored_items.append((score, item))
                
            scored_items.sort(key=lambda x: x[0], reverse=True)
            
            for score, item in scored_items[:top_k]:
                results.append({
                    "fir_id": item.get("fir_id", "Unknown"),
                    "crime_type": item.get("crime_type", "Unknown"),
                    "district": item.get("district", "Unknown"),
                    "date_filed": item.get("date_filed", "Unknown"),
                    "text": item.get("text", ""),
                    "score": score
                })
        except Exception as err:
            print(f"   -> [FALLBACK ERROR] Failed to search dataset: {err}")
            
    scores = [r["score"] for r in results]
    top_score = max(scores) if scores else 0.0
    valid_count = len(results)
    
    return {
        "chunks": results,
        "telemetry": {
            "top_score": top_score,
            "valid_results_count": valid_count,
            "confidence_band": "MEDIUM" if valid_count > 0 else "LOW"
        }
    }


def retrieve(query: str, top_k: int = 3, filters_dict: dict = None):
    """
    Core retrieval function for the RAG pipeline.
    Uses vector index if enabled, or instant dataset fallback by default.
    """
    if not HAS_LLAMA_INDEX or _index is None:
        return _dataset_fallback_search(query, top_k, filters_dict)

    print(f"   -> [DEBUG] Executing similarity search (top_k={top_k})...")
    
    try:
        vector_filters = None
        if filters_dict:
            filter_list = [
                MetadataFilter(key=k, value=v, operator=FilterOperator.EQ)
                for k, v in filters_dict.items()
            ]
            vector_filters = MetadataFilters(filters=filter_list, condition="and")

        retriever = _index.as_retriever(
            similarity_top_k=top_k,
            filters=vector_filters
        )

        nodes_with_scores = retriever.retrieve(query)
        print(f"   -> [DEBUG] Successfully retrieved {len(nodes_with_scores)} chunks!")
        
        results = []
        scores = []
        for node in nodes_with_scores:
            score = round(node.score, 4)
            scores.append(score)
            results.append({
                "fir_id": node.metadata.get("fir_id"),
                "crime_type": node.metadata.get("crime_type"),
                "district": node.metadata.get("district"),
                "date_filed": node.metadata.get("date_filed"),
                "text": node.node.get_content(),
                "score": score
            })
            
        top_score = max(scores) if scores else 0.0
        threshold = 0.65
        valid_count = sum(1 for s in scores if s >= threshold)
        
        if top_score >= 0.75 and valid_count >= 2:
            confidence_band = "HIGH"
        elif top_score >= 0.70 and valid_count >= 1:
            confidence_band = "MEDIUM"
        else:
            confidence_band = "LOW"
            
        return {
            "chunks": results,
            "telemetry": {
                "top_score": top_score,
                "valid_results_count": valid_count,
                "confidence_band": confidence_band
            }
        }
    except Exception as exc:
        print(f"   -> [RETRIEVE ERROR] Vector query failed ({exc}). Using dataset fallback.")
        return _dataset_fallback_search(query, top_k, filters_dict)


def run_manual_tests():
    # Adding metadata filters to specific queries to test hybrid retrieval
    test_cases = [
        {
            "query": "Chain snatching by two men on a motorcycle", 
            "filters": None
        },
        {
            "query": "Chain snatching by two men on a motorcycle", 
            "filters": {"district": "Mysuru"}  # 🎯 Should force-exclude the Bengaluru near-duplicates
        },
        {
            "query": "ಬಸ್ ನಿಲ್ದಾಣದಲ್ಲಿ ಮಹಿಳೆಯ ಚಿನ್ನದ ಸರ ಕಳ್ಳತನ", # Kannada: Gold chain theft
            "filters": {"district": "Bengaluru Urban", "crime_type": "Chain-Snatching"}
        }
    ]
    
    print("🚀 Starting Hybrid Retrieval Testing Process...\n")
    
    for idx, case in enumerate(test_cases, 1):
        query = case["query"]
        filters = case["filters"]
        
        print(f"================================================================")
        print(f"🔍 TEST QUERY #{idx}: '{query}'")
        if filters:
            print(f"🔒 STRICT PRE-FILTER APPLIED: {filters}")
        print(f"================================================================")
        
        try:
            ret_payload = retrieve(query, top_k=2, filters_dict=filters)
            hits = ret_payload.get("chunks", [])
            
            if not hits:
                print("   ❌ No matching FIRs retrieved under these filter conditions.")
                continue
                
            for rank, hit in enumerate(hits, 1):
                print(f"\n   🎯 Match {rank} [Score: {hit['score']:.4f}]")
                print(f"   📂 FIR ID     : {hit['fir_id']}")
                print(f"   🚨 Crime Type  : {hit['crime_type']}")
                print(f"   📍 Location    : {hit['district']}")
                print(f"   📝 Narrative   : {hit['text'][:140]}...")
                
        except Exception as e:
            print(f"   ❌ Retrieval failed. Error: {e}")
            
        print("\n")

if __name__ == "__main__":
    run_manual_tests()