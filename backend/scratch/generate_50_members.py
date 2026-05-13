import psycopg2
import random
from datetime import datetime, date

def generate_50_members():
    try:
        conn = psycopg2.connect(
            dbname='attendance_db',
            user='postgres',
            password='123456',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()

        # 1. Clear existing data to start fresh with exactly 50
        cur.execute("DELETE FROM attendance")
        cur.execute("DELETE FROM employees")
        
        # 2. Add 50 employees
        designations = ['Welder', 'Fitter', 'Electrician', 'Operator', 'Supervisor', 'Helper']
        today = date.today()
        
        print("Generating 50 employees...")
        for i in range(1, 51):
            name = f"Test User {i:02d}"
            salary = random.randint(15000, 25000)
            designation = random.choice(designations)
            aadhar = f"{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
            phone = f"9{random.randint(100000000, 999999999)}"
            
            cur.execute("""
                INSERT INTO employees (employee_id, name, basic_salary, designation, joining_date, aadhar_number, phone_number, shift_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """, (i, name, salary, designation, today, aadhar, phone))

        # 3. Add attendance for today
        print("Generating attendance for today...")
        for i in range(1, 51):
            status = random.choice(['P', 'P', 'P', 'A', 'HD'])
            in_time = "09:00:00"
            out_time = "18:00:00"
            remarks = "Work task"
            
            if status == 'A':
                in_time = None
                out_time = None
                remarks = "Absent"
            elif status == 'HD':
                out_time = "13:30:00"
                remarks = "Half day"
            
            cur.execute("""
                INSERT INTO attendance (employee_id, date, status, in_time, out_time, remarks)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (i, today, status, in_time, out_time, remarks))

        conn.commit()
        print("50 members and attendance generated successfully.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_50_members()
