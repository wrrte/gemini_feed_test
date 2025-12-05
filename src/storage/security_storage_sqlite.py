from core.security.security_database_interface import SecurityDBInterface
from core.security.security_mode.security_mode import SecurityMode
from core.security.security_zone import SecurityZone

from storage.sensor_storage_sqlite import SensorSqliteDB
from storage.security_mode_storage_sqlite import SecurityModeSqliteDB
from storage.security_zone_storage_sqlite import SecurityZoneSqliteDB


class SecuritySqliteDB(SecurityDBInterface):
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.sensor_storage = SensorSqliteDB(storage_manager)
        self.security_mode_storage = SecurityModeSqliteDB(storage_manager)
        self.security_zone_storage = SecurityZoneSqliteDB(storage_manager)

    def add_security_mode(self, mode) -> None:
        pass

    def remove_security_mode(self, name: str) -> None:
        pass

    def update_security_mode(self, name: str, mode: SecurityMode) -> None:
        self.security_mode_storage.update_security_mode(name, mode)

    def get_sensors(self):
        return self.sensor_storage.get_sensors()

    def get_security_zones(self):
        return self.security_zone_storage.get_security_zones()

    def get_security_modes(self):
        return self.security_mode_storage.get_security_modes()

    def get_now_security_mode(self) -> int | None:
        return self.security_mode_storage.get_now_security_mode()

    def set_now_security_mode(self, now: int | None) -> None:
        self.security_mode_storage.set_now_security_mode(now)

    def add_sensor(self, sensor, on: bool = True, arm: bool | None = None) -> None:
        pass

    def turn_onoff_sensor(self, sensor, onoff: bool) -> None:
        self.sensor_storage.turn_onoff_sensor(sensor, onoff)

    def remove_sensor(self, sensor) -> None:
        pass

    def update_sensor(self, sensor, data: tuple[bool, bool | None]) -> None:
        self.sensor_storage.update_sensor(sensor, data)

    def add_security_zone(self, security_zone: SecurityZone) -> None:
        self.security_zone_storage.add_security_zone(security_zone)

    def update_security_zone(self, zone_id: int, security_zone: SecurityZone) -> None:
        self.security_zone_storage.update_security_zone(zone_id, security_zone)

    def remove_security_zone(self, security_zone_id: int) -> None:
        self.security_zone_storage.remove_security_zone(security_zone_id)
