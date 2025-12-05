
from core.security.security_database_interface import SecurityDBInterface
from core.security.security_mode.away import Away
from core.security.security_mode.extended_travel import ExtendedTravel
from core.security.security_mode.home import Home
from core.security.security_mode.security_mode import SecurityMode
from core.security.security_mode.overnight_travel import OvernightTravel
from core.security.security_zone import SecurityZone
from device.device_motion_detector import DeviceMotionDetector
from device.device_windoor_sensor import DeviceWinDoorSensor
from device.interface_sensor import InterfaceSensor


class SecurityMemoryDatabase(SecurityDBInterface):
    def __init__(self):
        super().__init__()
        self.sensors: dict[InterfaceSensor, tuple[bool, bool | None]] = {
            DeviceWinDoorSensor(20, 80): (True, None),
            DeviceWinDoorSensor(70, 20): (True, None),
            DeviceWinDoorSensor(20, 200): (True, None),
            DeviceWinDoorSensor(400, 20): (True, None),
            DeviceWinDoorSensor(470, 80): (True, None),
            DeviceWinDoorSensor(475, 210): (True, None),
            DeviceWinDoorSensor(250, 20): (True, None),
            DeviceWinDoorSensor(80, 280): (True, None),
            DeviceMotionDetector((30, 80), (465, 80)): (True, None),
            DeviceMotionDetector((145, 170), (25, 248)): (True, None),
        }
        self.security_zones: list[SecurityZone] = []
        self.security_modes: list[SecurityMode] = [
            Home(list(self.sensors.keys())),
            Away(list(self.sensors.keys())),
            OvernightTravel(list(self.sensors.keys())),
            ExtendedTravel(list(self.sensors.keys()))
        ]
        self.now_security_mode: int | None = None

    def add_security_mode(self, mode: SecurityMode) -> None:
        pass

    def remove_security_mode(self, name: str) -> None:
        pass

    def update_security_mode(self, name: str, mode: SecurityMode) -> None:
        pass

    def get_sensors(self) -> dict[InterfaceSensor, tuple[bool, bool | None]]:
        return self.sensors

    def get_security_zones(self) -> list[SecurityZone]:
        return self.security_zones

    def get_security_modes(self) -> list[SecurityMode]:
        return self.security_modes

    def get_now_security_mode(self) -> int | None:
        return self.now_security_mode

    def set_now_security_mode(self, now: int | None) -> None:
        self.now_security_mode = now

    def add_sensor(self, sensor: InterfaceSensor, on: bool = True, arm: bool | None = None) -> None:
        pass

    def turn_onoff_sensor(self, sensor: InterfaceSensor, onoff: bool) -> None:
        pass

    def remove_sensor(self, sensor: InterfaceSensor) -> None:
        pass

    def update_sensor(self, sensor: InterfaceSensor, data: tuple[bool, bool | None]) -> None:
        pass

    def add_security_zone(self, security_zone: SecurityZone) -> None:
        pass

    def update_security_zone(self, zone_id: int, security_zone: SecurityZone) -> None:
        pass

    def remove_security_zone(self, security_zone_id: int) -> None:
        pass
