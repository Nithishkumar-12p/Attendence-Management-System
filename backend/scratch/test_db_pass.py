import psycopg2
import os

passwords = ["postgres", "admin123", "123456", "root", "password", ""]

for p in passwords:
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=p,
            dbname="postgres"
        )
        print(f"SUCCESS: Password is '{p}'")
        conn.close()
        break
    except Exception as e:
        print(f"FAILED: Password '{p}' - {e}")
