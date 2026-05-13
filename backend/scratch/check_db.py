from backend.database.db_connection import db
import os
from dotenv import load_dotenv

load_dotenv()

def check_employees():
    try:
        query = "SELECT * FROM employees"
        rows = db.execute_query(query, fetch=True)
        print(f"Employees in DB: {rows}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_employees()
