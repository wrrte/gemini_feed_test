from abc import ABC

from core.security.security_mode.security_mode import SecurityMode
from core.security.security_zone import SecurityZone
from device.interface_sensor import InterfaceSensor


class SecurityModeDBInterface(ABC):
    def get_security_modes(self) -> list[SecurityMode]:
        pass

    def get_now_security_mode(self) -> int | None:
        pass

    def set_now_security_mode(self, now: int | None) -> None:
        pass

    def add_security_mode(self, mode: SecurityMode) -> None:
        pass

    def remove_security_mode(self, name: str) -> None:
        pass

    def update_security_mode(self, name: str, mode: SecurityMode) -> None:
        pass


class SensorDBInterface(ABC):
    def get_sensors(self) -> dict[InterfaceSensor, tuple[bool, bool | None]]:
        pass

    def add_sensor(self, sensor: InterfaceSensor, on: bool = True, arm: bool | None = None) -> None:
        pass

    def turn_onoff_sensor(self, sensor: InterfaceSensor, onoff: bool) -> None:
        # InterfaceSensor have get_id() so compare id.
        pass

    def remove_sensor(self, sensor: InterfaceSensor) -> None:
        # InterfaceSensor have get_id() so compare id.
        pass

    def update_sensor(self, sensor: InterfaceSensor, data: tuple[bool, bool | None]) -> None:
        # InterfaceSensor have get_id() so compare id.
        pass


class SecurityZoneDBInterface(ABC):
    def get_security_zones(self) -> list[SecurityZone]:
        pass

    def add_security_zone(self, security_zone: SecurityZone) -> None:
        pass

    def update_security_zone(self, zone_id: int, security_zone: SecurityZone) -> None:
        pass

    def remove_security_zone(self, security_zone_id: int) -> None:
        pass


class SecurityDBInterface(SecurityModeDBInterface, SensorDBInterface, SecurityZoneDBInterface):
    def __init__(self) -> None:
        pass
