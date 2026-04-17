from flask import Blueprint, request, jsonify
from backend.models.settings import SettingsModel

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/', methods=['GET'])
def get_settings():
    """Return all settings as a JSON object."""
    settings = SettingsModel.get_all()
    return jsonify(settings)

@settings_bp.route('/update', methods=['POST'])
def update_settings():
    """Bulk update settings. Expects JSON object { key: value, ... }"""
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid input. Expected a JSON object."}), 400

    result = SettingsModel.update_bulk(data)
    if result:
        return jsonify({"success": True, "message": "Settings updated successfully."})
    return jsonify({"error": "Failed to update settings."}), 500

@settings_bp.route('/get/<key>', methods=['GET'])
def get_single(key):
    """Get a single setting by key."""
    value = SettingsModel.get_value(key)
    if value is not None:
        return jsonify({"key": key, "value": value})
    return jsonify({"error": f"Setting '{key}' not found."}), 404
