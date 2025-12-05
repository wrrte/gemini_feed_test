from storage.storage_sqlite import StorageManager
from core.security.security_database_interface import SecurityModeDBInterface
from core.security.security_mode.security_mode import SecurityMode
from device.device_motion_detector import DeviceMotionDetector
from device.device_windoor_sensor import DeviceWinDoorSensor

import json


class SecurityModeSqliteDB(SecurityModeDBInterface):
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager

    def get_security_modes(self) -> list[SecurityMode]:
        query = """
        SELECT x.mode_id, x.name
        FROM safehome_modes as x
        ORDER BY x.mode_id ASC
        """
        rows = self.storage_manager.execute(query)

        security_modes = []

        for row in rows:
            security_modes.append(SecurityMode([], row[1]))

        query = """
        SELECT x.mode_id, z.sensor_id, z.sensor_type, z.location
        FROM safehome_modes as x
        INNER JOIN mode_sensor_map as y using(mode_id)
        INNER JOIN sensors as z using(sensor_id)
        """

        rows = self.storage_manager.execute(query)

        for row in rows:
            json_value = json.loads(row[3])

            if row[2] == "DeviceMotionDetector":
                sensor = DeviceMotionDetector((json_value["up_left_x"], json_value["up_left_y"]),
                                              (json_value["down_right_x"], json_value["down_right_y"]))
                sensor.sensor_id = row[1]
                security_modes[row[0] - 1].sensors.append(sensor)

            elif row[2] == "DeviceWinDoorSensor":
                sensor = DeviceWinDoorSensor(json_value["x"], json_value["y"])
                sensor.sensor_id = row[1]
                security_modes[row[0] - 1].sensors.append(sensor)
            else:
                raise Exception("Unknown sensor device type stored in sqlite database")

        return security_modes

    def get_now_security_mode(self) -> int | None:
        query = """
        SELECT *
        FROM system_settings
        WHERE name=?
        """

        rows = self.storage_manager.execute(query, ("now_security_mode",))

        json_values = {}

        if len(rows) <= 0:
            raise Exception("Wrong json schema stored in DB. now_security_mode does not exist")

        row = rows[0]
        json_value = json.loads(row[2])

        return json_value["mode"]

    def set_now_security_mode(self, now: int | None) -> None:
        query = """
        UPDATE system_settings
        SET value=?
        WHERE name=?
        """

        self.storage_manager.execute(query, (json.dumps({"mode": now}), "now_security_mode",))

    def add_security_mode(self, mode: SecurityMode) -> None:
        pass

    def remove_security_mode(self, name: str) -> None:
        pass

    def update_security_mode(self, name: str, mode: SecurityMode) -> None:
        query = """
        SELECT mode_id
        FROM safehome_modes
        WHERE name=?
        """

        rows = self.storage_manager.execute(query, (name,))
        row = rows[0]

        query = """
        DELETE FROM "mode_sensor_map" WHERE mode_id=?
        """

        self.storage_manager.execute(query, (row[0],))

        for sensor in mode.sensors:
            query = """
            INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (?, ?)
            """
            self.storage_manager.execute(query, (row[0], sensor.get_id()))
