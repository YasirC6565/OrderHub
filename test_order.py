#!/usr/bin/env python3
"""Test the problematic order"""
from dotenv import load_dotenv
import os
load_dotenv()

import requests
import json

order_text = """3 Onion

1 Tom

3bg Chilli

2kg Rocket Chilli

2p Muki

3p Iceberg

1bx Orange"""

print("=" * 60)
print("Testing Order Submission")
print("=" * 60)
print(f"\nOrder text:\n{order_text}\n")

# Test with a restaurant name
data = {
    'Body': order_text,
    'RestaurantName': 'Test Restaurant'
}

print("📤 Sending order to /whatsapp endpoint...")
try:
    r = requests.post('http://localhost:8000/whatsapp', data=data, timeout=10)
    print(f"✅ Status Code: {r.status_code}\n")
    
    result = r.json()
    
    print(f"📊 Total orders processed: {len(result.get('orders', []))}")
    print(f"📋 Restaurant: {result.get('restaurant_name', 'N/A')}\n")
    
    # Check for errors
    saved_count = 0
    error_count = 0
    
    for i, order in enumerate(result.get('orders', []), 1):
        status = order.get('status', 'unknown')
        if status == 'saved':
            saved_count += 1
            parsed = order.get('parsed', {})
            print(f"✅ Order {i}: {parsed.get('quantity')} {parsed.get('unit')} {parsed.get('product')}")
            if order.get('errors'):
                print(f"   ⚠️  Errors: {order.get('errors')}")
        else:
            error_count += 1
            print(f"❌ Order {i}: Status = {status}")
            print(f"   Error: {order.get('error', 'Unknown error')}")
            print(f"   Message: {order.get('message', 'No message')}")
            if order.get('parsed'):
                parsed = order.get('parsed', {})
                print(f"   Parsed: {parsed.get('quantity')} {parsed.get('unit')} {parsed.get('product')}")
    
    print(f"\n📈 Summary: {saved_count} saved, {error_count} errors")
    
    # Check database
    print("\n" + "=" * 60)
    print("Checking Database")
    print("=" * 60)
    
    from src.saver import get_database_engine
    import pandas as pd
    
    engine = get_database_engine()
    query = """
        SELECT restaurant_name, product, quantity, unit, date, original_text
        FROM restaurant_orders
        WHERE restaurant_name = 'Test Restaurant'
        ORDER BY date DESC
        LIMIT 10
    """
    
    df = pd.read_sql(query, engine)
    
    if not df.empty:
        print(f"\n✅ Found {len(df)} orders in database for 'Test Restaurant'")
        print("\nRecent orders:")
        for idx, row in df.iterrows():
            print(f"  - {row['quantity']} {row['unit']} {row['product']} (Original: {row['original_text']})")
    else:
        print("\n❌ No orders found in database for 'Test Restaurant'")
        print("   This suggests the orders were not saved to the database.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

