from backend.database.db_connection import db
result = db.execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema='public'", fetch=True)
print('Tables:', result)
result = db.execute_query("SELECT COUNT(*) FROM employees", fetch=True)
print('Employee Count:', result[0][0])
result = db.execute_query("SELECT COUNT(*) FROM attendance", fetch=True)
print('Attendance Count:', result[0][0])
