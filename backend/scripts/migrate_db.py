import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "attendance_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def migrate():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Add Employee Columns
        commands = [
            "ALTER TABLE employees ADD COLUMN IF NOT EXISTS aadhar_number VARCHAR(12);",
            "ALTER TABLE employees ADD COLUMN IF NOT EXISTS phone_number VARCHAR(15);",
            "ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_start_date DATE;",
            "ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_end_date DATE;",
            "ALTER TABLE employees ADD COLUMN IF NOT EXISTS working_hours_per_day NUMERIC(4, 2);",
            "ALTER TABLE employees ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            # Add Attendance Columns
            "ALTER TABLE attendance ADD COLUMN IF NOT EXISTS tools_count INTEGER DEFAULT 0;",
            "ALTER TABLE attendance ADD COLUMN IF NOT EXISTS tools_details TEXT;"
        ]

        for cmd in commands:
            try:
                cur.execute(cmd)
                print(f"Executed: {cmd}")
            except Exception as e:
                print(f"Failed to execute {cmd}: {e}")
                conn.rollback()
                continue

        conn.commit()
        print("Migration complete!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    migrate()
