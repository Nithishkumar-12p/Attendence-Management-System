import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

def initialize_database():
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")

    # Connect to default postgres DB to create the new one
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cursor.fetchone()

        if not exists:
            print(f"Database {dbname} not found. Creating...")
            cursor.execute(f"CREATE DATABASE {dbname}")
            print(f"Database {dbname} created.")
        else:
            print(f"Database {dbname} already exists.")

        cursor.close()
        conn.close()

        # Now connect to the new database and run schema.sql
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cursor = conn.cursor()

        # FIXED PATH: schema.sql is in backend/database/
        schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql'))
        print(f"Applying schema from: {schema_path}")
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        with open(schema_path, 'r') as f:
            cursor.execute(f.read())
        
        conn.commit()
        print("Schema applied successfully.")
        cursor.close()
        conn.close()

    except psycopg2.Error as pe:
        print(f"PostgreSQL Error: {pe}")
        print(f"Details: host={host}, port={port}, user={user}, dbname={dbname}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    initialize_database()
