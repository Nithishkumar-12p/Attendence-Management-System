from flask import Blueprint, request, jsonify
from backend.models.salary import SalaryModel

salary_bp = Blueprint('salary', __name__)

@salary_bp.route('/calculate', methods=['POST'])
def calculate_salary():
    data = request.json
    emp_ids = data.get('employee_ids', [])
    month = data.get('month')
    year = data.get('year')
    
    results = []
    for emp_id in emp_ids:
        res = SalaryModel.calculate_monthly_salary(emp_id, month, year)
        if res:
            results.append(res)
            
    return jsonify(results)

@salary_bp.route('/report/<int:month>/<int:year>', methods=['GET'])
def get_salary_report(month, year):
    # Fetch existing salary records for the month
    from backend.database.db_connection import db
    query = """
        SELECT s.*, e.name, e.designation, e.basic_salary as original_basic
        FROM salaries s
        JOIN employees e ON s.employee_id = e.employee_id
        WHERE s.month = %s AND s.year = %s
    """
    records = db.execute_query(query, (month, year), fetch=True)
    formatted = []
    if records:
        for r in records:
            formatted.append({
                "employee_id": r[1],
                "month": r[2],
                "year": r[3],
                "working_days": r[4],
                "present_days": float(r[5]),
                "absent_days": float(r[6]),
                "leaves_taken": float(r[7]),
                "deductions": float(r[8]),
                "final_salary": float(r[9]),
                "name": r[11],
                "designation": r[12],
                "basic_salary": float(r[13])
            })
    return jsonify(formatted)
