from datetime import datetime, time, timedelta
from backend.database.db_connection import db
from backend.models.settings import SettingsModel

class AttendanceModel:
    @staticmethod
    def mark_attendance(employee_id, status, date=None, in_time=None, out_time=None, remarks=None, tools_count=0, tools_details=None):
        if not date:
            date = datetime.now().date()
            
        # Scrub invalid time values
        if in_time == '-' or not in_time or in_time == '00:00': in_time = None
        if out_time == '-' or not out_time or out_time == '00:00': out_time = None
        
        is_late = False
        if status == 'P' and in_time:
            # Get shift timings for this employee
            shift_query = """
                SELECT s.start_time, s.grace_period 
                FROM employees e
                JOIN shifts s ON e.shift_id = s.id
                WHERE e.employee_id = %s
            """
            shift_data = db.execute_query(shift_query, (employee_id,), fetch=True)
            
            if shift_data:
                # shift_data[0][0] is start_time (datetime.time object or string)
                # shift_data[0][1] is grace_period (int)
                shift_start = shift_data[0][0]
                grace_minutes = int(shift_data[0][1] or 15)
            else:
                # Fallback to global standard settings
                shift_start = SettingsModel.get_value('shift_start_time', '09:00')
                grace_minutes = int(SettingsModel.get_value('grace_period', '15'))
            
            # Convert start_time to datetime for calculation if it's a string
            if isinstance(shift_start, str):
                try:
                    shift_start_dt = datetime.strptime(shift_start, '%H:%M:%S')
                except ValueError:
                    shift_start_dt = datetime.strptime(shift_start, '%H:%M')
            else:
                # It's already a time object, create a dummy datetime
                shift_start_dt = datetime.combine(datetime.today(), shift_start)
            
            grace_time = (shift_start_dt + timedelta(minutes=grace_minutes)).time()
            
            if isinstance(in_time, str):
                try:
                    # Clean input time (HH:MM:SS -> HH:MM)
                    t_str = in_time.substring(0, 5) if len(in_time) > 5 else in_time
                    t = datetime.strptime(t_str, '%H:%M').time()
                    if t > grace_time:
                        is_late = True
                except (ValueError, AttributeError):
                    # Handle cases where substring might fail or format is different
                    try:
                        t = datetime.strptime(in_time[:5], '%H:%M').time()
                        if t > grace_time:
                            is_late = True
                    except:
                        pass

        query = """
            INSERT INTO attendance (employee_id, date, status, in_time, out_time, is_late, remarks, tools_count, tools_details)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (employee_id, date) DO UPDATE 
            SET status = EXCLUDED.status, 
                in_time = EXCLUDED.in_time, 
                out_time = EXCLUDED.out_time, 
                is_late = EXCLUDED.is_late,
                remarks = EXCLUDED.remarks,
                tools_count = EXCLUDED.tools_count,
                tools_details = EXCLUDED.tools_details
        """
        params = (employee_id, date, status, in_time, out_time, is_late, remarks, tools_count, tools_details)
        res = db.execute_query(query, params)
        
        # Sync Daily Description (remarks) to Employee Designation (Type of Work)
        # This keeps the master worker data updated with their latest role in reports
        # We process 'None' as empty string for consistent clearing
        sync_remarks = remarks if remarks is not None else ''
        sync_query = "UPDATE employees SET designation = %s WHERE employee_id = %s"
        db.execute_query(sync_query, (sync_remarks, employee_id))
            
        return res

    @staticmethod
    def get_attendance_for_date(date):
        query = """
            SELECT e.employee_id, e.name, e.designation, a.status, a.in_time, a.out_time, a.is_late, a.remarks, a.tools_count, a.tools_details
            FROM employees e
            LEFT JOIN attendance a ON e.employee_id = a.employee_id AND a.date = %s
            WHERE e.is_active = TRUE
        """
        return db.execute_query(query, (date,), fetch=True)

    @staticmethod
    def get_attendance_for_range(start_date, end_date):
        query = """
            SELECT a.date, e.employee_id, e.name, e.designation, a.status, a.in_time, a.out_time, a.remarks, a.tools_count, a.tools_details
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.date >= %s AND a.date <= %s
            ORDER BY a.date ASC, e.employee_id ASC
        """
        return db.execute_query(query, (start_date, end_date), fetch=True)
