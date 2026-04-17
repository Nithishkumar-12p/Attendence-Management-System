import os, sys
# Add project root (two levels up from this file: backend/database/ -> project root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.database.db_connection import db



def migrate_settings():
    print("Migrating: Creating settings table...")
    
    # Create table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS settings (
        key VARCHAR(100) PRIMARY KEY,
        value TEXT NOT NULL,
        description TEXT
    );
    """
    db.execute_query(create_table_query)
    
    # Initial seeds
    seeds = [
        ('company_name', 'VIDVAT SOLUTIONS', 'Display name of the organization'),
        ('shift_start_time', '09:00', 'Standard shift entry time (HH:MM)'),
        ('shift_end_time', '18:00', 'Standard shift exit time (HH:MM)'),
        ('grace_period', '15', 'Late arrival grace period in minutes'),
        ('default_working_hours', '8.0', 'Standard daily working hours for payroll')
    ]
    
    for key, value, desc in seeds:
        check_query = "SELECT 1 FROM settings WHERE key = %s"
        if not db.execute_query(check_query, (key,), fetch=True):
            insert_query = "INSERT INTO settings (key, value, description) VALUES (%s, %s, %s)"
            db.execute_query(insert_query, (key, value, desc))
            print(f"Seeded: {key}")
    
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate_settings()
