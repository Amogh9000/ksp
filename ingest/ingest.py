import json
import os
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

# LlamaIndex Imports
from llama_index.core import Document, Settings, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.groq import Groq

# Ensure stdout handles UTF-8 on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Force load the environment variables
load_dotenv(override=True)


def validate_and_clean_record(record: dict, index: int) -> dict:
    """
    Enforces the strict Track 1 schema contract on incoming data records.
    Raises errors or corrects formatting anomalies to prevent database drift.
    """
    required_keys = ["fir_id", "crime_type", "district", "date_filed", "text"]
    
    # 1. Structural Check
    for key in required_keys:
        if key not in record or record[key] is None:
            raise ValueError(f"❌ Schema Drift Detected at record [{index}]: Missing required key '{key}'")

    # 2. Type & Value Normalization
    fir_id = str(record["fir_id"]).strip()
    crime_type = str(record["crime_type"]).strip()
    district = str(record["district"]).strip()
    date_filed = str(record["date_filed"]).strip()
    text = str(record["text"]).strip()

    # 3. Strict Date Validation (Ensures YYYY-MM-DD)
    try:
        datetime.strptime(date_filed, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"❌ Schema Drift Detected: Record {fir_id} has invalid date format '{date_filed}'. Expected YYYY-MM-DD.")

    # 4. District & Crime Title Case Standardization
    district = district.title()
    crime_type = crime_type.title()

    return {
        "fir_id": fir_id,
        "crime_type": crime_type,
        "district": district,
        "date_filed": date_filed,
        "text": text
    }


def load_fir_documents(file_path):
    print(f"[INFO] Loading FIR records from {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    
    print("⚡ Validating dataset schema alignment against Track 1 contract...")
    documents = []
    
    for idx, row in enumerate(records):
        # --- THE FIX: Intercept and validate before document construction ---
        try:
            clean_row = validate_and_clean_record(row, idx)
        except ValueError as e:
            print(f"\n🛑 [FATAL CIRCUIT BREAKER] Ingestion stopped to prevent database drift:")
            print(str(e))
            sys.exit(1)
            
        metadata = {
            "fir_id": clean_row["fir_id"],
            "district": clean_row["district"],
            "crime_type": clean_row["crime_type"],
            "date_filed": clean_row["date_filed"],
        }
        
        doc = Document(
            text=clean_row["text"],
            metadata=metadata,
        )
        documents.append(doc)
    
    return documents


def main():
    # --- PHASE 1: Data Loading ---
    # Unified tracking path directly pointing to your 10k output dataset
    data_path = "track1_dataset.json"
    
    if not os.path.exists(data_path):
        print(f"❌ Error: Could not find the dataset file at '{data_path}'")
        sys.exit(1)
        
    docs = load_fir_documents(data_path)
    print(f"[OK] Cleanly validated and loaded {len(docs)} FIR documents.")

    # --- PHASE 2: Global Settings Configuration ---
    print("[INFO] Setting up LaBSE and Groq to bypass OpenAI defaults...")
    
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/LaBSE")
    Settings.text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=0)

    # --- PHASE 3: Database Connection ---
    print("[INFO] Connecting to pgvector (Multilingual Table)...")
    vector_store = PGVectorStore.from_params(
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        table_name="fir_embeddings_labse", 
        embed_dim=768                      
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # --- PHASE 4: Execution ---
    print("[INFO] Vectorizing and storing documents via LaBSE (768 dimensions)...")
    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=Settings.embed_model, 
        show_progress=True
    )
    
    print("[DONE] MULTILINGUAL INGESTION COMPLETE! Table 'fir_embeddings_labse' is live.")


if __name__ == "__main__":
    main()