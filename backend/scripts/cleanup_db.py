import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "attendance_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def cleanup():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Truncate tables to preserve schema but remove all data
        # Order matters due to foreign keys: salaries -> attendance -> employees
        cur.execute("TRUNCATE TABLE salaries, attendance, employees RESTART IDENTITY CASCADE;")
        
        conn.commit()
        print("Database cleaned successfully! All worker, attendance, and salary data removed.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Cleanup Error: {e}")

if __name__ == "__main__":
    cleanup()
