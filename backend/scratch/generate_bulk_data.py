import psycopg2
import random
from datetime import datetime, date

def generate_bulk_data():
    try:
        conn = psycopg2.connect(
            dbname='attendance_db',
            user='postgres',
            password='123456',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()

        # 1. Clear existing dummy data (except the admin/default)
        # cur.execute("DELETE FROM attendance")
        # cur.execute("DELETE FROM employees WHERE employee_id > 1")
        
        # 2. Add 100 employees
        designations = ['Welder', 'Fitter', 'Electrician', 'Operator', 'Supervisor', 'Helper', 'Painter', 'Mechanic']
        today = date.today()
        
        print("Generating 100 employees...")
        for i in range(2, 102):
            name = f"Worker {i}"
            salary = random.randint(12000, 35000)
            designation = random.choice(designations)
            aadhar = f"{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
            phone = f"9{random.randint(100000000, 999999999)}"
            
            cur.execute("""
                INSERT INTO employees (employee_id, name, basic_salary, designation, joining_date, aadhar_number, phone_number, shift_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                ON CONFLICT (employee_id) DO NOTHING
            """, (i, name, salary, designation, today, aadhar, phone))

        # 3. Add attendance for these 100 employees for today
        print("Generating attendance records...")
        cur.execute("SELECT employee_id FROM employees WHERE is_active = TRUE")
        emps = cur.fetchall()
        
        for (emp_id,) in emps:
            status = random.choice(['P', 'P', 'P', 'P', 'A', 'HD', 'P', 'P']) # Weighted towards Present
            in_time = "09:00:00"
            out_time = "18:00:00"
            remarks = "Regular shift"
            
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
                ON CONFLICT (employee_id, date) DO UPDATE 
                SET status = EXCLUDED.status, in_time = EXCLUDED.in_time, out_time = EXCLUDED.out_time, remarks = EXCLUDED.remarks
            """, (emp_id, today, status, in_time, out_time, remarks))

        conn.commit()
        print("Bulk data generation complete.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_bulk_data()
