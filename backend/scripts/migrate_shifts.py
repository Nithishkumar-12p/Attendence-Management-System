import os, sys
# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.database.db_connection import db

def migrate_shifts():
    print("Migrating: Creating shifts table and updating employees...")
    
    # 1. Create shifts table
    create_shifts_query = """
    CREATE TABLE IF NOT EXISTS shifts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        working_hours NUMERIC(4,2) NOT NULL DEFAULT 8.0,
        grace_period INTEGER DEFAULT 15,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    db.execute_query(create_shifts_query)
    
    # 2. Add shift_id to employees table if it doesn't exist
    add_col_query = """
    DO $$ 
    BEGIN 
        IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'employees' AND COLUMN_NAME = 'shift_id') THEN
            ALTER TABLE employees ADD COLUMN shift_id INTEGER REFERENCES shifts(id);
        END IF;
    END $$;
    """
    db.execute_query(add_col_query)
    
    # 3. Seed default "General Shift" from existing settings
    # Try to get current settings
    settings = {}
    rows = db.execute_query("SELECT key, value FROM settings WHERE key IN ('shift_start_time', 'shift_end_time', 'grace_period', 'default_working_hours')", fetch=True)
    if rows:
        for r in rows:
            settings[r[0]] = r[1]
    
    start_time = settings.get('shift_start_time', '09:00')
    end_time = settings.get('shift_end_time', '18:00')
    grace = int(settings.get('grace_period', 15))
    work_hrs = float(settings.get('default_working_hours', 8.0))
    
    # Check if a default shift already exists
    check_shift = db.execute_query("SELECT id FROM shifts WHERE name = 'General Shift'", fetch=True)
    if not check_shift:
        insert_shift = """
        INSERT INTO shifts (name, start_time, end_time, working_hours, grace_period)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        """
        result = db.execute_query(insert_shift, ('General Shift', start_time, end_time, work_hrs, grace), fetch=True)
        shift_id = result[0][0]
        print(f"Created 'General Shift' with ID: {shift_id}")
    else:
        shift_id = check_shift[0][0]
        print(f"'General Shift' already exists with ID: {shift_id}")
        
    # 4. Update all employees to point to this shift_id (only if they are NULL)
    update_emp_query = "UPDATE employees SET shift_id = %s WHERE shift_id IS NULL"
    db.execute_query(update_emp_query, (shift_id,))
    print("Updated employees to default shift.")
    
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate_shifts()
