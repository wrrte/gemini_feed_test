from core.security.security_database_interface import SensorDBInterface
from storage.storage_sqlite import StorageManager
from device.device_motion_detector import DeviceMotionDetector
from device.device_windoor_sensor import DeviceWinDoorSensor
from device.interface_sensor import InterfaceSensor

import json


class SensorSqliteDB(SensorDBInterface):
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager

    def get_sensors(self) -> dict[InterfaceSensor, tuple[bool, bool | None]]:
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

        return sensors

    def add_sensor(self, sensor: InterfaceSensor, on: bool = True, arm: bool | None = None) -> None:
        pass

    def turn_onoff_sensor(self, sensor: InterfaceSensor, onoff: bool) -> None:
        # InterfaceSensor have get_id() so compare id.
        query = """
        UPDATE sensors
        SET is_enabled=?
        WHERE sensor_id=?
        """

        self.storage_manager.execute(query, (onoff, sensor.get_id()))

    def remove_sensor(self, sensor: InterfaceSensor) -> None:
        pass

    def update_sensor(self, sensor: InterfaceSensor, data) -> None:
        # InterfaceSensor have get_id() so compare id.
        query = """
        UPDATE sensors
        SET is_enabled=?, is_armed=?
        WHERE sensor_id=?
        """

        self.storage_manager.execute(query, (data[0], data[1], sensor.get_id()))
