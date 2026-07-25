import os
import psycopg2
from dotenv import load_dotenv

# Force load the environment variables
load_dotenv(override=True)

def verify_database():
    print("🔍 Connecting directly to PostgreSQL to inspect vector tables...")
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()
        
        # Look for both the bge-small table and the LaBSE table
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE '%fir_embeddings%';
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No FIR embedding tables found in the public schema.")
            return
            
        for table in tables:
            actual_table = table[0]
            print(f"\n📊 Analyzing Table: {actual_table}")
            
            # 1. Get total row count
            cursor.execute(f"SELECT COUNT(*) FROM {actual_table};")
            row_count = cursor.fetchone()[0]
            print(f"   🔹 Total Records Ingested: {row_count}")
            
            # 2. Verify that the embedding column exists and is populated
            # LlamaIndex usually names the vector column 'embedding'
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM {actual_table} 
                    WHERE embedding IS NOT NULL;
                """)
                populated_vectors = cursor.fetchone()[0]
                
                if row_count == populated_vectors and row_count > 0:
                    print(f"   ✅ Vector Column Integrity: 100% POPULATED ({populated_vectors}/{row_count} rows contain active vectors)")
                else:
                    print(f"   ⚠️ Vector Column Integrity: WARNING! Found {row_count - populated_vectors} rows with missing vectors.")
                
                # 3. Sample a vector to verify its dimensions dynamically
                cursor.execute(f"SELECT embedding FROM {actual_table} LIMIT 1;")
                sample_vector = cursor.fetchone()
                if sample_vector and sample_vector[0]:
                    # Format changes depending on whether it returns a list or a string representation
                    vector_str = str(sample_vector[0])
                    dimensions = len(vector_str.strip('[]').split(','))
                    print(f"   🔹 Detected Vector Dimensions: {dimensions}")
                    
            except Exception as vector_error:
                print(f"   ❌ Could not read embedding column: {vector_error}")
                conn.rollback()

        cursor.close()
        conn.close()
        print("\n🏁 Database verification routine finished successfully.")
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    verify_database()