import requests
import json

def run_translation_quality_test():
    url = "http://127.0.0.1:8000/query"
    
    # 10 localized, realistic law enforcement queries in Kannada
    kannada_queries = [
        # --- Theft (ಕಳ್ಳತನ) ---
        "ಹಾಸನದಲ್ಲಿ ಬೈಕ್ ಕಳ್ಳತನವಾಗಿದ್ದರ ಬಗ್ಗೆ ಎಫ್‌ಐಆರ್ ವಿವರ ಕೊಡಿ.", 
        # (Give FIR details about a bike theft in Hassan.)
        
        "ಬೆಳಗಾವಿಯಲ್ಲಿ ವಾಹನ ಕಳ್ಳತನಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಕರಣಗಳ ಸಾರಾಂಶ ಕೊಡಿ.",
        # (Give a summary of vehicle theft cases in Belagavi.)
        
        "ಚಿನ್ನದ ಸರಗಳ್ಳತನ ಪ್ರಕರಣಗಳ ಮಾಹಿತಿ ಬೇಕು.",
        # (Need information on gold chain snatching cases.)

        # --- Assault (ಹಲ್ಲೆ) ---
        "ರಾತ್ರಿಯ ವೇಳೆ ಸಾರ್ವಜನಿಕ ಸ್ಥಳದಲ್ಲಿ ನಡೆದ ಹಲ್ಲೆ ಪ್ರಕರಣಗಳು.",
        # (Assault cases that happened in a public place at night.)
        
        "ಮಾರಣಾಂತಿಕ ಆಯುಧಗಳಿಂದ ಹಲ್ಲೆ ಮಾಡಿದ ಆರೋಪಿಗಳ ಪಟ್ಟಿ ಇದೆಯೇ?",
        # (Is there a list of accused who assaulted with deadly weapons?)

        # --- Missing Persons (ಕಾಣೆಯಾದ ವ್ಯಕ್ತಿ) ---
        "ಕಳೆದ ವಾರದಿಂದ ಕಾಣೆಯಾಗಿರುವ ಅಪ್ರಾಪ್ತ ಬಾಲಕಿಯರ ಬಗ್ಗೆ ಏನಾದರೂ ಮಾಹಿತಿ ಇದೆಯೇ?",
        # (Is there any information about minor girls missing since last week?)
        
        "ಬೆಂಗಳೂರಿನಲ್ಲಿ ವೃದ್ಧರು ಕಾಣೆಯಾಗಿರುವ ಇತ್ತೀಚಿನ ದೂರುಗಳು.",
        # (Recent complaints of elderly persons missing in Bengaluru.)

        # --- Cyber Crime & Fraud (ಸೈಬರ್ ವಂಚನೆ) ---
        "ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ವಂಚನೆ ಮತ್ತು ಒಟಿಪಿ ಹಂಚಿಕೆಯಿಂದ ಹಣ ಕಳೆದುಕೊಂಡ ಪ್ರಕರಣಗಳು.",
        # (Cases of losing money due to credit card fraud and OTP sharing.)
        
        "ಸಾಮಾಜಿಕ ಜಾಲತಾಣಗಳಲ್ಲಿ ನಕಲಿ ಖಾತೆ ತೆರೆದು ಬ್ಲ್ಯಾಕ್‌ಮೇಲ್ ಮಾಡುತ್ತಿರುವ ದೂರುಗಳು.",
        # (Complaints of blackmail by opening fake accounts on social media.)

        # --- Narcotics / Organised Crime (ಮಾದಕ ದ್ರವ್ಯ) ---
        "ಮಾದಕ ದ್ರವ್ಯ ಮಾರಾಟ ಜಾಲದ ವಿರುದ್ಧ ದಾಖಲಾಗಿರುವ ಇತ್ತೀಚಿನ ಎಫ್‌ಐಆರ್ ಯಾವುದು?"
        # (What is the recent FIR registered against a drug peddling network?)
    ]

    print("🚀 Firing Kannada Translation Test Suite...\n")
    
    for i, query in enumerate(kannada_queries, 1):
        payload = {
            "query": query,
            "filters_dict": None,
            "officer_id": "TEST-TRANSLATE"
        }
        
        try:
            print(f"[{i}/10] Firing Query: {query}")
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer_text", "").replace('\n', ' ')
                conf = data.get("confidence_band", "ERR")
                print(f"     ✅ Status: SUCCESS | Confidence: {conf}")
                print(f"     🧠 RAG Answer Snippet: {answer[:90]}...\n")
            else:
                print(f"     ❌ Status: FAILED (API returned {response.status_code})\n")
                
        except Exception as e:
            print(f"     ❌ Status: CRASHED ({e})\n")

    print("-" * 80)
    print("🏁 TRANSLATION TEST COMPLETE. Check your FastAPI console for the exact English strings.")

if __name__ == "__main__":
    run_translation_quality_test()