import time
import requests
import os
import sys
import io

# Force UTF-8 output on Windows terminals
_stdout_encoding = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'
if _stdout_encoding.lower() != 'utf-8' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import os
from dotenv import load_dotenv

print("🚀 Starting isolated RAG Synthesis Fallback Test...")
load_dotenv()

# Simulate the chunk data passed to Catalyst
chunks = [
    {"fir_id": "100040011202400001", "text": "EXACT MATCHING FIR RECORD: Crime Against Property"},
    {"fir_id": "100040011202400013", "text": "Rioting incident near Naik Zila, Belagavi."}
]
search_query = "What crimes occurred near Belagavi?"

print(f"\n🧠 [PHASE 2] Synthesizing report via Zoho Catalyst QuickML...")
gen_start = time.perf_counter()

url = "https://api.catalyst.zoho.in/quickml/v1/project/53326000000013024/rag/answer"
headers = {
    "CATALYST-ORG": "60079693511",
    "Authorization": f"Zoho-oauthtoken {os.getenv('CATALYST_API_KEY')}",
    "Content-Type": "application/json"
}

payload = {
    "query": search_query,
    "documents": [str(c.get("fir_id", "")) for c in chunks]
}

try:
    print("📡 Sending payload to Catalyst API...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        raw_answer_text = data.get("answer", data.get("response", "No answer returned by Catalyst."))
        print(f"✅ [CATALYST SUCCESS] {raw_answer_text}")
    else:
        print(f"🛑 [CATALYST ERROR] {response.status_code}: {response.text}")
        print(f"🔄 [FALLBACK] Triggering Groq Gateway Fallback...")
        
        # Test the Groq fallback!
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), "query"))
        from llm_gateway import LLMGateway
        gateway = LLMGateway()
        context_string = "\n".join([c.get("text", "") for c in chunks])
        raw_answer_text = gateway.generate(prompt=search_query, context=context_string)
        
except Exception as e:
    print(f"🛑 [CATALYST EXCEPTION] {e}")
    print(f"🔄 [FALLBACK] Triggering Groq Gateway Fallback...")
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "query"))
    from llm_gateway import LLMGateway
    gateway = LLMGateway()
    context_string = "\n".join([c.get("text", "") for c in chunks])
    raw_answer_text = gateway.generate(prompt=search_query, context=context_string)

generation_ms = round((time.perf_counter() - gen_start) * 1000, 2)
print(f"\n🎯 [FINAL OUTPUT] (Took {generation_ms}ms)")
print("="*50)
print(raw_answer_text.strip())
print("="*50)
print("✅ Test Completed successfully without loading heavy vector models.")
