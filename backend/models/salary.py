from backend.database.db_connection import db

class SalaryModel:
    @staticmethod
    def calculate_monthly_salary(employee_id, month, year):
        # 1. Fetch employee basic salary
        emp_query = "SELECT basic_salary FROM employees WHERE employee_id = %s"
        emp_res = db.execute_query(emp_query, (employee_id,), fetch=True)
        if not emp_res:
            return None
        basic_salary = float(emp_res[0][0])
        # For contract workers, "basic_salary" is actually their Daily Wage.
        daily_wage = basic_salary

        # 2. Fetch attendance stats for the month
        # Status codes: P (Present), A (Absent), CL (Casual Leave), SL (Sick Leave), HD (Half Day)
        stats_query = """
            SELECT status, COUNT(*) 
            FROM attendance 
            WHERE employee_id = %s AND EXTRACT(MONTH FROM date) = %s AND EXTRACT(YEAR FROM date) = %s
            GROUP BY status
        """
        stats_res = db.execute_query(stats_query, (employee_id, month, year), fetch=True)
        
        status_counts = { 'P': 0, 'A': 0, 'CL': 0, 'SL': 0, 'HD': 0 }
        for row in stats_res:
            status_counts[row[0]] = row[1]
        
        absent_days = status_counts['A']
        half_days = status_counts['HD']
        leaves = status_counts['CL'] + status_counts['SL']
        
        # Calculation logic for contract daily-wage workers:
        # Paid strictly for Present Days + (Half Days * 0.5)
        present_days_count = status_counts['P'] + (half_days * 0.5)
        
        # Final Salary is just Present Days * Daily Wage
        final_salary = present_days_count * daily_wage
        
        # No deductions applied for daily wage workers, they are just unpaid for absent days
        deductions = 0
        
        total_days_accounted = status_counts['P'] + absent_days + leaves + half_days

        # Update or Insert record
        save_query = """
            INSERT INTO salaries (employee_id, month, year, working_days, present_days, absent_days, leaves_taken, deductions, final_salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (employee_id, month, year) DO UPDATE SET
                working_days = EXCLUDED.working_days,
                present_days = EXCLUDED.present_days,
                absent_days = EXCLUDED.absent_days,
                leaves_taken = EXCLUDED.leaves_taken,
                deductions = EXCLUDED.deductions,
                final_salary = EXCLUDED.final_salary
        """
        params = (employee_id, month, year, total_days_accounted, present_days_count, absent_days, leaves, deductions, final_salary)
        db.execute_query(save_query, params)
        
        return {
            "employee_id": employee_id,
            "basic_salary": basic_salary,
            "present_days": float(present_days_count),
            "absent_days": float(absent_days),
            "half_days": int(half_days),
            "deductions": round(float(deductions), 2),
            "final_salary": round(float(final_salary), 2)
        }
