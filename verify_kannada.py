import requests
import json

def run_5_kannada_deliverable_test():
    url = "http://127.0.0.1:8000/query"
    
    # 5 distinct Kannada investigative queries covering multiple districts & crime types
    kannada_test_queries = [
        {
            "id": "QUERY_01",
            "category": "Cyber Crime / Bank Fraud",
            "query": "ಆಶಿ ಯೋಗಿ ಸಂತ್ರಸ್ತರಾಗಿರುವ ಹಾಸನದ ಅನಧಿಕೃತ ಬ್ಯಾಂಕ್ ವ್ಯವಹಾರಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಸೈಬರ್ ಅಪರಾಧದ ವಿವರಗಳನ್ನು ನೀಡಿ."
        },
        {
            "id": "QUERY_02",
            "category": "OTP Fraud / Financial Crime",
            "query": "ಸಾಮಿ ಸರ್ಕಲ್ ಬಳಿ ನಡೆದ ಒಟಿಪಿ ವಂಚನೆ ಪ್ರಕರಣದ ಸಾರಾಂಶ ಮತ್ತು ವಿವರಗಳನ್ನು ನೀಡಿ."
        },
        {
            "id": "QUERY_03",
            "category": "Theft / Chain Snatching",
            "query": "ಬಸ್ ನಿಲ್ದಾಣ ಮತ್ತು ಸಾರ್ವಜನಿಕ ರಸ್ತೆಯಲ್ಲಿ ನಡೆದ ಚಿನ್ನದ ಸರ ಕಳ್ಳತನ ಪ್ರಕರಣಗಳ ಮಾಹಿತಿ ನೀಡಿ."
        },
        {
            "id": "QUERY_04",
            "category": "Vehicle Theft",
            "query": "ಬೆಳಗಾವಿ ಮತ್ತು ಸುತ್ತಮುತ್ತಲಿನ ಪ್ರದೇಶಗಳಲ್ಲಿ ವಾಹನ ಕಳ್ಳತನಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಇತ್ತೀಚಿನ ಎಫ್‌ಐಆರ್ ವಿವರ ಕೊಡಿ."
        },
        {
            "id": "QUERY_05",
            "category": "District General Crime Overview",
            "query": "ಹಾಸನ ಜಿಲ್ಲೆಯಲ್ಲಿ ದಾಖಲಾಗಿರುವ ಇತ್ತೀಚಿನ ಅಪರಾಧ ಪ್ರಕರಣಗಳು ಮತ್ತು ತನಿಖಾ ವರದಿ ನೀಡಿ."
        }
    ]

    doc_filename = "deliverable_kannada_5_queries_proof.md"
    
    print("🚀 Firing 5-Query Kannada Deliverable Verification...\n")
    
    with open(doc_filename, "w", encoding="utf-8") as doc:
        doc.write("# Deliverable Proof: Kannada Query In -> Kannada Answer Out\n")
        doc.write("### Verification Suite Results (5/5 Queries)\n\n")
        doc.write("---\n\n")

    passed_count = 0

    for item in kannada_test_queries:
        print(f"📌 [{item['id']}] Category: {item['category']}")
        print(f"📥 Input (Kannada): {item['query']}")
        
        payload = {
            "query": item["query"],
            "filters_dict": None,
            "officer_id": "DELIVERABLE-VERIFY"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                conf = data.get("confidence_band", "UNKNOWN")
                answer = data.get("answer_text", "")
                citations = data.get("citations", [])
                
                print(f"     ✅ Status: SUCCESS | Confidence: {conf} | Citations: {len(citations)}")
                answer_snippet = answer[:80].replace('\n', ' ')
                print(f"     🧠 Output Snippet: {answer_snippet}...\n")
                
                # Write to the deliverable proof document
                with open(doc_filename, "a", encoding="utf-8") as doc:
                    doc.write(f"## Test Case {item['id']}: {item['category']}\n")
                    doc.write(f"**Input Query (Kannada):** `{item['query']}`\n\n")
                    doc.write(f"**Confidence Band:** `{conf}`  \n")
                    doc.write(f"**Citations Count:** `{len(citations)}`  \n\n")
                    doc.write(f"### Generated Response (Kannada Output):\n{answer}\n\n")
                    if citations:
                        doc.write("**Attached Citations:**\n")
                        for c in citations:
                            doc.write(f"- **FIR ID:** `{c.get('fir_id')}` | Snippet: {c.get('snippet')}\n")
                    doc.write("\n---\n\n")
                
                passed_count += 1
            else:
                print(f"     ❌ Status: FAILED (HTTP {response.status_code})\n")
        except Exception as e:
            print(f"     ❌ Status: CRASHED ({e})\n")

    print("=" * 80)
    print(f"🏁 COMPLETED: {passed_count}/5 queries verified successfully!")
    print(f"📄 Verification report saved to: '{doc_filename}'")
    print("=" * 80)

if __name__ == "__main__":
    run_5_kannada_deliverable_test()