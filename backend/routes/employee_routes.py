from flask import Blueprint, request, jsonify
from backend.models.employee import EmployeeModel

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/', methods=['GET'])
def get_employees():
    employees = EmployeeModel.get_all_employees()
    formatted = []
    if employees:
        for e in employees:
            formatted.append({
                "employee_id": e[0],
                "name": e[1],
                "basic_salary": float(e[2]),
                "designation": e[3],
                "joining_date": str(e[4]) if e[4] else None,
                "aadhar_number": e[5],
                "phone_number": e[6],
                "contract_start_date": str(e[7]) if e[7] else None,
                "contract_end_date": str(e[8]) if e[8] else None,
                "working_hours_per_day": float(e[9]) if e[9] else 8.0,
                "is_active": e[10],
                "created_at": str(e[11]) if e[11] else None,
                "shift_id": e[12] if len(e) > 12 else None
            })
    return jsonify(formatted)

@employee_bp.route('/add', methods=['POST'])
def add_employee():
    data = request.json
    success = EmployeeModel.add_employee(
        data.get('name'),
        data.get('basic_salary'),
        data.get('designation'),
        data.get('joining_date'),
        data.get('aadhar_number'),
        data.get('phone_number'),
        data.get('contract_start_date'),
        data.get('contract_end_date'),
        data.get('working_hours_per_day'),
        data.get('shift_id')
    )
    return jsonify({"success": success})

@employee_bp.route('/update/<emp_id>', methods=['PUT'])
def update_employee(emp_id):
    data = request.json
    success = EmployeeModel.update_employee(
        emp_id,
        data.get('name'),
        data.get('basic_salary'),
        data.get('designation'),
        data.get('joining_date'),
        data.get('aadhar_number'),
        data.get('phone_number'),
        data.get('contract_start_date'),
        data.get('contract_end_date'),
        data.get('working_hours_per_day'),
        data.get('shift_id')
    )
    return jsonify({"success": success})

@employee_bp.route('/delete/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    success = EmployeeModel.delete_employee(emp_id)
    return jsonify({"success": success})
