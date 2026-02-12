import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
print(f"Key loaded: {GOOGLE_API_KEY[:5]}...{GOOGLE_API_KEY[-5:] if GOOGLE_API_KEY else 'None'}")

# URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
# Trying 1.5 Flash as fallback if 2.0 fails
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

print(f"Testing URL: {URL}")

payload = {
    "contents": [{
        "role": "user",
        "parts": [{"text": "Hola, ¿cómo estás?"}]
    }]
}

url_with_key = f"{URL}?key={GOOGLE_API_KEY}"
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url_with_key, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
