from storage.storage_sqlite import StorageManager
from core.security.security_database_interface import SecurityZoneDBInterface
from core.security.security_zone_geometry.area import Square
from core.security.security_zone import SecurityZone
from device.device_motion_detector import DeviceMotionDetector
from device.device_windoor_sensor import DeviceWinDoorSensor

import json


class SecurityZoneSqliteDB(SecurityZoneDBInterface):
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager

    def get_security_zones(self) -> list[SecurityZone]:
        query = """
        SELECT *
        FROM sensors
        """
        rows = self.storage_manager.execute(query)

        sensors = {}

        for row in rows:
            json_value = json.loads(row[2])
            if row[1] == "DeviceMotionDetector":
                sensor = DeviceMotionDetector((json_value["up_left_x"], json_value["up_left_y"]),
                                              (json_value["down_right_x"], json_value["down_right_y"]))

                sensor.sensor_id = row[0]
                if row[4] is None:
                    sensors[sensor] = (bool(row[3]), row[4])
                else:
                    sensors[sensor] = (bool(row[3]), bool(row[4]))
            elif row[1] == "DeviceWinDoorSensor":
                sensor = DeviceWinDoorSensor(json_value["x"], json_value["y"])

                sensor.sensor_id = row[0]

                if row[4] is None:
                    sensors[sensor] = (bool(row[3]), row[4])
                else:
                    sensors[sensor] = (bool(row[3]), bool(row[4]))
            else:
                raise Exception("Unknown sensor device type stored in sqlite database")

        query = """
        SELECT *
        FROM security_zones
        """

        rows = self.storage_manager.execute(query)

        security_zones = []

        for row in rows:
            security_zones.append(SecurityZone(Square(row[3], row[5], row[2], row[4]), list(sensors.keys())))
            security_zones[-1].id = row[0]
            security_zones[-1].enabled = row[1]

        return security_zones

    def add_security_zone(self, security_zone: SecurityZone) -> None:
        query = """
        INSERT INTO "security_zones" ("is_enabled", "up_left_x", "up_left_y", "down_right_x", "down_right_y") VALUES (?, ?, ?, ?, ?) RETURNING security_zone_id
        """

        rows = self.storage_manager.execute(query, (
            security_zone.enabled, security_zone.area.up_left[0], security_zone.area.up_left[1],
            security_zone.area.down_right[0], security_zone.area.down_right[1]))
        security_zone_id = rows[0][0]

        security_zone.id = security_zone_id

    def update_security_zone(self, zone_id: int, security_zone: SecurityZone) -> None:
        query = """
        UPDATE security_zones
        SET is_enabled = ?, up_left_x = ?, up_left_y = ?, down_right_x = ?, down_right_y = ?
        WHERE security_zone_id = ?
        """

        self.storage_manager.execute(query, (
            security_zone.enabled, security_zone.area.up_left[0], security_zone.area.up_left[1],
            security_zone.area.down_right[0], security_zone.area.down_right[1], zone_id))


    def remove_security_zone(self, security_zone_id: int) -> None:
        query = """
        DELETE FROM "security_zones" WHERE security_zone_id = ?
        """

        self.storage_manager.execute(query, (security_zone_id,))
