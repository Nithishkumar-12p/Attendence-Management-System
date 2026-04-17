from flask import Blueprint, request, jsonify
from backend.models.shift import ShiftModel

shift_bp = Blueprint('shifts', __name__)

@shift_bp.route('/', methods=['GET'])
def get_all_shifts():
    shifts = ShiftModel.get_all()
    return jsonify(shifts)

@shift_bp.route('/', methods=['POST'])
def create_shift():
    data = request.json
    try:
        res = ShiftModel.create(
            data['name'], 
            data['start_time'], 
            data['end_time'], 
            data['working_hours'], 
            data.get('grace_period', 15)
        )
        if res:
            return jsonify({"success": True, "id": res[0][0]})
        return jsonify({"success": False, "error": "Failed to create shift"}), 500
    except KeyError as e:
        return jsonify({"success": False, "error": f"Missing field: {str(e)}"}), 400

@shift_bp.route('/<int:shift_id>', methods=['PUT'])
def update_shift(shift_id):
    data = request.json
    res = ShiftModel.update(
        shift_id,
        data['name'], 
        data['start_time'], 
        data['end_time'], 
        data['working_hours'], 
        data['grace_period']
    )
    if res:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Failed to update shift"}), 500

@shift_bp.route('/<int:shift_id>', methods=['DELETE'])
def delete_shift(shift_id):
    success, error = ShiftModel.delete(shift_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": error}), 400

@shift_bp.route('/assign', methods=['POST'])
def assign_members():
    data = request.json
    shift_id = data.get('shift_id')
    employee_ids = data.get('employee_ids', [])
    
    if not shift_id:
        return jsonify({"success": False, "error": "Missing shift_id"}), 400
        
    if ShiftModel.assign_members(shift_id, employee_ids):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Failed to assign members"}), 500
