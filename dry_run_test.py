import json
import requests

URL = "http://127.0.0.1:8000/query"

TEST_CASES = [
    {
        "intent_type": "LOOKUP",
        "payload": {
            "query": "Give me the summary of the OTP fraud case near Sami Circle.",
            "officer_id": "OFFICER_LOOKUP"
        }
    },
    {
        "intent_type": "PATTERN",
        "payload": {
            "query": "What is the most common cyber crime in Hassan this month?",
            "officer_id": "OFFICER_PATTERN"
        }
    },
    {
        "intent_type": "PREDICT",
        "payload": {
            "query": "What is the likelihood of a chain snatching incident at the bus stand tomorrow?",
            "officer_id": "OFFICER_PREDICT"
        }
    },
    {
        "intent_type": "NETWORK",
        "payload": {
            "query": "Is Quincy Bhardwaj connected to any other bank fraud cases or organized crime syndicates?",
            "officer_id": "OFFICER_NETWORK"
        }
    }
]

def run_dry_run():
    print("🚀 EXECUTING LIVE /query ENDPOINT DRY RUN FOR ALL 4 INTENTS\n" + "="*65)
    
    for idx, test in enumerate(TEST_CASES, 1):
        target_intent = test["intent_type"]
        payload = test["payload"]
        
        print(f"\n[TEST {idx}/4] Expected Intent: {target_intent}")
        print(f"Query: \"{payload['query']}\"")
        
        try:
            res = requests.post(URL, json=payload, timeout=120)
            if res.status_code == 200:
                data = res.json()
                detected_intent = data.get("intent", "LOOKUP" if "intent" not in data else data["intent"])
                
                print(f"  ✅ Status: 200 OK | Returned Intent: {detected_intent}")
                
                if detected_intent == "LOOKUP":
                    print(f"  📌 Pipeline Path: FULL RAG VECTOR RETRIEVAL")
                    print(f"  📊 Confidence Band: {data.get('confidence_band')}")
                    print(f"  📚 Citations Found: {len(data.get('citations', []))}")
                    print(f"  💬 Answer Snippet: {data.get('answer_text', '')[:90]}...")
                else:
                    print(f"  📌 Pipeline Path: TRACK 4 HANDOFF STUB")
                    route_payload = data.get("route_payload", {})
                    print(f"  📦 Route Target Module: {route_payload.get('target_module')}")
                    print(f"  🆔 Officer ID Passed: {route_payload.get('officer_id')}")
                    print(f"  🕒 Timestamp Generated: {route_payload.get('timestamp')}")
                    print(f"  💬 Message: {data.get('answer_text')}")
            else:
                print(f"  ❌ Status: {res.status_code} | Error: {res.text}")
        except Exception as e:
            print(f"  ❌ Request Failed: {e}")

    print("\n" + "="*65 + "\n🏁 DRY RUN COMPLETE")

if __name__ == "__main__":
    run_dry_run()