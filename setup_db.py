import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Force load the environment variables
load_dotenv(override=True)

def setup_database():
    print("🔌 Connecting to default 'postgres' database...")
    try:
        # 1. Connect to the default Postgres database to execute CREATE DATABASE
        conn = psycopg2.connect(
            dbname="postgres",  # Default system database
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", os.getenv("DB_PASS", "postgres")),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        # Must be in autocommit to create a database
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        db_name = os.getenv("DB_NAME", "ksp_db")

        print(f"🏗️ Creating database: {db_name}...")
        try:
            cursor.execute(f"CREATE DATABASE {db_name};")
            print("✅ Database created successfully.")
        except psycopg2.errors.DuplicateDatabase:
            print("⚠️ Database already exists.")
        
        cursor.close()
        conn.close()

        # 2. Reconnect to the NEW database to install the vector extension
        print(f"🧬 Enabling pgvector extension in {db_name}...")
        new_conn = psycopg2.connect(
            dbname=db_name,
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", os.getenv("DB_PASS", "postgres")),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        new_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        new_cursor = new_conn.cursor()
        
        # Install the extension required for LlamaIndex/pgvector
        new_cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ pgvector extension is live!")
        
        new_cursor.close()
        new_conn.close()
        print("🏁 Database setup complete. Ready for data!")

    except Exception as e:
        print(f"❌ Setup Error: {e}")

if __name__ == "__main__":
    setup_database()