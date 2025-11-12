"""
Simple script to verify the app is using PostgreSQL database
This will show SQL queries being executed
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Database Usage Verification")
print("=" * 60)

# Check what DATABASE_URL is being used
database_url = os.getenv("DATABASE_URL")
if database_url:
    # Mask password
    if "@" in database_url:
        parts = database_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split(":")
            if len(user_pass) >= 2:
                masked = f"{user_pass[0]}:****@{parts[1]}"
            else:
                masked = database_url
        else:
            masked = database_url
    else:
        masked = database_url
    
    print(f"\n✅ DATABASE_URL is set: {masked}")
    
    if "postgresql" in database_url.lower() or "postgres" in database_url.lower():
        print("✅ Using PostgreSQL database")
    else:
        print("⚠️  Not using PostgreSQL format")
else:
    print("❌ DATABASE_URL not found")

print("\n" + "=" * 60)
print("To verify database usage:")
print("1. Start your FastAPI server")
print("2. Watch the console output - you should see SQL queries")
print("3. When you save an order, you'll see INSERT queries")
print("4. When you load history, you'll see SELECT queries")
print("=" * 60)
print("\nExample SQL output you should see:")
print("  INSERT INTO restaurant_orders ...")
print("  SELECT * FROM restaurant_orders ...")
print("\nIf you see these queries, the app IS using PostgreSQL! ✅")

