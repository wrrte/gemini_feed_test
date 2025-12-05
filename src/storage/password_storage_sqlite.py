from core.login.password_storage import IPasswordDB
from storage.storage_sqlite import StorageManager


class PasswordSqliteDB(IPasswordDB):
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager

    def get_password(self, user_id):
        query = """
        SELECT *
        FROM users
        WHERE user_id = ?
        """

        rows = self.storage_manager.execute(query, (user_id, ))

        if len(rows) == 0:
            return None

        row = rows[0]

        return row[1]


    def set_password(self, user_id, new_password):
        query = """
        UPDATE users
        SET password = ?
        WHERE user_id = ?
        """

        self.storage_manager.execute(query, (new_password, user_id))
