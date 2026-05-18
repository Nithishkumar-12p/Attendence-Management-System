import os
import sys
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Try loading .env from multiple fallback directories to support both development and packaged environments
dotenv_paths = []

# 1. If running as a bundled executable, look next to the executable
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    # Next to backend.exe (usually in resources/ in packaged Electron app)
    dotenv_paths.append(os.path.join(exe_dir, '.env'))
    # In the resources directory (fallback)
    dotenv_paths.append(os.path.join(exe_dir, '..', '.env'))
    # Next to the main application executable (two levels up from backend.exe)
    dotenv_paths.append(os.path.join(exe_dir, '..', '..', '.env'))

# 2. Development paths
# Next to db_connection.py's parent (backend/.env)
dotenv_paths.append(os.path.join(os.path.dirname(__file__), '..', '.env'))
# Root folder (.env)
dotenv_paths.append(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
# Current working directory
dotenv_paths.append(os.path.join(os.getcwd(), '.env'))
dotenv_paths.append(os.path.join(os.getcwd(), 'backend', '.env'))

# Load the first .env that exists
loaded = False
for path_to_try in dotenv_paths:
    normalized_path = os.path.abspath(path_to_try)
    if os.path.exists(normalized_path):
        load_dotenv(normalized_path)
        print(f"PostgreSQL Connection: Loaded .env from {normalized_path}")
        loaded = True
        break

if not loaded:
    # Fallback to default load_dotenv() which searches the current working directory
    load_dotenv()
    print("PostgreSQL Connection: No specific .env file found. Loading from default env variables.")


class DatabaseConnection:
    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls.initialize_pool()
        return cls._instance

    @classmethod
    def initialize_pool(cls):
        try:
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME")
            )
            print("PostgreSQL connection pool initialized successfully.")
        except Exception as e:
            print(f"Error initializing PostgreSQL connection pool: {e}")

    def get_connection(self):
        if self._connection_pool:
            return self._connection_pool.getconn()
        return None

    def release_connection(self, conn):
        if self._connection_pool and conn:
            self._connection_pool.putconn(conn)

    def execute_query(self, query, params=None, fetch=False):
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                data = None
                if fetch:
                    data = cursor.fetchall()
                conn.commit()
                return data if fetch else True
        except Exception as e:
            print(f"Database Query Error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            if conn:
                conn.rollback()
            return None
        finally:
            self.release_connection(conn)

# Singleton Instance
db = DatabaseConnection()
