from storage.storage_sqlite import StorageManager
from storage.control_panel_setting_storage_sqlite import ControlPanelSettingsSqliteDB

def test_get_master_password():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    setting_db = ControlPanelSettingsSqliteDB(storage_manager)

    master_password = setting_db.get_master_password()

    assert master_password == "1234"


def test_set_master_password():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    setting_db = ControlPanelSettingsSqliteDB(storage_manager)

    setting_db.set_master_password("4321")

    master_password = setting_db.get_master_password()

    assert master_password == "4321"

def test_get_guest_password():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    setting_db = ControlPanelSettingsSqliteDB(storage_manager)

    guest_password = setting_db.get_guest_password()

    assert guest_password == ""


def test_set_guest_password():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    setting_db = ControlPanelSettingsSqliteDB(storage_manager)

    setting_db.set_guest_password("1234")

    guest_password = setting_db.get_master_password()

    assert guest_password == "1234"

