from .device_sensor_tester import DeviceSensorTester
from .interface_sensor import InterfaceSensor
from core.security.security_zone_geometry.area import Line


class DeviceMotionDetector(DeviceSensorTester, InterfaceSensor):

    def __init__(self, start: (int, int), end: (int, int)):
        super().__init__()

        self.area = Line(start, end)

        # Assign unique ID
        DeviceSensorTester.newIdSequence_MotionDetector += 1
        self.sensor_id = DeviceSensorTester.newIdSequence_MotionDetector

        # Initialize state
        self.detected = False
        self.armed = False

        # Add to linked list
        self.next = DeviceSensorTester.head_MotionDetector
        self.next_sensor = self.next  # alias
        DeviceSensorTester.head_MotionDetector = self
        DeviceSensorTester.head_motion_detector = self  # alias

        # Update GUI and link heads
        if DeviceSensorTester.safeHomeSensorTest is not None:
            DeviceSensorTester.safeHomeSensorTest.head_motion = DeviceSensorTester.head_MotionDetector
            DeviceSensorTester.safeHomeSensorTest.rangeSensorID_MotionDetector.set(
                f"1 ~ {DeviceSensorTester.newIdSequence_MotionDetector}")

    def intrude(self):
        """Simulate motion detection."""
        self.detected = True

    def release(self):
        """Clear motion detection."""
        self.detected = False

    def get_id(self):
        """Alias for getID."""
        return self.sensor_id

    def read(self):
        """Read the sensor state."""
        if self.armed:
            return self.detected
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
