"""
Test the /history endpoint directly
"""
import requests
import json

# Test the endpoint
url = "http://localhost:8000/history"

print("=" * 60)
print("Testing /history endpoint")
print("=" * 60)
print(f"\n📡 Calling: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Response data:")
        print(json.dumps(data, indent=2))
        
        orders = data.get("orders", [])
        print(f"\n✅ Number of orders: {len(orders)}")
        
        if orders:
            print(f"\n📋 First order:")
            order = orders[0]
            print(f"  Restaurant: {order.get('restaurant_name')}")
            print(f"  Date: {order.get('date')}")
            print(f"  Items: {len(order.get('items', []))}")
            for item in order.get('items', []):
                print(f"    - {item.get('quantity')} {item.get('unit')} {item.get('product')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to server")
    print("   Make sure your FastAPI server is running on http://localhost:8000")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)

