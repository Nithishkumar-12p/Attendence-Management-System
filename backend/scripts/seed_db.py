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
    
    today = datetime.now()
    
    # 1. Fetch all existing active employees
    print("Fetching active employees...")
    query = "SELECT employee_id FROM employees WHERE is_active = TRUE"
    records = db.execute_query(query, fetch=True)
    employee_ids = [r[0] for r in records]
    
    print(f"Generating data for {len(employee_ids)} active employees.")

    # 2. Insert Attendance for the last 7 days
    print("Seeding attendance for the last 7 days...")
    status_options = ['P', 'P', 'P', 'P', 'A', 'HD', 'P', 'P'] # Weightage towards Present

    records_count = 0
    # Seed from 6 days ago up to today (inclusive)
    for day_offset in range(7):
        date_obj = today - timedelta(days=day_offset)
        date = date_obj.strftime('%Y-%m-%d')
        
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
    
    # 3. Seed Salaries for the current month
    print(f"Seeding salaries for {today.month}/{today.year}...")
    from backend.models.salary import SalaryModel
    salary_count = 0
    for emp_id in employee_ids:
        res = SalaryModel.calculate_monthly_salary(emp_id, today.month, today.year)
        if res:
            salary_count += 1
    print(f"Successfully seeded {salary_count} salary records.")

    print("Seeding complete!")

if __name__ == "__main__":
    seed_random_data()
