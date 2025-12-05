from storage.storage_sqlite import StorageManager
from storage.password_storage_sqlite import PasswordSqliteDB

def test_get_password():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    password_db = PasswordSqliteDB(storage_manager)

    admin_password = password_db.get_password("admin")

    assert admin_password == "1234"

def test_get_password_fail():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    password_db = PasswordSqliteDB(storage_manager)

    admin_password = password_db.get_password("master")

    assert admin_password is None


def test_set_password():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    password_db = PasswordSqliteDB(storage_manager)
    password_db.set_password("admin", "4321")

    admin_password = password_db.get_password("admin")

    assert admin_password == "4321"
