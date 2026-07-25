import requests, os
from dotenv import load_dotenv

load_dotenv()
url = 'https://api.catalyst.zoho.in/quickml/v1/project/53326000000013024/rag/answer'
headers = {
    'CATALYST-ORG': '60079693511',
    'Authorization': f"Zoho-oauthtoken {os.getenv('CATALYST_API_KEY')}",
    'Content-Type': 'application/json'
}

payload = {
    'query': 'What is a Workflow in ZohoCRM?'
}
try:
    r = requests.post(url, headers=headers, json=payload)
    print('NO DOCUMENTS:', r.status_code, r.text)
except Exception as e:
    print('NO DOCUMENTS ERROR:', e)

payload_huge = {
    'query': 'What is a Workflow in ZohoCRM?',
    'documents': ['A' * 10000]
}
try:
    r3 = requests.post(url, headers=headers, json=payload_huge)
    print('HUGE TEXT:', r3.status_code, r3.text)
except Exception as e:
    print('HUGE TEXT ERROR:', e)
    
payload_huge_ids = {
    'query': 'What is a Workflow in ZohoCRM?',
    'documents': ['1234567890' * 100]
}
try:
    r4 = requests.post(url, headers=headers, json=payload_huge_ids)
    print('HUGE ID:', r4.status_code, r4.text)
except Exception as e:
    print('HUGE ID ERROR:', e)
