from backend.database.db_connection import db

class SettingsModel:
    @staticmethod
    def get_all():
        """Return all settings as a list of dicts."""
        query = "SELECT key, value, description FROM settings ORDER BY key"
        rows = db.execute_query(query, fetch=True)
        if not rows:
            return []
        return [{"key": r[0], "value": r[1], "description": r[2]} for r in rows]

    @staticmethod
    def get_value(key, default=None):
        """Get a single setting value by key."""
        query = "SELECT value FROM settings WHERE key = %s"
        rows = db.execute_query(query, (key,), fetch=True)
        if rows and rows[0]:
            return rows[0][0]
        return default

    @staticmethod
    def update(key, value):
        """Update a single setting. Creates it if it doesn't exist."""
        query = """
            INSERT INTO settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """
        return db.execute_query(query, (key, value))

    @staticmethod
    def update_bulk(settings_dict):
        """Update multiple settings at once."""
        for key, value in settings_dict.items():
            SettingsModel.update(key, value)
        return True
