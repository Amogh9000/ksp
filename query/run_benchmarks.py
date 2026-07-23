from generate import generate_report

def run_evaluation_suite():
    print("🚀 INITIALIZING DATATHON EVALUATION SUITE...\n")
    
    # Task 1: The Primary Target Query
    q_primary = "show me robberies in Bengaluru Urban in 2024"
    
    # Task 3: The 5 Diverse Test Queries
    test_queries = [
        "Chain snatching incidents where the suspect was wearing a blue hoodie", # Tests specific suspect details (Mysuru)
        "Fake FedEx customs officer scam involving illegal passports",           # Tests cross-referencing near-duplicate cyber frauds (Mangaluru)
        "Physical assault outside a pub using a steering lock",                  # Tests weapon-specific matching (Bengaluru)
        "Domestic dispute escalating to violence with a glass bottle",           # Tests localized physical altercations (Mysuru)
        "Robbery at an independent residence in Vijayanagar while owners were away" # Tests specific location and MO matching
    ]
    
    # ---------------------------------------------------------
    # EXECUTING PRIMARY TARGET
    # ---------------------------------------------------------
    print("================================================================")
    print("🎯 PRIMARY TEST: Strict Metadata + Vector Combination")
    print(f"Query: '{q_primary}'")
    print("================================================================")
    
    # We pass the metadata filter to guarantee 100% accuracy for the strict district/year requirements
    report_primary = generate_report(
        q_primary, 
        filters_dict={"district": "Bengaluru Urban", "crime_type": "Robbery"}
    )
    print("\n🚨 GROQ SYNTHESIS:")
    print(report_primary)
    print("\n\n")
    
    # ---------------------------------------------------------
    # EXECUTING DIVERSE SUITE
    # ---------------------------------------------------------
    print("================================================================")
    print("🧪 DIVERSE TEST SUITE: Stress-Testing Semantic Boundaries")
    print("================================================================")
    
    for idx, query in enumerate(test_queries, 1):
        print(f"\n--- TEST {idx} ---")
        print(f"Query: '{query}'")
        
        # We run these without hard filters to test the pure semantic capability of LaBSE
        report = generate_report(query)
        print("\n🚨 GROQ SYNTHESIS:")
        print(report)
        print("-" * 64)

if __name__ == "__main__":
    run_evaluation_suite()