from storage.storage_sqlite import StorageManager
from storage.system_setting_storage_sqlite import SystemSettingsSqliteDB
from core.setting.system_setting import SystemSettings


def test_get_system_settings():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    system_settings_storage_manager = SystemSettingsSqliteDB(storage_manager)

    system_settings = system_settings_storage_manager.get_system_settings()

    assert system_settings.system_lock_time == 300
    assert system_settings.panic_phone_number == "112"
    assert system_settings.alarm_time_before_phonecall == 5
    assert system_settings.home_phone_number == "01012345678"


def test_update_system_settings():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    system_settings_storage_manager = SystemSettingsSqliteDB(storage_manager)

    system_settings = SystemSettings()
    system_settings.system_lock_time = 60
    system_settings.panic_phone_number = "12345678910"
    system_settings.alarm_time_before_phonecall = 120
    system_settings.home_phone_number = "10987654321"

    system_settings_storage_manager.update_system_settings(system_settings)

    system_settings = system_settings_storage_manager.get_system_settings()

    assert system_settings.system_lock_time == 60
    assert system_settings.panic_phone_number == "12345678910"
    assert system_settings.alarm_time_before_phonecall == 120
    assert system_settings.home_phone_number == "10987654321"
