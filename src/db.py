import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

POSTGRES_HOST=os.getenv("DB_HOST","localhost")
POSTGRES_PORT = int(os.getenv("DB_PORT",5432))
POSTGRES_USER = os.getenv("DB_USER","postgres")
POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
POSTGRES_DB = os.getenv("DB_NAME","orderhub")


def get_connection():
    return psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,          # change if you use another user
        password=POSTGRES_PASSWORD, # replace with your actual password
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )

def get_products():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, unit_synonyms FROM products;")
            rows = cur.fetchall()
            # e.g. [('Onion', ['bag','kilo','kg']), ('Potato', ...)]
            return rows

def get_restaurant_by_name(name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM restaurants WHERE name=%s;", (name,))
            return cur.fetchone()

def get_restaurant_by_phone(phone_number: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.name
                FROM restaurants r
                JOIN client_phone_numbers p ON r.id = p.client_id
                WHERE p.phone_number = %s;
            """, (phone_number,))
            return cur.fetchone()

