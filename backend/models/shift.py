from backend.database.db_connection import db

class ShiftModel:
    @staticmethod
    def get_all():
        """Get all shifts with member count."""
        query = """
            SELECT s.*, COUNT(e.employee_id) as member_count
            FROM shifts s
            LEFT JOIN employees e ON s.id = e.shift_id AND e.is_active = TRUE
            GROUP BY s.id
            ORDER BY s.id ASC
        """
        rows = db.execute_query(query, fetch=True)
        if not rows:
            return []
        
        return [{
            "id": r[0],
            "name": r[1],
            "start_time": str(r[2]),
            "end_time": str(r[3]),
            "working_hours": float(r[4]),
            "grace_period": r[5],
            "member_count": r[7]
        } for r in rows]

    @staticmethod
    def create(name, start_time, end_time, working_hours, grace_period=15):
        query = """
            INSERT INTO shifts (name, start_time, end_time, working_hours, grace_period)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """
        params = (name, start_time, end_time, working_hours, grace_period)
        return db.execute_query(query, params, fetch=True)

    @staticmethod
    def update(shift_id, name, start_time, end_time, working_hours, grace_period):
        query = """
            UPDATE shifts 
            SET name=%s, start_time=%s, end_time=%s, working_hours=%s, grace_period=%s
            WHERE id=%s
        """
        params = (name, start_time, end_time, working_hours, grace_period, shift_id)
        return db.execute_query(query, params)

    @staticmethod
    def delete(shift_id):
        # Check if any employees are assigned
        check_query = "SELECT 1 FROM employees WHERE shift_id = %s AND is_active = TRUE"
        if db.execute_query(check_query, (shift_id,), fetch=True):
            return False, "Cannot delete shift with assigned members."
        
        query = "DELETE FROM shifts WHERE id = %s"
        return db.execute_query(query, (shift_id,)), None

    @staticmethod
    def assign_members(shift_id, employee_ids):
        """Assign multiple employees to a shift and remove others."""
        if not isinstance(employee_ids, list):
            return False
        
        try:
            # First, clear this shift_id from EVERYONE who currently has it
            clear_query = "UPDATE employees SET shift_id = NULL WHERE shift_id = %s"
            db.execute_query(clear_query, (shift_id,))
            
            # If the list is empty, we're done (everyone was removed)
            if not employee_ids:
                return True

            # Convert list to format for IN clause and assign new ID
            placeholders = ', '.join(['%s'] * len(employee_ids))
            update_query = f"UPDATE employees SET shift_id = %s WHERE employee_id IN ({placeholders})"
            params = [shift_id] + employee_ids
            return db.execute_query(update_query, params)
        except Exception as e:
            print(f"Error in assign_members: {e}")
            return False
