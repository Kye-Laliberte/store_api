from api.connect import get_connection
from os.path import exists 
import random
import psycopg2
import logging
from datetime import datetime
def setup(schema_path="sql/schema.sql"):
    
    if not exists(schema_path):
        raise FileNotFoundError(f"file not found: {schema_path}")
    
    with open(schema_path, "r", encoding="utf-8") as file:
            sql = file.read()
    
    with get_connection()as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            
            # Users
            cursor.execute("""
                INSERT INTO users (email, password_hash, created_at)
                VALUES
                ('alice@gmail.com', 'hash_alice', %s),
                       ('bob@outlook.com', 'hash_bob', %s)
                ON CONFLICT (email) DO NOTHING;
            """, (datetime.now(), datetime.now()))

            # Items
            cursor.execute("""
                INSERT INTO items (name, description, quantity, price)
                VALUES
                ('Keyboard', 'Mechanical keyboard', 10, 49.99),
                ('Mouse', 'Wireless mouse', 20, 19.99),
                ('Monitor', '24-inch monitor', 5, 149.99)
                ON CONFLICT (name) DO NOTHING;
            """)

            # Carts (one per user)
            cursor.execute("""
                INSERT INTO carts (user_id, purchase_date)
                SELECT id, %s FROM users
                ON CONFLICT (user_id) DO NOTHING;
            """, (datetime.now(),))

            ## Cart Items
            cursor.execute("""
                INSERT INTO cart_items (cart_id, item_id, quantity)
                SELECT c.id, i.id, 1
                FROM carts c
                JOIN items i ON i.name = 'Keyboard'
                WHERE c.user_id = (SELECT id FROM users WHERE email = 'alice@gmail.com')
                ON CONFLICT (cart_id, item_id) DO NOTHING;
            """)
            # Orders
            cursor.execute("""
                INSERT INTO orders (user_id, total_price, order_date)
                SELECT id, 49.99, %s FROM users
                WHERE email = 'alice@gmail.com';
            """, (datetime.now(),))
            #ON CONFLICT (user_id) DO NOTHING
            # Order Items
            cursor.execute("""
                INSERT INTO order_items (order_id, item_id, quantity, price_at_order)
                SELECT o.id, i.id, 1 , i.price
                FROM orders o
                JOIN items i ON i.name = 'Keyboard'
                WHERE o.user_id = (SELECT id FROM users WHERE email = 'alice@gmail.com')
                ;
            """)
def setup_db():
    try:
        setup()
        logging.info("Database setup completed successfully.")
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    setup_db()