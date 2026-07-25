import requests
import json
import time

def tail_audit_log(lines=8):
    """Reads the most recent entries from the XAI log to verify detection."""
    with open("audit_log.jsonl", "r", encoding="utf-8") as f:
        log_lines = f.readlines()
        return [json.loads(line) for line in log_lines[-lines:]]

def run_language_test():
    url = "http://127.0.0.1:8000/query"
    
    queries = [
        # --- 1. Short English Queries (The langdetect killers) ---
        "OTP fraud",
        "FIR 102",
        "Hassan crime",
        
        # --- 2. Kannada Script ---
        "ಹಾಸನದಲ್ಲಿ ಸೈಬರ್ ಅಪರಾಧ",
        "ಬ್ಯಾಂಕ್ ಖಾತೆಯಿಂದ ಹಣ ಕಳ್ಳತನ",
        
        # --- 3. Code-Mixed (Kannada + English) ---
        "Hassan nalli cyber crime cases detail kodi",
        "stolen vehicles in Belagavi list madi",
        "OTP fraud details beku"
    ]
    
    print("🚀 Firing Multilingual Batch to Gateway...")
    for query in queries:
        payload = {"query": query, "filters_dict": None, "officer_id": "LANG-TEST"}
        requests.post(url, json=payload)
        
    time.sleep(1) # Give the system a second to write all logs
    
    print("\n📊 FastText Detection Results (Read from XAI Audit Log):")
    print(f"{'Detected':<10} | {'Query'}")
    print("-" * 60)
    
    recent_logs = tail_audit_log(len(queries))
    for log in recent_logs:
        print(f"{log.get('detected_language', 'ERR'):<10} | {log.get('raw_query')}")

if __name__ == "__main__":
    run_language_test()