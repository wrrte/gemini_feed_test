from device.interface_sensor import InterfaceSensor


class SecurityMode:
    def __init__(self, sensors: list[InterfaceSensor], name: str = "None") -> None:
        self.name: str = name
        self.sensors: list[InterfaceSensor] = sensors

    def get_arm_sensors(self) -> list[InterfaceSensor]:
        return self.sensors
