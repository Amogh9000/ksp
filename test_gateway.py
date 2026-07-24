import requests

url = "http://127.0.0.1:8000/query"

payload = {
    "query": "What is the likelihood of a robbery near Sami Circle tomorrow?",
    "officer_id": "TEST_OFFICER"
}

print("🚀 Sending request to gateway...")
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}\n")
print("Response JSON:")
print(response.json())