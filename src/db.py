import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    """Get database connection, handles errors gracefully
    
    Supports Railway's DATABASE_URL format (postgresql://user:pass@host:port/db)
    Falls back to individual environment variables if DATABASE_URL is not set.
    """
    try:
        # Railway provides DATABASE_URL automatically when you add a Postgres service
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # Railway's DATABASE_URL might use postgres:// instead of postgresql://
            # psycopg2 requires postgresql://, so we fix it if needed
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            return psycopg2.connect(database_url)
        else:
            # Fall back to individual environment variables (for local development)
            POSTGRES_HOST = os.getenv("DB_HOST", "localhost")
            POSTGRES_PORT = int(os.getenv("DB_PORT", 5432))
            POSTGRES_USER = os.getenv("DB_USER", "postgres")
            POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
            POSTGRES_DB = os.getenv("DB_NAME", "orderhub")
            
            return psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT
            )
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("⚠️  App will continue but database features will be unavailable")
        return None

def get_products():
    """Get products from PostgreSQL database"""
    conn = get_connection()
    if not conn:
        print("⚠️  Database not available, returning empty product list")
        return []
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, unit_synonyms FROM products;")
                rows = cur.fetchall()
                # e.g. [('Onion', ['bag','kilo','kg']), ('Potato', ...)]
                return rows
    except Exception as e:
        print(f"⚠️  Error fetching products: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_restaurant_by_name(name: str):
    """Get restaurant by name from PostgreSQL"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM restaurants WHERE name=%s;", (name,))
                return cur.fetchone()
    except Exception as e:
        print(f"⚠️  Error fetching restaurant by name: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_restaurant_by_phone(phone_number: str):
    """Get restaurant by phone from PostgreSQL"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT r.id, r.name
                    FROM restaurants r
                    JOIN client_phone_numbers p ON r.id = p.client_id
                    WHERE p.phone_number = %s;
                """, (phone_number,))
                return cur.fetchone()
    except Exception as e:
        print(f"⚠️  Error fetching restaurant by phone: {e}")
        return None
    finally:
        if conn:
            conn.close()

