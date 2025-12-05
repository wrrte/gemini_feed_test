from storage.storage_sqlite import StorageManager
from storage.security_zone_storage_sqlite import SecurityZoneSqliteDB
from core.security.security_zone import SecurityZone
from core.security.security_zone_geometry.area import Square

from device.device_motion_detector import DeviceMotionDetector
from device.device_windoor_sensor import DeviceWinDoorSensor

from storage.security_storage_sqlite import SecuritySqliteDB


def test_get_security_zones():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_zone_db = SecurityZoneSqliteDB(storage_manager)

    security_zones = security_zone_db.get_security_zones()

    assert len(security_zones) == 0


def test_add_security_zone():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_zone_db = SecurityZoneSqliteDB(storage_manager)

    new_zone = SecurityZone(Square(0, 0, 10, 10), [])

    security_zone_db.add_security_zone(new_zone)

    security_zones = security_zone_db.get_security_zones()

    assert len(security_zones) == 1


def test_update_security_zone():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_zone_db = SecurityZoneSqliteDB(storage_manager)

    new_zone = SecurityZone(Square(0, 0, 10, 10), [])

    security_zone_db.add_security_zone(new_zone)

    new_zone_id = new_zone.id

    security_zones = security_zone_db.get_security_zones()

    assert len(security_zones) == 1
    assert security_zones[0].area.up_left[0] == 10
    assert security_zones[0].area.up_left[1] == 0
    assert security_zones[0].area.down_right[0] == 10
    assert security_zones[0].area.down_right[1] == 0
    assert new_zone_id == 1

    new_zone = SecurityZone(Square(0, 0, 20, 20), [])

    security_zone_db.update_security_zone(new_zone_id, new_zone)

    security_zones = security_zone_db.get_security_zones()

    assert len(security_zones) == 1
    assert security_zones[0].area.up_left[0] == 20
    assert security_zones[0].area.up_left[1] == 0
    assert security_zones[0].area.down_right[0] == 20
    assert security_zones[0].area.down_right[1] == 0
    assert new_zone_id == 1


def test_remove_security_zone():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_zone_db = SecurityZoneSqliteDB(storage_manager)

    new_zone = SecurityZone(Square(0, 0, 10, 10), [])

    security_zone_db.add_security_zone(new_zone)

    new_zone_id = new_zone.id

    security_zones = security_zone_db.get_security_zones()

    assert len(security_zones) == 1
    assert new_zone_id == 1

    security_zone_db.remove_security_zone(new_zone_id)
    security_zones = security_zone_db.get_security_zones()
    assert len(security_zones) == 0


def test_get_security_zones_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    security_zone_db = SecuritySqliteDB(storage_manager)

    security_zones = security_zone_db.get_security_zones()

    assert len(security_zones) == 0
