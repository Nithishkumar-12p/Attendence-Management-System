from backend.database.db_connection import db

class EmployeeModel:
    @staticmethod
    def add_employee(name, basic_salary, designation=None, joining_date=None, 
                     aadhar_number=None, phone_number=None, contract_start_date=None, 
                     contract_end_date=None, working_hours_per_day=None, shift_id=None):
        # Aadhar uniqueness check
        check_query = "SELECT employee_id FROM employees WHERE aadhar_number = %s"
        if aadhar_number and db.execute_query(check_query, (aadhar_number,), fetch=True):
            return False # Duplicate Aadhar

        query = """
            INSERT INTO employees (name, basic_salary, designation, joining_date, 
                                   aadhar_number, phone_number, contract_start_date, 
                                   contract_end_date, working_hours_per_day, shift_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (name, basic_salary, designation, joining_date, 
                  aadhar_number, phone_number, contract_start_date, 
                  contract_end_date, working_hours_per_day, shift_id)
        return db.execute_query(query, params)

    @staticmethod
    def auto_deactivate_expired_contracts():
        # Soft delete workers whose contract end date has passed.
        query = "UPDATE employees SET is_active = FALSE WHERE contract_end_date < CURRENT_DATE AND is_active = TRUE"
        db.execute_query(query)

    @staticmethod
    def get_all_employees():
        # Run auto-deactivation first to ensure accuracy
        EmployeeModel.auto_deactivate_expired_contracts()
        
        # Only return active workers
        query = "SELECT * FROM employees WHERE is_active = TRUE ORDER BY employee_id"
        return db.execute_query(query, fetch=True)

    @staticmethod
    def get_employee_by_id(employee_id):
        query = "SELECT * FROM employees WHERE employee_id = %s"
        return db.execute_query(query, (employee_id,), fetch=True)

    @staticmethod
    def update_employee(employee_id, name, basic_salary, designation, joining_date,
                        aadhar_number=None, phone_number=None, contract_start_date=None, 
                        contract_end_date=None, working_hours_per_day=None, shift_id=None):
        query = """
            UPDATE employees SET name=%s, basic_salary=%s, designation=%s, joining_date=%s,
                                 aadhar_number=%s, phone_number=%s, contract_start_date=%s, 
                                 contract_end_date=%s, working_hours_per_day=%s, shift_id=%s
            WHERE employee_id=%s
        """
        params = (name, basic_salary, designation, joining_date, 
                  aadhar_number, phone_number, contract_start_date, 
                  contract_end_date, working_hours_per_day, shift_id, employee_id)
        return db.execute_query(query, params)

    @staticmethod
    def delete_employee(employee_id):
        # Soft deletion
        query = "UPDATE employees SET is_active = FALSE WHERE employee_id = %s"
        return db.execute_query(query, (employee_id,))

