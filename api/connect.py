import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv
from pathlib import Path

@contextmanager
def get_connection():

    dotenv_path = Path(".env")
    load_dotenv(dotenv_path=dotenv_path)
    

    conn= psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
        )
    

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()