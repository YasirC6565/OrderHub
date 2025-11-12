from dotenv import load_dotenv
load_dotenv()

from src.saver import get_database_engine
import pandas as pd

engine = get_database_engine()
df = pd.read_sql(
    "SELECT restaurant_name, product, quantity, unit, original_text FROM restaurant_orders WHERE restaurant_name = 'Test Restaurant' ORDER BY date DESC LIMIT 7",
    engine
)

print(f"Orders in database: {len(df)}")
if not df.empty:
    print("\nRecent orders:")
    for idx, row in df.iterrows():
        print(f"  - {row['quantity']} {row['unit']} {row['product']} (Original: {row['original_text']})")
else:
    print("No orders found")

