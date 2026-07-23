import os
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.groq import Groq

# Force load the environment variables
load_dotenv(override=True)

def main():
    print("🧠 Booting up LaBSE and Groq...")
    # 1. Match the exact embedding model used for ingestion
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/LaBSE")
    
    # 2. Spin up our LLM for synthesizing the final answer
    Settings.llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

    print("🔌 Connecting to Postgres (LaBSE Multilingual Table)...")
    vector_store = PGVectorStore.from_params(
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        table_name="fir_embeddings_labse",
        embed_dim=768
    )

    # 3. Create the query engine (fetching top 3 most similar FIRs)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    query_engine = index.as_query_engine(similarity_top_k=3)

    # 4. The Multilingual Test
    # Kannada: "Theft of woman's gold chain at bus stop"
    kannada_query = "ಬಸ್ ನಿಲ್ದಾಣದಲ್ಲಿ ಮಹಿಳೆಯ ಚಿನ್ನದ ಸರ ಕಳ್ಳತನ" 
    
    print(f"\n🗣️ Querying RAG in Kannada: {kannada_query}")
    response = query_engine.query(kannada_query)
    
    print("\n==================================================")
    print("🤖 GROQ'S SYNTHESIZED RESPONSE:")
    print(response)
    print("==================================================")
    
    print("\n📄 BEHIND THE SCENES: SOURCE DOCUMENTS RETRIEVED:")
    for i, node in enumerate(response.source_nodes):
        print(f"\n--- Match {i+1} (Vector Similarity Score: {node.score:.3f}) ---")
        print(f"FIR ID: {node.metadata.get('fir_id')}")
        print(f"Narrative snippet: {node.text[:150]}...")

if __name__ == "__main__":
    main()