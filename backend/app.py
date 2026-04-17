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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Backend is running", "database": "PostgreSQL"})

if __name__ == '__main__':
    # Run the app
    # In production, Electron will spawn this.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
