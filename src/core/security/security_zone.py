from core.security.security_zone_geometry.area import Square
from device.interface_sensor import InterfaceSensor

security_zone_id: set[int] = set()


class SecurityZone:
    def __init__(self, area: Square, sensors: list[InterfaceSensor]):
        global security_zone_id
        new_id = 1
        while new_id in security_zone_id:
            new_id += 1
        self.id: int = new_id
        security_zone_id.add(self.id)
        self.area = area
        self.sensors: list[InterfaceSensor] = []
        self.enabled = True
        for sensor in sensors:
            if sensor.area is not None:
                if sensor.area.overlap(self.area):
                    self.sensors.append(sensor)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def update(self, area: Square, sensors: list[InterfaceSensor]) -> None:
        self.area = area
        self.sensors: list[InterfaceSensor] = []
        for sensor in sensors:
            if sensor.area is not None:
                if sensor.area.overlap(self.area):
                    self.sensors.append(sensor)
