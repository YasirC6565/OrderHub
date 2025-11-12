"""
Quick script to check if the server is running
"""
import requests
import sys

url = "http://localhost:8000/history"

print("Checking if server is running...")
print(f"Testing: {url}")

try:
    response = requests.get(url, timeout=5)
    print(f"✅ Server is running! Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received: {len(data.get('orders', []))} orders")
    sys.exit(0)
except requests.exceptions.ConnectionError:
    print("❌ Server is NOT running or not accessible")
    print("   Start your server with: uvicorn src.main:app --reload")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

