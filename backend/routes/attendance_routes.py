from flask import Blueprint, request, jsonify
from backend.models.attendance import AttendanceModel

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['POST'])
def mark_attendance():
    data = request.json
    # data expects list of {employee_id, status, date, in_time, out_time}
    if not isinstance(data, list):
        data = [data]
    
    results = []
    for item in data:
        res = AttendanceModel.mark_attendance(
            item.get('employee_id'),
            item.get('status'),
            item.get('date'),
            item.get('in_time'),
            item.get('out_time'),
            item.get('remarks'),
            item.get('tools_count', 0),
            item.get('tools_details')
        )
        results.append(res)
    
    return jsonify({"success": all(results), "count": len(results)})

@attendance_bp.route('/list/<date>', methods=['GET'])
def get_attendance(date):
    records = AttendanceModel.get_attendance_for_date(date)
    formatted = []
    if records:
        for r in records:
            formatted.append({
                "employee_id": r[0],
                "name": r[1],
                "designation": r[2],
                "status": r[3] or 'A',
                "in_time": str(r[4]) if r[4] else '-',
                "out_time": str(r[5]) if r[5] else '-',
                "is_late": r[6],
                "remarks": r[7] if len(r)>7 and r[7] else '',
                "tools_count": r[8] if len(r)>8 and r[8] else 0,
                "tools_details": r[9] if len(r)>9 and r[9] else ''
            })
    return jsonify(formatted)

@attendance_bp.route('/range', methods=['GET'])
def get_attendance_range():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400
        
    records = AttendanceModel.get_attendance_for_range(start_date, end_date)
    formatted = []
    if records:
        for r in records:
            formatted.append({
                "date": str(r[0]),
                "employee_id": r[1],
                "name": r[2],
                "designation": r[3],
                "status": r[4] or 'A',
                "in_time": str(r[5]) if r[5] else '-',
                "out_time": str(r[6]) if r[6] else '-',
                "remarks": r[7] if len(r)>7 and r[7] else '',
                "tools_count": r[8] if len(r)>8 and r[8] else 0,
                "tools_details": r[9] if len(r)>9 and r[9] else ''
            })
    return jsonify(formatted)
