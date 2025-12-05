from .device_sensor_tester import DeviceSensorTester
from .interface_sensor import InterfaceSensor
from core.security.security_zone_geometry.area import Point


class DeviceWinDoorSensor(DeviceSensorTester, InterfaceSensor):

    def __init__(self, x: int, y: int):
        super().__init__()

        self.area = Point(x, y)

        # Assign unique ID
        DeviceSensorTester.newIdSequence_WinDoorSensor += 1
        self.sensor_id = DeviceSensorTester.newIdSequence_WinDoorSensor

        # Initialize state
        self.opened = False
        self.armed = False

        # Add to linked list
        self.next = DeviceSensorTester.head_WinDoorSensor
        self.next_sensor = self.next  # alias
        DeviceSensorTester.head_WinDoorSensor = self
        DeviceSensorTester.head_windoor_sensor = self  # alias

        # Update GUI and link heads
        if DeviceSensorTester.safeHomeSensorTest is not None:
            DeviceSensorTester.safeHomeSensorTest.head_windoor = DeviceSensorTester.head_WinDoorSensor
            DeviceSensorTester.safeHomeSensorTest.rangeSensorID_WinDoorSensor.set(
                f"1 ~ {DeviceSensorTester.newIdSequence_WinDoorSensor}")

    def intrude(self):
        """Simulate opening the window/door."""
        self.opened = True

    def release(self):
        """Simulate closing the window/door."""
        self.opened = False

    def get_id(self):
        """Alias for getID."""
        return self.sensor_id

    def read(self):
        """Read the sensor state."""
        if self.armed:
            return self.opened
        return False

    def arm(self):
        """Enable the sensor."""
        self.armed = True

    def disarm(self):
        """Disable the sensor."""
        self.armed = False

    def test_armed_state(self):
        """Test if the sensor is enabled."""
        return self.armed
