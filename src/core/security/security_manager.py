from typing import Optional

from core.log.log import Log
from core.log.log_manager import LogManager
from core.security.alarm import Alarm
from core.security.security_database_interface import SecurityDBInterface
from core.security.security_exceptions import (
    SensorAlreadyExistsError,
    SensorNotFoundError,
    SecurityModeNotFoundError,
    SecurityModeAlreadyExistsError,
    SecurityZoneNotFoundError
)
from core.security.security_mode.security_mode import SecurityMode
from core.security.security_zone import SecurityZone, security_zone_id
from core.security.security_zone_geometry.area import Square
from core.security.sensor_controller import SensorController
from device.interface_sensor import InterfaceSensor


class SecurityManager:
    # security system will be turned on if SecurityManager is made.
    def __init__(self, db_manager: SecurityDBInterface, log_manager: LogManager):
        # sensor: (on/off, arm/disarm/none)

        self.db_manager: SecurityDBInterface = db_manager
        self.sensors: dict[InterfaceSensor, tuple[bool, bool | None]] = db_manager.get_sensors()
        self.security_zones: list[SecurityZone] = db_manager.get_security_zones()
        for zone in self.security_zones:
            security_zone_id.add(zone.id)
            zone.update(zone.area, list(self.sensors.keys()))

        self.security_modes: list[SecurityMode] = db_manager.get_security_modes()

        for mode in self.security_modes:
            ids = list(map(lambda sensor: sensor.get_id(), mode.sensors))
            new_sensors = list(filter(lambda sensor: sensor.get_id() in ids, self.sensors))
            mode.sensors = new_sensors

        self.now_security_mode: int | None = db_manager.get_now_security_mode()

        self.sensor_controller: SensorController = SensorController(self.sensors)
        self.default_zone: tuple[int, int, int, int] = (150, 200, 210, 240)
        self.alarm: Alarm = Alarm()
        self.bypass: set[InterfaceSensor] = set()
        self.log_manager: LogManager = log_manager

    def add_sensor(self, sensor: InterfaceSensor, on: bool = True, arm: bool | None = None) -> None:
        if sensor not in self.sensors:
            self.sensors[sensor] = (on, arm)
        else:
            raise SensorAlreadyExistsError()
        self.db_manager.add_sensor(sensor, on, arm)

    def turn_on_sensor(self, sensor: InterfaceSensor) -> None:
        if sensor in self.sensors:
            tmp = self.sensors[sensor]
            self.sensors[sensor] = (True, tmp[1])
        else:
            raise SensorNotFoundError()
        self.db_manager.turn_onoff_sensor(sensor, True)

    def turn_off_sensor(self, sensor: InterfaceSensor) -> None:
        if sensor in self.sensors:
            tmp = self.sensors[sensor]
            self.sensors[sensor] = (False, tmp[1])
        else:
            raise SensorNotFoundError()
        self.db_manager.turn_onoff_sensor(sensor, False)

    def set_onoff_sensor(self, sensor: InterfaceSensor, on: bool = True) -> None:
        if sensor in self.sensors:
            tmp = self.sensors[sensor]
            self.sensors[sensor] = (on, tmp[1])
        else:
            raise SensorNotFoundError()
        self.db_manager.turn_onoff_sensor(sensor, on)

    def remove_sensor(self, sensor: InterfaceSensor) -> tuple[bool, bool | None]:
        if sensor not in self.sensors:
            raise SensorNotFoundError()
        self.db_manager.remove_sensor(sensor)
        return self.sensors.pop(sensor)

    def set_security_mode_index(self, mode: int | None) -> None:
        if mode is None:
            self.now_security_mode = None
        else:
            if 0 <= mode < len(self.security_modes):
                self.now_security_mode = mode
            else:
                raise SecurityModeNotFoundError()
        self.db_manager.set_now_security_mode(self.now_security_mode)

    def set_security_mode_name(self, name: str) -> None:
        for i in range(len(self.security_modes)):
            if self.security_modes[i].name == name:
                self.now_security_mode = i
                self.db_manager.set_now_security_mode(i)
                return
        raise SecurityModeNotFoundError()

    def get_security_mode(self, name: str) -> SecurityMode | None:
        for mode in self.security_modes:
            if mode.name == name:
                return mode
        raise SecurityModeNotFoundError()

    def add_security_mode(self, name: str) -> SecurityMode | None:
        for mode in self.security_modes:
            if mode.name == name:
                raise SecurityModeAlreadyExistsError()
        tmp = SecurityMode([], name)
        self.db_manager.add_security_mode(tmp)
        self.security_modes.append(tmp)

    def update_security_mode(self, name: str, sensors: list[InterfaceSensor]) -> None:
        for mode in self.security_modes:
            if mode.name == name:
                mode.sensors = sensors
                self.db_manager.update_security_mode(name, mode)
                return
        raise SecurityModeNotFoundError()

    def remove_security_mode(self, name: str) -> None:
        for mode in self.security_modes:
            if mode.name == name:
                self.security_modes.remove(mode)
                self.db_manager.remove_security_mode(name)
                return
        raise SecurityModeNotFoundError()

    def add_security_zone(self) -> SecurityZone:
        new_zone = SecurityZone(Square(*self.default_zone),
                                list(self.sensors.keys()))
        self.security_zones.append(new_zone)
        self.db_manager.add_security_zone(new_zone)
        return new_zone

    def update_security_zone(self, zone_id: int, area: Square) -> list[InterfaceSensor] | None:
        for security_zone in self.security_zones:
            if security_zone.id == zone_id:
                security_zone.update(area, list(
                    self.sensors.keys()))
                self.db_manager.update_security_zone(zone_id, security_zone)
                return security_zone.sensors
        raise SecurityZoneNotFoundError()

    def remove_security_zone(self, zone_id: int) -> None:
        for security_zone in self.security_zones:
            if security_zone.id == zone_id:
                self.security_zones.remove(security_zone)
                self.db_manager.remove_security_zone(zone_id)
                return
        raise SecurityZoneNotFoundError()

    def arm_security_zone(self, zone_id: int) -> None:
        for security_zone in self.security_zones:
            if security_zone.id == zone_id:
                security_zone.enable()
                self.db_manager.update_security_zone(zone_id, security_zone)
                return
        raise SecurityZoneNotFoundError()

    def disarm_security_zone(self, zone_id: int) -> None:
        for security_zone in self.security_zones:
            if security_zone.id == zone_id:
                security_zone.disable()
                self.db_manager.update_security_zone(zone_id, security_zone)
                return
        raise SecurityZoneNotFoundError()

    def set_arm_security_zone(self, zone_id: int, arm: bool) -> None:
        for security_zone in self.security_zones:
            if security_zone.id == zone_id:
                security_zone.enabled = arm
                self.db_manager.update_security_zone(zone_id, security_zone)
                return
        raise SecurityZoneNotFoundError()

    def sensor_bypass(self, sensor: InterfaceSensor) -> None:
        self.bypass.add(sensor)

    def sensor_bypass_finish(self, sensor: InterfaceSensor) -> None:
        if sensor not in self.bypass:
            raise SensorNotFoundError()
        self.bypass.remove(sensor)

    def arm(self, sensor: InterfaceSensor) -> None:
        if sensor in self.sensors:
            tmp = self.sensors[sensor]
            self.sensors[sensor] = (tmp[0], True)
            self.db_manager.update_sensor(sensor, (tmp[0], True))
            return
        raise SensorNotFoundError()

    def disarm(self, sensor: InterfaceSensor) -> None:
        if sensor in self.sensors:
            tmp = self.sensors[sensor]
            self.sensors[sensor] = (tmp[0], False)
            self.db_manager.update_sensor(sensor, (tmp[0], False))
            return
        raise SensorNotFoundError()

    def set_arm(self, sensor: InterfaceSensor, arm: bool | None) -> None:
        if sensor in self.sensors:
            tmp = self.sensors[sensor]
            self.sensors[sensor] = (tmp[0], arm)
            self.db_manager.update_sensor(sensor, (tmp[0], arm))
            return
        raise SensorNotFoundError()

    def update(self, detected_sensor_reset: bool = False) -> \
            tuple[dict[InterfaceSensor, Optional[bool]], list[InterfaceSensor]]:
        for sensor in self.sensors.keys():
            sensor.disarm()

        # 1. security mode
        if self.now_security_mode is not None:
            if 0 <= self.now_security_mode < len(self.security_modes):
                mode = self.security_modes[self.now_security_mode]
                for sensor in mode.get_arm_sensors():
                    sensor.arm()
            else:
                self.now_security_mode = None

        # 2. security zone
        for security_zone in self.security_zones:
            if security_zone.enabled:
                for sensor in security_zone.sensors:
                    sensor.arm()
            else:
                pass

        # 3. each sensor
        for sensor, status in self.sensors.items():
            if status[1] is None:
                continue
            elif status[1]:
                sensor.arm()
            else:
                sensor.disarm()

        result, armed_detected = self.sensor_controller.read()
        det = False
        for detected in armed_detected:
            if detected in self.bypass:
                continue
            else:
                self.alarm.siren()
                det = True

        if det:
            tmp = Log()
            tmp.date_time = self.log_manager.get_time()
            tmp.description = str([s.get_id() for s in armed_detected])
            self.log_manager.save_log(tmp)

        if detected_sensor_reset:
            for sensor in armed_detected:
                try:
                    sensor.release()
                except Exception:  # it doesn't have to be covered.
                    pass

        return result, armed_detected
