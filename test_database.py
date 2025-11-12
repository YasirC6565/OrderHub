"""
Test script to verify PostgreSQL database connection and data
"""
import os
from dotenv import load_dotenv
from src.saver import get_database_engine
import pandas as pd

load_dotenv()

def test_database_connection():
    """Test database connection and show data"""
    print("=" * 60)
    print("Testing PostgreSQL Database Connection")
    print("=" * 60)
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        return
    
    # Mask password for display
    if "@" in database_url:
        parts = database_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split(":")
            if len(user_pass) >= 2:
                masked_url = f"{user_pass[0]}:****@{parts[1]}"
            else:
                masked_url = database_url
        else:
            masked_url = database_url
    else:
        masked_url = database_url
    
    print(f"\n✅ DATABASE_URL found: {masked_url}")
    
    try:
        # Get engine
        print("\n📡 Connecting to database...")
        engine = get_database_engine()
        print("✅ Database engine created successfully")
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful!")
            
            # Check if table exists
            print("\n🔍 Checking if 'restaurant_orders' table exists...")
            check_table_query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'restaurant_orders'
                );
            """
            result = pd.read_sql(check_table_query, conn)
            table_exists = result.iloc[0, 0]
            
            if table_exists:
                print("✅ Table 'restaurant_orders' exists")
                
                # Count rows
                print("\n📊 Counting rows in restaurant_orders table...")
                count_query = "SELECT COUNT(*) as total FROM restaurant_orders;"
                count_result = pd.read_sql(count_query, conn)
                total_rows = count_result.iloc[0, 0]
                print(f"✅ Total rows in table: {total_rows}")
                
                if total_rows > 0:
                    # Show recent orders
                    print("\n📋 Showing last 5 orders from database:")
                    print("-" * 60)
                    recent_query = """
                        SELECT 
                            id,
                            restaurant_id,
                            restaurant_name,
                            quantity,
                            unit,
                            product,
                            date,
                            need_attention
                        FROM restaurant_orders
                        WHERE product IS NOT NULL AND product != ''
                        ORDER BY date DESC
                        LIMIT 5;
                    """
                    recent_orders = pd.read_sql(recent_query, conn)
                    print(recent_orders.to_string(index=False))
                    
                    # Show recent messages
                    print("\n💬 Showing last 5 messages from database:")
                    print("-" * 60)
                    messages_query = """
                        SELECT 
                            id,
                            restaurant_id,
                            restaurant_name,
                            message,
                            date,
                            need_attention
                        FROM restaurant_orders
                        WHERE message IS NOT NULL AND message != ''
                        ORDER BY date DESC
                        LIMIT 5;
                    """
                    recent_messages = pd.read_sql(messages_query, conn)
                    if len(recent_messages) > 0:
                        print(recent_messages.to_string(index=False))
                    else:
                        print("No messages found")
                else:
                    print("⚠️  Table is empty - no data yet")
                    
                # Show table structure
                print("\n📐 Table structure:")
                print("-" * 60)
                structure_query = """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' 
                    AND table_name = 'restaurant_orders'
                    ORDER BY ordinal_position;
                """
                structure = pd.read_sql(structure_query, conn)
                print(structure.to_string(index=False))
                
            else:
                print("❌ ERROR: Table 'restaurant_orders' does not exist!")
                print("   Please create the table using the schema provided.")
        
        print("\n" + "=" * 60)
        print("✅ Database test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()

