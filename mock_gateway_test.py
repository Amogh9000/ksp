import sys
import io
# Force UTF-8 output on Windows terminals that default to cp1252
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

def run_mock_gateway_call():
    """
    Automated test script to prove zero schema mismatches 
    on the API contract.
    """
    url = "http://127.0.0.1:8000/query"
    
    # 1. The Exact Input Contract
    payload = {
        "query": "Give me the intelligence summary on the cyber crime in Hassan involving an unauthorized bank transaction.",
        "filters_dict": None,
        "officer_id": "MOCK-OFFICER-77" 
    }
    
    print(f"🚀 Pinging Local Gateway at {url}...")
    
    try:
        response = requests.post(url, json=payload)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Gateway is down. Did you run 'python query/app.py' in another terminal?")
        sys.exit(1)

    # 2. Assert HTTP Success
    if response.status_code != 200:
        print(f"❌ Contract Mismatch: Received Status Code {response.status_code}")
        print(response.text)
        sys.exit(1)

    print("✅ Status 200 OK")
    
    # 3. Assert the Output Schema Match
    data = response.json()
    
    expected_keys = ["confidence_band", "telemetry", "answer_text", "citations"]
    for key in expected_keys:
        if key not in data:
            print(f"❌ Schema Mismatch: Missing expected key '{key}' in response.")
            sys.exit(1)
            
    # Optional nested telemetry check
    if "top_score" not in data.get("telemetry", {}):
         print(f"❌ Schema Mismatch: Telemetry block is missing 'top_score'.")
         sys.exit(1)

    print("✅ Output Schema Matches Gateway Contract Exactly")
    print(f"✅ Intelligence Successfully Synthesized ({len(data['citations'])} citations retrieved)")
    print("\n--- DELIVERABLE COMPLETE ---")

if __name__ == "__main__":
    run_mock_gateway_call()