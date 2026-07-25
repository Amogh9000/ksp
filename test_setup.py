import os
import psycopg2
from dotenv import load_dotenv

# override=True forces Python to read the .env file and ignore terminal memory
load_dotenv(override=True)

def verify_db():
    print(f"🔍 Diagnostic: Attempting connection to {os.getenv('DB_HOST')} on port {os.getenv('DB_PORT')}...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        ext = cursor.fetchone()
        print(f"✅ Database connected. pgvector extension: {ext[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def verify_llm():
    from llama_index.llms.groq import Groq
    try:
        llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
        response = llm.complete("Ping")
        print(f"✅ LLM connection successful. Response: {response.text.strip()}")
    except Exception as e:
        print(f"❌ LLM API call failed: {e}")

if __name__ == "__main__":
    print("--- Running Architecture Diagnostics ---")
    verify_db()
    verify_llm()