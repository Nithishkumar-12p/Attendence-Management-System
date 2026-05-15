from backend.database.db_connection import db
from datetime import datetime

def run_check():
    print("=== System Health Check ===")
    try:
        # Check Employees
        res = db.execute_query("SELECT COUNT(*) FROM employees WHERE is_active = TRUE", fetch=True)
        active_count = res[0][0] if res else 0
        print(f"Active Employees: {active_count}")

        # Check Attendance
        today = datetime.now().strftime('%Y-%m-%d')
        res = db.execute_query("SELECT COUNT(*) FROM attendance WHERE date = %s", (today,), fetch=True)
        today_att = res[0][0] if res else 0
        print(f"Attendance for Today ({today}): {today_att}")

        # Check latest attendance
        res = db.execute_query("SELECT MAX(date) FROM attendance", fetch=True)
        latest_date = res[0][0] if res else "None"
        print(f"Latest Attendance Date in DB: {latest_date}")

        if active_count > 0:
            print("SUCCESS: Database is reachable and has data.")
        else:
            print("WARNING: Database is reachable but has no active employees.")

    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")

if __name__ == "__main__":
    run_check()
