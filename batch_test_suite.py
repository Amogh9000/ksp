import requests
import time

def run_batch_test():
    url = "http://127.0.0.1:8000/query"
    
    # A mix of highly relevant, ambiguous, and complete nonsense queries
    queries = [
        # --- Group 1: High Relevance (Should score HIGH/MEDIUM and return answers) ---
        "Give me the intelligence summary on the cyber crime in Hassan involving an unauthorized bank transaction.",
        "Show me all incidents of OTP fraud reported near Sami Circle.",
        "Are there any cases involving a suspect named Quincy Bhardwaj?",
        "Details regarding social media impersonation near Sheth Street.",
        "Summarize the phishing scams reported by Hitesh Rajan.",
        "Is Maanav Barad linked to any other financial crimes?",
        
        # --- Group 2: Broad / Ambiguous (Should pull data, testing chunk limits) ---
        "List all crimes against women filed recently.",
        "What are the major cyber crimes reported in Hassan?",
        "Give me all FIRs filed in 2024 involving bank accounts.",
        "Any incidents involving stolen vehicles or property theft in Belagavi?",
        
        # --- Group 3: Out-of-Domain / Nonsense (MUST trigger GUARDRAIL and LOW confidence) ---
        "How do I bake a chocolate cake?",
        "Who is the current Prime Minister of India?",
        "Provide a summary of UFO sightings reported in Bengaluru.",
        "What is the weather forecast for tomorrow?",
        "Can you write a Python script to scrape Twitter?"
    ]

    print("🚀 Initializing Batch Test Suite (15 Queries)...\n")
    print(f"{'Status':<10} | {'Conf':<6} | {'Chunks':<6} | {'Total(ms)':<10} | {'Query Snippet'}")
    print("-" * 80)

    success_count = 0
    fallback_count = 0

    for query in queries:
        payload = {
            "query": query,
            "filters_dict": None,
            "officer_id": "TEST-BATCH-RUNNER"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"{'ERROR':<10} | API crashed on query: {query[:30]}...")
                continue
                
            data = response.json()
            
            # Extract telemetry
            conf = data.get("confidence_band", "ERR")
            chunks = data["telemetry"].get("valid_results_count", 0)
            
            # Safely get timing if it exists, otherwise default to 0
            timing = data["telemetry"].get("performance_ms", {})
            total_ms = timing.get("total_pipeline_ms", 0)
            
            # Check if fallback guardrail triggered
            answer = data.get("answer_text", "")
            if "Low confidence" in answer or "Insufficient intelligence" in answer or chunks == 0:
                status = "GUARDRAIL"
                fallback_count += 1
            else:
                status = "SUCCESS"
                success_count += 1
                
            print(f"{status:<10} | {conf:<6} | {chunks:<6} | {total_ms:<10} | {query[:45]}...")
            
        except Exception as e:
            print(f"{'FAIL':<10} | Exception: {str(e)[:30]}")
            
    print("-" * 80)
    print("🏁 BATCH TEST COMPLETE")
    print(f"Total Successful Syntheses: {success_count}")
    print(f"Total Guardrail Fallbacks: {fallback_count}")
    print(f"Total Queries Processed: {len(queries)}")

if __name__ == "__main__":
    run_batch_test()