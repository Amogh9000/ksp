import os
# 1. Ban TensorFlow from loading entirely
os.environ['USE_TF'] = '0'
# 2. Force HuggingFace to strictly use PyTorch
os.environ['USE_TORCH'] = '1'
# 3. Prevent multithreading DLL collisions
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# 4. Suppress the C++ logging spam
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 5. Import torch FIRST to lock in the backend before LlamaIndex wakes up
import torch
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator

# Force load the environment variables BEFORE singleton init so DB credentials are available
load_dotenv(override=True)

# ---------------------------------------------------------
# MODULE-LEVEL SINGLETONS
# Initializing LaBSE and PGVectorStore once per process prevents:
#   - Multi-second cold-start latency on every single retrieve() call
#   - Windows torch DLL threading collisions under concurrent requests
#   - Memory churn from repeatedly loading a 471MB model
# ---------------------------------------------------------
print("   -> [STARTUP] Loading LaBSE embedding model (CPU) — one-time init...")
_embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/LaBSE",
    device="cpu"
)

print("   -> [STARTUP] Connecting to pgvector database — one-time init...")
_vector_store = PGVectorStore.from_params(
    database=os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    table_name="fir_embeddings_labse",
    embed_dim=768
)

print("   -> [STARTUP] Mounting VectorStoreIndex — one-time init...")
_index = VectorStoreIndex.from_vector_store(
    vector_store=_vector_store,
    embed_model=_embed_model
)
print("   -> [STARTUP] All retrieval components ready.")


def retrieve(query: str, top_k: int = 3, filters_dict: dict = None):
    """
    Core retrieval function for the RAG pipeline.
    Uses module-level singleton embed model, vector store and index.
    Includes Confidence Band calculations based on vector math.
    """
    print(f"   -> [DEBUG] Executing similarity search (top_k={top_k})...")
    
    vector_filters = None
    if filters_dict:
        from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters, FilterOperator
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
        
    # ---------------------------------------------------------
    # CONFIDENCE BAND CALCULATION
    # ---------------------------------------------------------
    threshold = 0.65  # Baseline relevance threshold for LaBSE
    
    top_score = max(scores) if scores else 0.0
    valid_count = sum(1 for s in scores if s >= threshold)
    
    # Logic: High requires a strong primary match AND corroborating evidence.
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
            hits = retrieve(query, top_k=2, filters_dict=filters)
            
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