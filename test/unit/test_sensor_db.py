from storage.storage_sqlite import StorageManager
from storage.sensor_storage_sqlite import SensorSqliteDB

from storage.security_storage_sqlite import SecuritySqliteDB


def test_get_sensors():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    sensor_db = SensorSqliteDB(storage_manager)

    sensors = sensor_db.get_sensors()

    assert len(list(sensors.keys())) == 10


def test_turn_onoff_sensor():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    sensor_db = SensorSqliteDB(storage_manager)

    sensors = sensor_db.get_sensors()
    sensor_keys = list(sensors.keys())

    assert len(sensor_keys) == 10
    assert sensors[sensor_keys[0]][0] == True

    sensor_db.turn_onoff_sensor(sensor_keys[0], False)

    sensors2 = sensor_db.get_sensors()
    sensor_keys2 = list(sensors2.keys())

    assert sensor_keys[0].get_id() == sensor_keys2[0].get_id()

    assert len(sensor_keys2) == 10
    assert sensors2[sensor_keys2[0]][0] == False


def test_update_sensor():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    sensor_db = SensorSqliteDB(storage_manager)

    sensors = sensor_db.get_sensors()
    sensor_keys = list(sensors.keys())

    assert len(sensor_keys) == 10
    assert sensors[sensor_keys[0]] == (True, None)

    sensor_db.update_sensor(sensor_keys[0], (False, False))

    sensors2 = sensor_db.get_sensors()
    sensor_keys2 = list(sensors2.keys())

    assert sensor_keys[0].get_id() == sensor_keys2[0].get_id()

    assert len(sensor_keys2) == 10
    assert sensors2[sensor_keys2[0]] == (False, False)


def test_get_sensors_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    sensor_db = SecuritySqliteDB(storage_manager)

    sensors = sensor_db.get_sensors()

    assert len(list(sensors.keys())) == 10


def test_turn_onoff_sensor_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    sensor_db = SecuritySqliteDB(storage_manager)

    sensors = sensor_db.get_sensors()
    sensor_keys = list(sensors.keys())

    assert len(sensor_keys) == 10
    assert sensors[sensor_keys[0]][0] == True

    sensor_db.turn_onoff_sensor(sensor_keys[0], False)

    sensors2 = sensor_db.get_sensors()
    sensor_keys2 = list(sensors2.keys())

    assert sensor_keys[0].get_id() == sensor_keys2[0].get_id()

    assert len(sensor_keys2) == 10
    assert sensors2[sensor_keys2[0]][0] == False


def test_update_sensor_2():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    sensor_db = SecuritySqliteDB(storage_manager)

    sensors = sensor_db.get_sensors()
    sensor_keys = list(sensors.keys())

    assert len(sensor_keys) == 10
    assert sensors[sensor_keys[0]] == (True, None)

    sensor_db.update_sensor(sensor_keys[0], (False, False))

    sensors2 = sensor_db.get_sensors()
    sensor_keys2 = list(sensors2.keys())

    assert sensor_keys[0].get_id() == sensor_keys2[0].get_id()

    assert len(sensor_keys2) == 10
    assert sensors2[sensor_keys2[0]] == (False, False)
