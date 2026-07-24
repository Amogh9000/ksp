import requests
import json

def test_week1_kannada_queries():
    url = "http://127.0.0.1:8000/query"
    
    # Week 1 benchmark queries translated into natural Kannada
    week1_kannada_queries = [
        {
            "title": "1. Hassan Cyber Crime (Aashi Yogi Case)",
            "query": "ಆಶಿ ಯೋಗಿ ಸಂತ್ರಸ್ತರಾಗಿರುವ ಹಾಸನದ ಅನಧಿಕೃತ ಬ್ಯಾಂಕ್ ವ್ಯವಹಾರಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಸೈಬರ್ ಅಪರಾಧದ ವಿವರಗಳನ್ನು ನೀಡಿ."
        },
        {
            "title": "2. OTP Fraud near Sami Circle",
            "query": "ಸಾಮಿ ಸರ್ಕಲ್ ಬಳಿ ನಡೆದ ಒಟಿಪಿ ವಂಚನೆ ಪ್ರಕರಣದ ವಿವರಗಳನ್ನು ನೀಡಿ."
        },
        {
            "title": "3. Hassan Crime Overview",
            "query": "ಹಾಸನ ಜಿಲ್ಲೆಯಲ್ಲಿ ದಾಖಲಾಗಿರುವ ಇತ್ತೀಚಿನ ಸೈಬರ್ ಅಪರಾಧ ಪ್ರಕರಣಗಳ ಸಾರಾಂಶ ಕೊಡಿ."
        }
    ]

    print("🚀 Running Week 1 Kannada Round-Trip Test Suite...\n")
    print("=" * 80)

    # (Keep the top of your script the same)
    
    print("🚀 Running Week 1 Kannada Round-Trip Test Suite...\n")
    
    # Create or clear the review file
    with open("kannada_review_doc.md", "w", encoding="utf-8") as f:
        f.write("# Multilingual RAG Translation Review\n\n")

    for item in week1_kannada_queries:
        print(f"📌 TEST: {item['title']}")
        
        payload = {
            "query": item["query"],
            "filters_dict": None,
            "officer_id": "WEEK1-KN-TEST"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer_text", "")
                
                print("     ✅ SUCCESS - Writing to file...")
                
                # Append the readable results to our markdown file
                with open("kannada_review_doc.md", "a", encoding="utf-8") as f:
                    f.write(f"### {item['title']}\n")
                    f.write(f"**Kannada Query:** {item['query']}\n\n")
                    f.write(f"**Translated RAG Output:**\n{answer}\n\n")
                    f.write("---\n\n")
            else:
                print(f"❌ Error: API returned status code {response.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")

            
if __name__ == "__main__":
    test_week1_kannada_queries()