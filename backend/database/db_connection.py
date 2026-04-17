import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

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
            if conn:
                conn.rollback()
            return None
        finally:
            self.release_connection(conn)

# Singleton Instance
db = DatabaseConnection()
