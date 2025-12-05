from core.security.security_mode.security_mode import SecurityMode
from device.interface_sensor import InterfaceSensor


class Away(SecurityMode):
    def __init__(self, sensors: list[InterfaceSensor]):
        super().__init__([sensors[i] for i in [0, 1, 2]])
        self.name = "Away"
