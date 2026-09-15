
from api.connect import get_connection
from os.path import exists 
import psycopg2
import logging
from datetime import datetime
def seed_data():
   """   Seeds the database with initial data for users, items, carts, and orders.
    This function connects to the database, and inserts sample data into the users, items, carts, and orders tables."""
   with get_connection()as conn:
        with conn.cursor() as cursor:

            
            cursor.execute("""
                INSERT INTO users (email, password_hash, created_at, status)
                VALUES
                ('alice@gmail.com', 'hash_alice', %s, 'active'),
                       ('bob@outlook.com', 'hash_bob', %s, 'active')
                ON CONFLICT (email) DO NOTHING;""", 
                (datetime.now(), datetime.now()))

            # Items
            cursor.execute("""
                INSERT INTO items (name, description, quantity, price)
                VALUES
                ('Keyboard', 'Mechanical keyboard', 10, 49.99),
                ('Mouse', 'Wireless mouse', 20, 19.99),
                ('Monitor', '24-inch monitor', 5, 149.99),
                ('Pens','32 colored pen set',50,'5.99'),
                ('ipad','touch screen',3, 250.99),
                ('lazer ponter','Zap Zap', 8, 15.39)
                ON CONFLICT (name) DO NOTHING;""")

            

           
            
def setup_db():
    try:
        seed_data()
        logging.info("Database setup completed successfully.")
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    setup_db()