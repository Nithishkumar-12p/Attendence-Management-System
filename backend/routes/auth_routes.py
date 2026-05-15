from flask import Blueprint, request, jsonify
from backend.models.user import UserModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    if UserModel.get_user_by_username(username):
        return jsonify({"success": False, "message": "Username already exists"}), 400

    user_id = UserModel.create_user(username, password)
    if user_id:
        return jsonify({"success": True, "message": "User registered successfully", "user_id": user_id})
    else:
        return jsonify({"success": False, "message": "Failed to register user"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    user = UserModel.get_user_by_username(username)
    if user and user['password'] == password:  # Note: In a real app, use hashing!
        return jsonify({"success": True, "message": "Login successful", "user": {"id": user['id'], "username": user['username'], "role": user['role']}})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and new password are required"}), 400

    if not UserModel.get_user_by_username(username):
        return jsonify({"success": False, "message": "Username not found"}), 404

    if UserModel.update_password(username, password):
        return jsonify({"success": True, "message": "Password updated successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to update password"}), 500
