from typing import Optional

from device.interface_sensor import InterfaceSensor


class SensorController:
    def __init__(self, sensors: dict[InterfaceSensor, tuple[bool, bool | None]]):
        self.sensors = sensors

    def read(self) -> tuple[dict[InterfaceSensor, Optional[bool]], list[InterfaceSensor]]:
        result: dict[InterfaceSensor, Optional[bool]] = {sensor: None for sensor in self.sensors.keys()}
        armed_detected: list[InterfaceSensor] = []
        for sensor, on in self.sensors.items():
            # assert on[0]
            if not on[0]:
                continue
            tmp = sensor.read()
            result[sensor] = tmp
            if tmp and sensor.armed:
                armed_detected.append(sensor)
        return result, armed_detected
