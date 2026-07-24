import json
from generate import generate_report

def run_stress_test():
    print("🧨 INITIALIZING 8-POINT PIPELINE STRESS TEST...\n")
    
    # 8 distinct edge cases designed to break RAG systems
    test_cases = [
        {
            "name": "1. The Out-of-Domain Trap",
            "query": "What are the traffic fines for jumping a red light in Bengaluru?",
            "filters": None,
            "expected_behavior": "Should trigger the 'Insufficient intelligence' safety fallback."
        },
        {
            "name": "2. The Date Hallucination Check",
            "query": "Show me robberies that happened in 2025.",
            "filters": None,
            "expected_behavior": "Should return the safety fallback, as our dataset ends in 2024."
        },
        {
            "name": "3. The Contradictory Metadata Clash",
            "query": "Tell me about chain snatching in Mysuru.",
            "filters": {"district": "Bengaluru Urban"}, 
            "expected_behavior": "Should return empty. The strict SQL metadata filter must override the semantic text."
        },
        {
            "name": "4. The Vague Query (Low Semantic Signal)",
            "query": "Someone got hurt really bad.",
            "filters": None,
            "expected_behavior": "Should retrieve Assault FIRs based purely on semantic proximity to 'hurt'."
        },
        {
            "name": "5. The Kannada-English Cross-Contamination",
            "query": "ಮೈಸೂರಿನಲ್ಲಿ ಸೈಬರ್ ವಂಚನೆ (Cyber fraud in Mysuru)",
            "filters": {"crime_type": "Cyber Fraud"},
            "expected_behavior": "Should successfully pull Mysuru cyber frauds using hybrid filtering and bilingual text."
        },
        {
            "name": "6. The Hyper-Specific Weapon",
            "query": "Assault involving a steering lock or machete.",
            "filters": None,
            "expected_behavior": "Should pull FIR-2023-BLR-088 (steering lock) and FIR-2024-BLR-091 (machete)."
        },
        {
            "name": "7. The Duplicate Entity Pull",
            "query": "FedEx customs officer scam with illegal passports.",
            "filters": None,
            "expected_behavior": "Should pull BOTH Mangaluru near-duplicates (FIR-2023-MAN-042 and FIR-2023-MAN-901)."
        },
        {
            "name": "8. The Complex Multi-Variable Query",
            "query": "Robbery involving an auto-rickshaw late at night.",
            "filters": {"district": "Bengaluru Urban"},
            "expected_behavior": "Should hit FIR-2024-BLR-091 (IT employee mugged at 10 PM)."
        }
    ]
    
    success_count = 0
    failure_log = []

    for idx, test in enumerate(test_cases, 1):
        print(f"================================================================")
        print(f"🧪 TEST {idx}: {test['name']}")
        print(f"   Query  : '{test['query']}'")
        if test['filters']:
            print(f"   Filters: {test['filters']}")
        print(f"   Expect : {test['expected_behavior']}")
        print(f"----------------------------------------------------------------")
        
        try:
            # Execute the pipeline
            raw_response = generate_report(test['query'], filters_dict=test['filters'])
            
            # Verify JSON integrity
            parsed_json = json.loads(raw_response)
            
            # Print cleanly for eyeball logging
            print(f"✅ JSON Contract Parsed Successfully.")
            print(f"📝 Answer Snippet: {parsed_json['answer_text'][:150]}...")
            print(f"🔗 Citations Pulled: {len(parsed_json['citations'])}")
            for cite in parsed_json['citations']:
                print(f"    - {cite['fir_id']}: {cite['snippet'][:80]}...")
                
            success_count += 1
            
        except json.JSONDecodeError:
            print("❌ CRITICAL FAILURE: LLM broke the JSON contract format.")
            failure_log.append(f"Test {idx} failed JSON validation.")
        except Exception as e:
            print(f"❌ CRITICAL FAILURE: Pipeline crashed. Error: {e}")
            failure_log.append(f"Test {idx} crashed: {str(e)}")
            
        print("\n")

    print("================================================================")
    print(f"🏁 TEST SUITE COMPLETE. Passed: {success_count}/{len(test_cases)}")
    if failure_log:
        print("🚨 SHAKY BEHAVIOR LOG:")
        for log in failure_log:
            print(f"   - {log}")
    else:
        print("✅ PIPELINE IS ROCK SOLID. Zero crashes or format breaks detected.")
    print("================================================================")

if __name__ == "__main__":
    run_stress_test()