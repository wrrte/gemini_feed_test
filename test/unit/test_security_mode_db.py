from storage.storage_sqlite import StorageManager
from storage.security_mode_storage_sqlite import SecurityModeSqliteDB
from device.device_motion_detector import DeviceMotionDetector

from storage.security_storage_sqlite import SecuritySqliteDB


def test_get_security_modes():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecurityModeSqliteDB(storage_manager)

    security_modes = security_mode_db.get_security_modes()

    assert len(security_modes) == 4
    assert len(security_modes[0].sensors) == 0
    assert len(security_modes[1].sensors) == 10
    assert len(security_modes[2].sensors) == 8
    assert len(security_modes[3].sensors) == 4


def test_get_now_security_mode():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecurityModeSqliteDB(storage_manager)

    now_security_mode = security_mode_db.get_now_security_mode()

    assert now_security_mode is None


def test_set_now_security_mode():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecurityModeSqliteDB(storage_manager)

    now_security_mode = security_mode_db.get_now_security_mode()

    assert now_security_mode is None

    security_mode_db.set_now_security_mode(0)

    now_security_mode = security_mode_db.get_now_security_mode()

    assert now_security_mode == 0


def test_update_security_mode():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecurityModeSqliteDB(storage_manager)

    security_modes = security_mode_db.get_security_modes()

    assert len(security_modes) == 4
    assert len(security_modes[0].sensors) == 0
    assert len(security_modes[1].sensors) == 10
    assert len(security_modes[2].sensors) == 8
    assert len(security_modes[3].sensors) == 4

    security_modes[0]
    security_modes[0].sensors.append(DeviceMotionDetector(start=(0, 0), end=(0, 0)))
    security_modes[0].sensors[-1].sensor_id = 10

    # Stamp coupling occurred because of improvised in-memory security database
    # Summary: Whole SecurityMode object is passed
    # Problem: The only needed parameters are mode_name and list of sensor_ids
    security_mode_db.update_security_mode(security_modes[0].name, security_modes[0])

    security_modes = security_mode_db.get_security_modes()

    assert len(security_modes) == 4
    assert len(security_modes[0].sensors) == 1
    assert security_modes[0].sensors[-1].sensor_id == 10
    assert len(security_modes[1].sensors) == 10
    assert len(security_modes[2].sensors) == 8
    assert len(security_modes[3].sensors) == 4


def test_get_security_modes_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecuritySqliteDB(storage_manager)

    security_modes = security_mode_db.get_security_modes()

    assert len(security_modes) == 4
    assert len(security_modes[0].sensors) == 0
    assert len(security_modes[1].sensors) == 10
    assert len(security_modes[2].sensors) == 8
    assert len(security_modes[3].sensors) == 4


def test_get_now_security_mode_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecuritySqliteDB(storage_manager)

    now_security_mode = security_mode_db.get_now_security_mode()

    assert now_security_mode is None


def test_set_now_security_mode_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecuritySqliteDB(storage_manager)

    now_security_mode = security_mode_db.get_now_security_mode()

    assert now_security_mode is None

    security_mode_db.set_now_security_mode(0)

    now_security_mode = security_mode_db.get_now_security_mode()

    assert now_security_mode == 0


def test_update_security_mode_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_mode_db = SecuritySqliteDB(storage_manager)

    security_modes = security_mode_db.get_security_modes()

    assert len(security_modes) == 4
    assert len(security_modes[0].sensors) == 0
    assert len(security_modes[1].sensors) == 10
    assert len(security_modes[2].sensors) == 8
    assert len(security_modes[3].sensors) == 4

    security_modes[0]
    security_modes[0].sensors.append(DeviceMotionDetector(start=(0, 0), end=(0, 0)))
    security_modes[0].sensors[-1].sensor_id = 10

    # Stamp coupling occurred because of improvised in-memory security database
    # Summary: Whole SecurityMode object is passed
    # Problem: The only needed parameters are mode_name and list of sensor_ids
    security_mode_db.update_security_mode(security_modes[0].name, security_modes[0])

    security_modes = security_mode_db.get_security_modes()

    assert len(security_modes) == 4
    assert len(security_modes[0].sensors) == 1
    assert security_modes[0].sensors[-1].sensor_id == 10
    assert len(security_modes[1].sensors) == 10
    assert len(security_modes[2].sensors) == 8
    assert len(security_modes[3].sensors) == 4
