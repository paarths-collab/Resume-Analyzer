import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Support both DATABASE_URL (Neon) or individual env vars (Docker)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Using Neon or connection string
    print(f"Connecting to Neon PostgreSQL...")
else:
    # Fallback to individual env vars (Docker)
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5555')),
        'user': os.getenv('DB_USER', 'resumeuser'),
        'password': os.getenv('DB_PASSWORD', 'resumepass123'),
        'database': os.getenv('DB_NAME', 'resumedb')
    }
    print(f"Connecting to local PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        if DATABASE_URL:
            # Neon connection with SSL
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            # Local Docker connection
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor(commit=True):
    """Context manager for database cursor"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()