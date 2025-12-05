from abc import ABC, abstractmethod


class DeviceSensorTester(ABC):
    """Abstract base class for sensor devices with testing capability."""

    safeHomeSensorTest = None
    safehome_sensor_test = None  # alias for compatibility
    head_WinDoorSensor = None
    head_windoor_sensor = None  # alias
    head_MotionDetector = None
    head_motion_detector = None  # alias
    newIdSequence_WinDoorSensor = 0
    newIdSequence_MotionDetector = 0

    def __init__(self):
        self.next = None
        self.next_sensor = None  # alias
        self.sensor_id = 0  # alias

    @abstractmethod
    def intrude(self):
        """Simulate intrusion/detection."""
        pass

    @abstractmethod
    def release(self):
        """Release intrusion/detection state."""
        pass

    @staticmethod
    def showSensorTester():
        """Show the sensor tester GUI."""
        if DeviceSensorTester.safeHomeSensorTest is not None:
            return
        try:
            import os
            if os.environ.get("SAFEHOME_HEADLESS") == "1":
                return
            import tkinter as tk
            from .safehome_sensor_test_gui import SafeHomeSensorTest
            root = tk._default_root
            if root is None:
                root = tk.Tk()
                root.withdraw()
            gui = SafeHomeSensorTest(master=root)
            # Mirror Java setVisible(true)
            try:
                gui.deiconify()
                gui.lift()
            except Exception:
                pass
            DeviceSensorTester.safeHomeSensorTest = gui
            DeviceSensorTester.safehome_sensor_test = gui
        except Exception:
            # Fail silently in environments without display/Tkinter
            DeviceSensorTester.safeHomeSensorTest = None
            DeviceSensorTester.safehome_sensor_test = None
