"""
Test the history function to see what's happening
"""
import os
from dotenv import load_dotenv
from src.history import get_order_history

load_dotenv()

print("=" * 60)
print("Testing get_order_history() function")
print("=" * 60)

try:
    print("\n📡 Calling get_order_history()...")
    orders = get_order_history()
    print(f"✅ Function completed successfully!")
    print(f"📊 Number of orders returned: {len(orders)}")
    
    if orders:
        print("\n📋 Orders found:")
        for i, order in enumerate(orders[:3], 1):  # Show first 3
            print(f"\n  Order {i}:")
            print(f"    Restaurant: {order.get('restaurant_name')}")
            print(f"    Date: {order.get('date')}")
            print(f"    Items: {len(order.get('items', []))}")
            for item in order.get('items', [])[:2]:  # Show first 2 items
                print(f"      - {item.get('quantity')} {item.get('unit')} {item.get('product')}")
    else:
        print("\n⚠️  No orders returned (empty list)")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

