import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "attendance_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def reset_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
            schema_content = f.read()

        cur.execute(schema_content)
        conn.commit()
        print("Database schema updated successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Schema Update Error: {e}")

if __name__ == "__main__":
    reset_db()
