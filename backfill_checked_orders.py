#!/usr/bin/env python3
"""
Backfill script to populate checked_orders table with existing orders from restaurant_orders.
This will create entries for all restaurant orders that are grouped by restaurant_name and date.
"""
from dotenv import load_dotenv
load_dotenv()

from src.saver import get_database_engine
from sqlalchemy import text
from datetime import datetime

def backfill_checked_orders():
    """Backfill checked_orders table with existing orders"""
    engine = get_database_engine()
    
    print("🔄 Starting backfill of checked_orders table...")
    
    try:
        # Get all unique restaurant_name + date combinations with product counts
        query = text("""
            SELECT 
                restaurant_name,
                DATE(date) as order_date,
                COUNT(*) as product_count
            FROM restaurant_orders
            WHERE product IS NOT NULL 
                AND product != ''
            GROUP BY restaurant_name, DATE(date)
            ORDER BY order_date DESC, restaurant_name
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
            
            print(f"📊 Found {len(rows)} unique restaurant/date combinations")
            
            inserted = 0
            updated = 0
            errors = 0
            
            for restaurant_name, order_date, product_count in rows:
                try:
                    insert_query = text("""
                        INSERT INTO checked_orders (restaurant_name, order_date, checked_at, amount_of_products)
                        VALUES (:restaurant_name, :order_date, :checked_at, :amount_of_products)
                        ON CONFLICT (restaurant_name, order_date) DO UPDATE
                        SET checked_at = COALESCE(checked_orders.checked_at, :checked_at),
                            amount_of_products = :amount_of_products
                    """)
                    
                    with engine.begin() as trans_conn:
                        result = trans_conn.execute(insert_query, {
                            "restaurant_name": restaurant_name,
                            "order_date": order_date,
                            "checked_at": datetime.now(),
                            "amount_of_products": product_count
                        })
                        
                        if result.rowcount > 0:
                            inserted += 1
                            print(f"✅ Inserted: {restaurant_name} on {order_date} ({product_count} products)")
                        else:
                            updated += 1
                            print(f"ℹ️  Updated: {restaurant_name} on {order_date} ({product_count} products)")
                
                except Exception as e:
                    errors += 1
                    print(f"❌ Error processing {restaurant_name} on {order_date}: {e}")
            
            print(f"\n📈 Backfill complete:")
            print(f"   ✅ Inserted: {inserted}")
            print(f"   ℹ️  Updated: {updated}")
            print(f"   ❌ Errors: {errors}")
            print(f"   📊 Total processed: {len(rows)}")
    
    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    backfill_checked_orders()

