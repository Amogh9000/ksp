import time
from query.intent_router import route_query

# 20 Queries spanning all four intents (5 of each)
TEST_SUITE = [
    # --- LOOKUP ---
    {"query": "Summarize the cyber fraud case in Hassan.", "expected": "LOOKUP"},
    {"query": "Retrieve FIR 99384 from yesterday.", "expected": "LOOKUP"},
    {"query": "What are the details of the theft reported by Amogh?", "expected": "LOOKUP"},
    {"query": "Who is the investigating officer for the Sami circle incident?", "expected": "LOOKUP"},
    {"query": "Get me the police report for the stolen bike in Mysuru.", "expected": "LOOKUP"},
    
    # --- PATTERN ---
    {"query": "What's the trend for chain snatching in Bengaluru over the last 5 years?", "expected": "PATTERN"},
    {"query": "Identify the hotspots for financial crimes this quarter.", "expected": "PATTERN"},
    {"query": "Are OTP frauds more common on weekends?", "expected": "PATTERN"},
    {"query": "Which district has the highest rate of vehicle theft?", "expected": "PATTERN"},
    {"query": "Has there been a spike in robberies since December?", "expected": "PATTERN"},
    
    # --- PREDICT ---
    {"query": "What is the probability of retaliation attacks tomorrow?", "expected": "PREDICT"},
    {"query": "Predict the number of cyber crimes next month.", "expected": "PREDICT"},
    {"query": "Will there be violence during the Friday protests?", "expected": "PREDICT"},
    {"query": "Assess the risk of bank fraud for elderly citizens next week.", "expected": "PREDICT"},
    {"query": "Where is the next chain snatching most likely to happen?", "expected": "PREDICT"},
    
    # --- NETWORK ---
    {"query": "Who are the known associates of Hitesh Bhavsar?", "expected": "NETWORK"},
    {"query": "Are these three isolated thefts actually the work of one organized gang?", "expected": "NETWORK"},
    {"query": "Trace the bank accounts linked to the recent phishing scams.", "expected": "NETWORK"},
    {"query": "Map the connections between the suspects in the Hassan case.", "expected": "NETWORK"},
    {"query": "Is the victim related to any previous offenders?", "expected": "NETWORK"},
]

def run_accuracy_test():
    print("🚀 Firing 20-Query Intent Routing Validation...\n")
    
    passed = 0
    total = len(TEST_SUITE)
    
    start_time = time.perf_counter()
    
    for idx, test in enumerate(TEST_SUITE, 1):
        query = test["query"]
        expected = test["expected"]
        
        # Call the router
        actual = route_query(query)
        
        if actual == expected:
            passed += 1
            status = "✅ [PASS]"
        else:
            status = f"❌ [FAIL] (Expected: {expected}, Got: {actual})"
            
        print(f"{status} {expected.ljust(7)} - {query}")
        
    total_time = round((time.perf_counter() - start_time), 2)
    accuracy = (passed / total) * 100
    
    print("\n" + "="*60)
    print(f"🏁 VALIDATION COMPLETE in {total_time}s")
    print(f"🎯 ACCURACY: {passed}/{total} ({accuracy}%)")
    print("="*60)

if __name__ == "__main__":
    run_accuracy_test()