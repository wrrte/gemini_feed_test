from core.security.security_mode.security_mode import SecurityMode
from device.interface_sensor import InterfaceSensor


class Home(SecurityMode):
    def __init__(self, sensors: list[InterfaceSensor]):
        super().__init__([sensors[i] for i in [3, 4, 5]])
        self.name = "Home"

