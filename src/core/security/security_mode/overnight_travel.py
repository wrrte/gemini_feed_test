from core.security.security_mode.security_mode import SecurityMode
from device.interface_sensor import InterfaceSensor


class OvernightTravel(SecurityMode):
    def __init__(self, sensors: list[InterfaceSensor]):
        super().__init__([sensors[i] for i in [6, 7]])
        self.name = "Overnight"
