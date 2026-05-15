import os
import sys

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import routes
from backend.routes.employee_routes import employee_bp
from backend.routes.attendance_routes import attendance_bp
from backend.routes.salary_routes import salary_bp
from backend.routes.report_routes import report_bp
from backend.routes.settings_routes import settings_bp
from backend.routes.shift_routes import shift_bp
from backend.routes.auth_routes import auth_bp

load_dotenv()

app = Flask(__name__)
# Enable CORS for Electron (localhost)
CORS(app)

# Register Blueprints
app.register_blueprint(employee_bp, url_prefix='/api/employees')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(salary_bp, url_prefix='/api/salary')
app.register_blueprint(report_bp, url_prefix='/api/reports')
app.register_blueprint(settings_bp, url_prefix='/api/settings')
app.register_blueprint(shift_bp, url_prefix='/api/shifts')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Attendance Management System API is running",
        "endpoints": {
            "health": "/api/health",
            "employees": "/api/employees",
            "attendance": "/api/attendance",
            "salary": "/api/salary",
            "reports": "/api/reports",
            "shifts": "/api/shifts"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Backend is running", "database": "PostgreSQL"})

@app.route('/api/test_db', methods=['GET'])
def test_db():
    from backend.database.db_connection import db
    res = db.execute_query("SELECT COUNT(*) FROM employees WHERE is_active = TRUE", fetch=True)
    return jsonify({"count": res[0][0] if res else -1})

if __name__ == '__main__':
    # Run contract expiration cleanup once at startup
    try:
        from backend.models.employee import EmployeeModel
        print("Running startup cleanup: deactivating expired contracts...")
        EmployeeModel.auto_deactivate_expired_contracts()
    except Exception as e:
        print(f"Startup cleanup failed: {e}")

    # Run the app
    # In production, Electron will spawn this.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
