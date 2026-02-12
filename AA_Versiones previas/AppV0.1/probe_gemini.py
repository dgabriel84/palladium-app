import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
print(f"Key loaded: {GOOGLE_API_KEY[:5]}...")

models_to_try = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-pro",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest"
]

base_url = "https://generativelanguage.googleapis.com/v1beta/models/"

payload = {
    "contents": [{
        "role": "user",
        "parts": [{"text": "Hello"}]
    }]
}
headers = {"Content-Type": "application/json"}

for model in models_to_try:
    print(f"--- Probing {model} ---")
    url = f"{base_url}{model}:generateContent?key={GOOGLE_API_KEY}"
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS with {model}!")
            break
        else:
            print(f"Fail: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
