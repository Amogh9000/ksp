"""
Crime AI Datathon: RAG Retrieval Engine
---------------------------------------
This script connects to the pgvector database, embeds a raw text query using the 
multilingual LaBSE model, and executes a cosine similarity search to return the 
top-k most relevant FIR chunks with their exact semantic scores.
"""

import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator

# Bypass terminal cache and enforce local credentials
load_dotenv(override=True)

def retrieve(query: str, top_k: int = 3, filters_dict: dict = None):
    """
    Core retrieval function for the RAG pipeline.
    
    Args:
        query (str): The raw text user query (English or Kannada).
        top_k (int): Number of chunks to return.
        filters_dict (dict, optional): Key-value pairs for strict metadata filtering 
                                       (e.g., {"district": "Bengaluru Urban"}).
                                       
    Returns:
        list[dict]: A list of dictionaries containing the scored document chunks and metadata.
    """
    
    # 1. Initialize the embedding model (Must match ingestion exactly: 768 dimensions)
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/LaBSE")

    # 2. Connect to the pgvector storage layer
    vector_store = PGVectorStore.from_params(
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        table_name="fir_embeddings_labse",
        embed_dim=768
    )

    # 3. Mount the index over the existing database
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model
    )
    
    # 4. Optional: Apply SQL-level exact-match metadata filters prior to vector search
    vector_filters = None
    if filters_dict:
        filter_list = [
            MetadataFilter(key=k, value=v, operator=FilterOperator.EQ) 
            for k, v in filters_dict.items()
        ]
        vector_filters = MetadataFilters(filters=filter_list, condition="and")
    
    # 5. Build retriever and execute query
    retriever = index.as_retriever(
        similarity_top_k=top_k, 
        filters=vector_filters
    )
    
    nodes_with_scores = retriever.retrieve(query)
    
    # 6. Clean and package the payload for the downstream LLM or UI
    results = []
    for node in nodes_with_scores:
        results.append({
            "fir_id": node.metadata.get("fir_id"),
            "crime_type": node.metadata.get("crime_type"),
            "district": node.metadata.get("district"),
            "date_filed": node.metadata.get("date_filed"),
            "text": node.node.get_content(),
            "score": round(node.score, 4) # Cosine similarity score
        })
        
    return results

# ==========================================
# DEMO EXECUTION (For Team Review)
# ==========================================
if __name__ == "__main__":
    print("🚀 Initializing Vector Retrieval Demo...\n")
    
    # Test 1: Standard Semantic Search (English)
    q1 = "Burglary at a locked residential house"
    print(f"🔍 QUERY 1 (Raw Text): '{q1}'")
    hits_1 = retrieve(q1, top_k=2)
    for i, hit in enumerate(hits_1, 1):
        print(f"   [{hit['score']}] FIR: {hit['fir_id']} | Type: {hit['crime_type']} | Location: {hit['district']}")
    
    print("-" * 50)
    
    # Test 2: Multilingual Search (Kannada)
    q2 = "ಬಸ್ ನಿಲ್ದಾಣದಲ್ಲಿ ಮಹಿಳೆಯ ಚಿನ್ನದ ಸರ ಕಳ್ಳತನ"
    print(f"🔍 QUERY 2 (Multilingual): '{q2}'")
    hits_2 = retrieve(q2, top_k=2)
    for i, hit in enumerate(hits_2, 1):
        print(f"   [{hit['score']}] FIR: {hit['fir_id']} | Type: {hit['crime_type']} | Location: {hit['district']}")
    
    print("-" * 50)
    
    # Test 3: Hybrid Search (Vector + Metadata Pre-filtering)
    q3 = "Cyber fraud involving fake banking website"
    filters = {"district": "Bengaluru Urban"}
    print(f"🔍 QUERY 3 (Hybrid Filter): '{q3}' + Filters: {filters}")
    hits_3 = retrieve(q3, top_k=2, filters_dict=filters)
    for i, hit in enumerate(hits_3, 1):
         print(f"   [{hit['score']}] FIR: {hit['fir_id']} | Type: {hit['crime_type']} | Location: {hit['district']}")