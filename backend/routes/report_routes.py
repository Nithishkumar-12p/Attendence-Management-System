import os
from flask import Blueprint, send_file, request, jsonify
from backend.models.report_model import ReportModel

report_bp = Blueprint('report', __name__)

@report_bp.route('/pdf/daily/<date>', methods=['GET'])
def export_daily_pdf(date):
    try:
        pdf_path = ReportModel.generate_daily_pdf(date)
        return send_file(pdf_path, as_attachment=True, download_name=f'Vidvat_Solutions_Daily_Attendance_{date}.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/pdf/range', methods=['GET'])
def export_range_pdf():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400
        
    try:
        pdf_path = ReportModel.generate_range_pdf(start_date, end_date)
        return send_file(pdf_path, as_attachment=True, download_name=f'Vidvat_Solutions_Range_Attendance_{start_date}_to_{end_date}.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/pdf/salary/<int:month>/<int:year>', methods=['GET'])
def export_salary_pdf(month, year):
    ids_param = request.args.get('ids')
    try:
        if ids_param:
            emp_ids = [int(id) for id in ids_param.split(',') if id.strip()]
        else:
            # Fetch all employee IDs who have a salary record for this month
            from backend.database.db_connection import db
            query = "SELECT employee_id FROM salaries WHERE month = %s AND year = %s"
            rows = db.execute_query(query, (month, year), fetch=True)
            emp_ids = [r[0] for r in rows]

        if not emp_ids:
            return jsonify({"error": "No salary records found to export"}), 404

        pdf_path = ReportModel.generate_filtered_invoices_pdf(emp_ids, month, year)
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        if len(emp_ids) == 1:
            from backend.database.db_connection import db
            q = "SELECT name FROM employees WHERE employee_id = %s"
            r = db.execute_query(q, (emp_ids[0],), fetch=True)
            name = r[0][0] if r else f"ID_{emp_ids[0]}"
            download_name = f'VIDVAT - {name}.pdf'
        else:
            download_name = f'VIDVAT_Invoices_{month_names[month]}_{year}.pdf'

        return send_file(pdf_path, as_attachment=True, download_name=download_name)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/pdf/salary/slip/<int:emp_id>/<int:month>/<int:year>', methods=['GET'])
def export_salary_slip_pdf(emp_id, month, year):
    try:
        pdf_path = ReportModel.generate_salary_slip_pdf(emp_id, month, year)
        from backend.database.db_connection import db
        query = "SELECT name FROM employees WHERE employee_id = %s"
        res = db.execute_query(query, (emp_id,), fetch=True)
        name = res[0][0].replace(' ', '_') if res else f"Emp_{emp_id}"
        return send_file(pdf_path, as_attachment=True, download_name=f'Vidvat_Slip_{name}.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/pdf/employees', methods=['GET'])
def export_employee_list_pdf():
    try:
        pdf_path = ReportModel.generate_employee_list_pdf()
        return send_file(pdf_path, as_attachment=True, download_name=f'Vidvat_Worker_Directory.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
