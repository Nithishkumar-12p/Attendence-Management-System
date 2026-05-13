import psycopg2
import random

def generate_salaries():
    try:
        conn = psycopg2.connect(
            dbname='attendance_db',
            user='postgres',
            password='123456',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()
        
        # Get all employees
        cur.execute("SELECT employee_id, name, basic_salary FROM employees")
        employees = cur.fetchall()
        
        month = 4 # April
        year = 2026
        
        print(f"Generating salaries for {len(employees)} employees for {month}/{year}...")
        
        count = 0
        for emp_id, name, basic_salary in employees:
            present_days = random.randint(20, 30)
            absent_days = 30 - present_days
            final_salary = (float(basic_salary) / 30) * present_days
            
            cur.execute("""
                INSERT INTO salaries (employee_id, month, year, working_days, present_days, absent_days, leaves_taken, deductions, final_salary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (employee_id, month, year) DO UPDATE 
                SET present_days = EXCLUDED.present_days,
                    absent_days = EXCLUDED.absent_days,
                    final_salary = EXCLUDED.final_salary
            """, (emp_id, month, year, 30, present_days, absent_days, 0, 0, final_salary))
            count += 1
            
        conn.commit()
        print(f"Successfully generated {count} salary records.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_salaries()
