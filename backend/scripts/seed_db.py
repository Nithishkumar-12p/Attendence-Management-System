import os
import sys
import random
from datetime import datetime, timedelta

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.database.db_connection import db

def seed_random_data():
    print("Starting database seeding...")

    # Names and Designations for random generation
    names = [
        "Amit Kumar", "Priya Singh", "Rajesh Sharma", "Sunita Verma", 
        "Vijay Yadav", "Anjali Gupta", "Suresh Raina", "Meena Kumari",
        "Deepak Patel", "Pooja Reddy", "Manoj Tiwari", "Kavita Rao",
        "Sanjay Mishra", "Ritu Goyal", "Arun Varma", "Sneha Iyer"
    ]
    designations = ["Helper", "Supervisor", "Technician", "Operator", "Manager", "Security"]
    
    # 1. Insert Employees
    employee_ids = []
    print(f"Seeding {len(names)} employees...")
    
    for i, name in enumerate(names):
        salary = random.randint(15000, 45000)
        designation = random.choice(designations)
        aadhar = str(random.randint(100000000000, 999999999999))
        phone = str(random.randint(7000000000, 9999999999))
        joining_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
        
        query = """
            INSERT INTO employees (name, basic_salary, designation, joining_date, aadhar_number, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING employee_id
        """
        params = (name, salary, designation, joining_date, aadhar, phone)
        result = db.execute_query(query, params, fetch=True)
        if result:
            employee_ids.append(result[0][0])

    print(f"Successfully seeded {len(employee_ids)} employees.")

    # 2. Insert Attendance for the last 7 days
    print("Seeding attendance for the last 7 days...")
    today = datetime.now()
    status_options = ['P', 'P', 'P', 'P', 'A', 'HD', 'P', 'P'] # Weightage towards Present

    records_count = 0
    for day_offset in range(7):
        date = (today - timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        for emp_id in employee_ids:
            status = random.choice(status_options)
            in_time = None
            out_time = None
            is_late = False
            
            if status in ['P', 'HD']:
                # Random time between 8:30 and 9:30
                hour = random.randint(8, 9)
                minute = random.randint(0, 59)
                in_time = f"{hour:02d}:{minute:02d}:00"
                if hour > 9 or (hour == 9 and minute > 15):
                    is_late = True
                
                # Random out time around 18:00
                out_hour = random.randint(17, 19)
                out_minute = random.randint(0, 59)
                out_time = f"{out_hour:02d}:{out_minute:02d}:00"

            query = """
                INSERT INTO attendance (employee_id, date, status, in_time, out_time, is_late, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (employee_id, date) DO NOTHING
            """
            params = (emp_id, date, status, in_time, out_time, is_late, "Auto-seeded data")
            if db.execute_query(query, params):
                records_count += 1

    print(f"Successfully seeded {records_count} attendance records.")
    print("Seeding complete!")

if __name__ == "__main__":
    seed_random_data()
