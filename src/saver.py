import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from src.logger import log_correction

# Create a singleton engine that's reused across all database operations
# This is much faster than creating a new engine on every call
_engine = None

def get_database_engine():
    """Get SQLAlchemy engine with proper connection string format.
    
    Uses the same DATABASE_URL as the existing database connections (db.py).
    Handles Railway's postgres:// format and converts to postgresql+psycopg2:// for SQLAlchemy.
    Creates and reuses a singleton engine for better performance.
    """
    global _engine
    if _engine is not None:
        return _engine
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Railway's DATABASE_URL might use postgres:// instead of postgresql://
    # Convert to postgresql:// first (like db.py does)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Ensure the connection string uses psycopg2 driver for SQLAlchemy
    if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+psycopg2://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    # Create engine with connection pooling for better performance
    _engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=3600,   # Recycle connections after 1 hour
        pool_timeout=10,     # Timeout for getting connection from pool
        connect_args={"connect_timeout": 10},  # Connection timeout
        echo=True            # Set to True for SQL debugging - shows actual SQL queries
    )
    return _engine


def save_order(validated_output: dict, restaurant_id: int, restaurant_name: str, filepath = None):
    # Allow saving even if product is missing (save with errors)
    if not validated_output.get("validated"):
        return {
            "status": "skipped",
            "errors": validated_output.get("errors", []),
            "raw_message": validated_output.get("raw_message", ""),
            "parsed": validated_output.get("validated", {})
        }

    engine = get_database_engine()

    validated = validated_output["validated"]
    # Combine errors and red_alerts for the corrections column
    all_errors = validated_output.get("errors", []) + validated_output.get("red_alerts", [])
    errors = "; ".join(all_errors) if all_errors else None
    raw_message = validated_output.get("raw_message", "")
    need_attention = bool(validated_output.get("red_alerts"))
    
    # Mark as needing attention if there are red_alerts (stored in corrections column)
    if validated_output.get("red_alerts"):
        errors = errors if errors else "RED ALERT: " + "; ".join(validated_output.get("red_alerts", []))
    
    # Handle restaurant_id: if None, we can't insert due to foreign key constraint
    # Set to None in the database (if column allows NULL) or handle gracefully
    # Since restaurant_id is a foreign key, we'll pass None and let the database handle it
    # If the column doesn't allow NULL, this will need to be handled at the schema level
    db_restaurant_id = restaurant_id if restaurant_id is not None else None
    
    # Create DataFrame with data matching database schema
    data = {
        "restaurant_id": [db_restaurant_id],
        "restaurant_name": [restaurant_name],
        "quantity": [validated.get("quantity")],
        "unit": [validated.get("unit")],
        "product": [validated.get("product")],
        "corrections": [errors],
        "date": [datetime.now()],  # Use datetime object for TIMESTAMP
        "original_text": [raw_message],
        "need_attention": [need_attention],
        "message": [raw_message]  # message column
    }
    
    df = pd.DataFrame(data)
    
    # Insert into database with error handling
    try:
        # Try with schema-qualified table name first, fallback to just table name
        df.to_sql("restaurant_orders", engine, if_exists="append", index=False, schema="public")
    except Exception as e:
        # Handle foreign key constraint violations or other database errors
        error_msg = str(e)
        print(f"⚠️  Database error details: {error_msg}")
        print(f"   Error type: {type(e).__name__}")
        
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            print(f"⚠️  Table 'restaurant_orders' may not exist in the database")
            print(f"   Please verify the table exists with: SELECT * FROM restaurant_orders LIMIT 1;")
            return {
                "status": "error",
                "error": "table_not_found",
                "message": "Table 'restaurant_orders' does not exist in database",
                "parsed": validated,
                "raw_message": raw_message
            }
        elif "foreign key" in error_msg.lower() or "violates foreign key constraint" in error_msg.lower():
            print(f"⚠️  Database error: Foreign key constraint violation for restaurant_id={restaurant_id}")
            print(f"   This order will not be saved. Error: {error_msg}")
            return {
                "status": "error",
                "error": "restaurant_not_found",
                "message": f"Restaurant ID {restaurant_id} does not exist in database",
                "parsed": validated,
                "raw_message": raw_message
            }
        else:
            # Re-raise other database errors with full details
            print(f"⚠️  Database error: {error_msg}")
            raise

    # ✅ Log corrections separately if errors or red_alerts exist
    if all_errors:
        log_correction(
            restaurant=restaurant_name,
            raw_message=validated_output.get("raw_message", ""),
            corrections=all_errors
        )

    # Note: For orders, the full message body is saved to conversations at the webhook level
    # to avoid saving duplicate messages for each line item. This function only saves individual
    # order line items to restaurant_orders table.

    # Return status with detailed info
    return {
        "status": "saved",
        "parsed": validated,
        "raw_message": raw_message,
        "errors": validated_output.get("errors", [])
    }


def save_to_conversations(message: str, restaurant_id: int, restaurant_name: str, direction: str = "incoming", parent_message_id: int = None):
    """
    Save a message to the conversations table.
    
    Args:
        message: The message text
        restaurant_id: Restaurant ID (can be None)
        restaurant_name: Restaurant name
        direction: 'incoming' or 'outgoing' (default: 'incoming')
        parent_message_id: ID of parent message if this is a reply (default: None)
    """
    engine = get_database_engine()
    db_restaurant_id = restaurant_id if restaurant_id is not None else None
    
    # Create DataFrame with data matching conversations table schema
    data = {
        "restaurant_id": [db_restaurant_id],
        "restaurant_name": [restaurant_name],
        "message": [message],
        "direction": [direction],
        "parent_message_id": [parent_message_id],
        "created_at": [datetime.now()]
    }
    
    df = pd.DataFrame(data)
    
    # Insert into conversations table with error handling
    try:
        df.to_sql("conversations", engine, if_exists="append", index=False, schema="public")
        print(f"✅ Message saved to conversations table: {restaurant_name} - {direction}")
    except Exception as e:
        error_msg = str(e)
        # Don't fail the whole operation if conversations table doesn't exist or has issues
        print(f"⚠️  Could not save to conversations table: {error_msg}")
        # Continue execution - this is not critical for the main flow


def save_message(message: str, restaurant_id: int, restaurant_name: str, filepath = None):
    """
    Save a natural conversation message (not an order) to the database.
    Only fills: restaurant_id, restaurant_name, date, and message columns.
    All order-related columns (quantity, unit, product) remain empty.
    Messages are flagged with need_attention=True for review.
    Also saves to conversations table.
    """
    engine = get_database_engine()
    
    # Handle restaurant_id: if None, we can't insert due to foreign key constraint
    # Set to None in the database (if column allows NULL) or handle gracefully
    db_restaurant_id = restaurant_id if restaurant_id is not None else None
    
    # Create DataFrame with data matching database schema
    data = {
        "restaurant_id": [db_restaurant_id],
        "restaurant_name": [restaurant_name],
        "quantity": [None],  # empty for messages
        "unit": [None],  # empty for messages
        "product": [None],  # empty for messages
        "corrections": [None],  # empty for messages
        "date": [datetime.now()],  # Use datetime object for TIMESTAMP
        "original_text": [None],  # empty for messages
        "need_attention": [True],  # messages need review
        "message": [message]  # message column
    }
    
    df = pd.DataFrame(data)
    
    # Insert into database with error handling
    try:
        df.to_sql("restaurant_orders", engine, if_exists="append", index=False)
    except Exception as e:
        # Handle foreign key constraint violations or other database errors
        error_msg = str(e)
        if "foreign key" in error_msg.lower() or "violates foreign key constraint" in error_msg.lower():
            print(f"⚠️  Database error: Foreign key constraint violation for restaurant_id={restaurant_id}")
            print(f"   This message will not be saved. Error: {error_msg}")
            return {
                "status": "error",
                "error": "restaurant_not_found",
                "message": f"Restaurant ID {restaurant_id} does not exist in database",
                "restaurant_name": restaurant_name
            }
        else:
            # Re-raise other database errors
            print(f"⚠️  Database error: {error_msg}")
            raise
    
    # Also save to conversations table
    save_to_conversations(message, restaurant_id, restaurant_name, direction="incoming")
    
    return {
        "status": "message_saved",
        "message": message,
        "restaurant_name": restaurant_name
    }
