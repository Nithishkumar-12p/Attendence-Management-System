from backend.database.db_connection import db

class UserModel:
    @staticmethod
    def create_user(username, password, role='supervisor'):
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING id"
        params = (username, password, role)
        res = db.execute_query(query, params, fetch=True)
        return res[0][0] if res else None

    @staticmethod
    def get_user_by_username(username):
        query = "SELECT id, username, password, role FROM users WHERE username = %s"
        params = (username,)
        res = db.execute_query(query, params, fetch=True)
        if res:
            return {
                "id": res[0][0],
                "username": res[0][1],
                "password": res[0][2],
                "role": res[0][3]
            }
        return None
    
    @staticmethod
    def update_password(username, new_password):
        query = "UPDATE users SET password = %s WHERE username = %s"
        params = (new_password, username)
        return db.execute_query(query, params)
