import tkinter as tk
from tkinter import ttk, messagebox

from .device_sensor_tester import DeviceSensorTester


class SafeHomeSensorTest(tk.Toplevel):
    """Tkinter translation of the Java SafeHomeSensorTest GUI.

    This GUI allows the user to input a sensor ID and call open/close or
    detect/clear on registered sensors by ID. It uses the DeviceSensorTester
    head_* linked lists to find sensors.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Sensor Test")
        self.geometry("500x450")
        self.resizable(False, False)

        self.rangeSensorID_WinDoorSensor = tk.StringVar(value="N/A")
        self.inputSensorID_WinDoorSensor = tk.StringVar()

        self.rangeSensorID_MotionDetector = tk.StringVar(value="N/A")
        self.inputSensorID_MotionDetector = tk.StringVar()

        # WinDoor panel
        wd_frame = ttk.Frame(self)
        wd_frame.place(x=15, y=15, width=225, height=130)
        ttk.Label(wd_frame, text="      WinDoor Sensor").grid(row=0, column=0, columnspan=2)
        ttk.Label(wd_frame, text="   ID range").grid(row=1, column=0)
        ttk.Label(wd_frame, text="   input ID").grid(row=2, column=0)
        ttk.Entry(wd_frame, textvariable=self.rangeSensorID_WinDoorSensor, state="readonly", width=10).grid(row=1,
                                                                                                            column=1)
        ttk.Entry(wd_frame, textvariable=self.inputSensorID_WinDoorSensor, width=10).grid(row=2, column=1)

        # Sensor control buttons (Arm/Disarm)
        ttk.Label(wd_frame, text="Sensor Control:").grid(row=3, column=0, columnspan=2, pady=(5, 0))
        ttk.Button(wd_frame, text="Arm", command=lambda: self._handle_windoor_sensor("arm")).grid(row=4, column=0,
                                                                                                  padx=2)
        ttk.Button(wd_frame, text="Disarm", command=lambda: self._handle_windoor_sensor("disarm")).grid(row=4, column=1,
                                                                                                        padx=2)

        # Door control buttons (Open/Close)
        ttk.Label(wd_frame, text="Door Control:").grid(row=5, column=0, columnspan=2, pady=(5, 0))
        ttk.Button(wd_frame, text="Open", command=lambda: self._handle_windoor("open")).grid(row=6, column=0, padx=2)
        ttk.Button(wd_frame, text="Close", command=lambda: self._handle_windoor("close")).grid(row=6, column=1, padx=2)

        # Motion panel
        md_frame = ttk.Frame(self)
        md_frame.place(x=260, y=15, width=225, height=130)
        ttk.Label(md_frame, text="      Motion Detector").grid(row=0, column=0, columnspan=2)
        ttk.Label(md_frame, text="   ID range").grid(row=1, column=0)
        ttk.Label(md_frame, text="   input ID").grid(row=2, column=0)
        ttk.Entry(md_frame, textvariable=self.rangeSensorID_MotionDetector, state="readonly", width=10).grid(row=1,
                                                                                                             column=1)
        ttk.Entry(md_frame, textvariable=self.inputSensorID_MotionDetector, width=10).grid(row=2, column=1)

        # Sensor control buttons (Arm/Disarm)
        ttk.Label(md_frame, text="Sensor Control:").grid(row=3, column=0, columnspan=2, pady=(5, 0))
        ttk.Button(md_frame, text="Arm", command=lambda: self._handle_motion_sensor("arm")).grid(row=4, column=0,
                                                                                                 padx=2)
        ttk.Button(md_frame, text="Disarm", command=lambda: self._handle_motion_sensor("disarm")).grid(row=4, column=1,
                                                                                                       padx=2)

        # Motion control buttons (Detect/Clear)
        ttk.Label(md_frame, text="Motion Control:").grid(row=5, column=0, columnspan=2, pady=(5, 0))
        ttk.Button(md_frame, text="Detect", command=lambda: self._handle_motion("detect")).grid(row=6, column=0, padx=2)
        ttk.Button(md_frame, text="Clear", command=lambda: self._handle_motion("clear")).grid(row=6, column=1, padx=2)

        # Status display frame
        status_frame = ttk.LabelFrame(self, text="Sensor Status", padding=10)
        status_frame.place(x=15, y=160, width=470, height=270)

        # WinDoor status
        ttk.Label(status_frame, text="Window/Door Sensors:", font=("Arial", 9, "bold")).grid(row=0, column=0,
                                                                                             columnspan=3, sticky="w",
                                                                                             pady=(0, 5))
        self.wd_status_text = tk.Text(status_frame, height=5, width=53, font=("Courier", 9), state="disabled")
        self.wd_status_text.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Motion status
        ttk.Label(status_frame, text="Motion Detectors:", font=("Arial", 9, "bold")).grid(row=2, column=0, columnspan=3,
                                                                                          sticky="w", pady=(0, 5))
        self.motion_status_text = tk.Text(status_frame, height=5, width=53, font=("Courier", 9), state="disabled")
        self.motion_status_text.grid(row=3, column=0, columnspan=3)

        # Start status update loop
        self._update_status()

    def _update_status(self):
        """Update sensor status display every 500ms."""
        # Update WinDoor status
        self.wd_status_text.config(state="normal")
        self.wd_status_text.delete(1.0, tk.END)

        scan = DeviceSensorTester.head_WinDoorSensor
        if scan is None:
            self.wd_status_text.insert(tk.END, "No sensors registered\n")
        else:
            while scan is not None:
                sensor_id = getattr(scan, "sensor_id", getattr(scan, "sensorID", "?"))
                # Prefer explicit test method when available, fall back to known attrs
                if callable(getattr(scan, "test_armed_state", None)):
                    try:
                        armed = bool(scan.test_armed_state())
                    except Exception:
                        armed = False
                else:
                    armed = getattr(scan, "amred", getattr(scan, "armed", getattr(scan, "enabled", False)))
                opened = getattr(scan, "opened", False)

                # Separate status display: Sensor ON/OFF | Door OPEN/CLOSED
                sensor_status = "🟢 ON " if armed else "🔴 OFF"
                door_status = "🚪 OPEN  " if opened else "🚪 CLOSED"
                self.wd_status_text.insert(tk.END, f"ID {sensor_id}: Sensor[{sensor_status}] Door[{door_status}]\n")
                scan = getattr(scan, "next", None)

        self.wd_status_text.config(state="disabled")

        # Update Motion status
        self.motion_status_text.config(state="normal")
        self.motion_status_text.delete(1.0, tk.END)

        scan = DeviceSensorTester.head_MotionDetector
        if scan is None:
            self.motion_status_text.insert(tk.END, "No detectors registered\n")
        else:
            while scan is not None:
                sensor_id = getattr(scan, "sensor_id", getattr(scan, "sensorID", "?"))
                # Prefer explicit test method when available, fall back to known attrs
                if callable(getattr(scan, "test_armed_state", None)):
                    try:
                        armed = bool(scan.test_armed_state())
                    except Exception:
                        armed = False
                else:
                    armed = getattr(scan, "enabled", getattr(scan, "armed", getattr(scan, "amred", False)))
                detected = getattr(scan, "detected", False)

                # Separate status display: Sensor ON/OFF | Motion DETECTED/CLEAR
                sensor_status = "🟢 ON " if armed else "🔴 OFF"
                motion_status = "👁️  DETECTED" if detected else "⚪ CLEAR   "
                self.motion_status_text.insert(tk.END,
                                               f"ID {sensor_id}: Sensor[{sensor_status}] Motion[{motion_status}]\n")
                scan = getattr(scan, "next", None)

        self.motion_status_text.config(state="disabled")

        # Schedule next update
        self.after(500, self._update_status)

    def _validate_digits(self, s: str) -> bool:
        return s.isdigit() if s else False

    def _handle_windoor_sensor(self, action: str):
        """Handle Window/Door sensor arm/disarm."""
        inputNumber = self.inputSensorID_WinDoorSensor.get()
        if inputNumber == "":
            messagebox.showinfo(self.title(), "input the WinDoorSensor's ID")
            return
        if not self._validate_digits(inputNumber):
            messagebox.showinfo(self.title(), "only digit allowed")
            return
        selectedID = int(inputNumber)
        scan = DeviceSensorTester.head_WinDoorSensor
        while scan is not None and getattr(scan, "sensor_id", getattr(scan, "sensorID", None)) != selectedID:
            scan = getattr(scan, "next", None)
        if scan is None:
            messagebox.showinfo(self.title(), f"ID {selectedID} not exist")
        else:
            if action == "arm":
                scan.arm()
            else:
                scan.disarm()
            # Immediately update status display
            self._update_status()

    def _handle_windoor(self, action: str):
        inputNumber = self.inputSensorID_WinDoorSensor.get()
        if inputNumber == "":
            messagebox.showinfo(self.title(), "input the WinDoorSensor's ID")
            return
        if not self._validate_digits(inputNumber):
            messagebox.showinfo(self.title(), "only digit allowed")
            return
        selectedID = int(inputNumber)
        scan = DeviceSensorTester.head_WinDoorSensor
        while scan is not None and getattr(scan, "sensor_id", getattr(scan, "sensorID", None)) != selectedID:
            scan = getattr(scan, "next", None)
        if scan is None:
            messagebox.showinfo(self.title(), f"ID {selectedID} not exist")
        else:
            if action == "open":
                scan.intrude()
            else:
                scan.release()
            # Immediately update status display
            self._update_status()

    def _handle_motion_sensor(self, action: str):
        """Handle Motion Detector arm/disarm."""
        inputNumber = self.inputSensorID_MotionDetector.get()
        if inputNumber == "":
            messagebox.showinfo(self.title(), "input the MotionDetector's ID")
            return
        if not self._validate_digits(inputNumber):
            messagebox.showinfo(self.title(), "only digit allowed")
            return
        selectedID = int(inputNumber)
        scan = DeviceSensorTester.head_MotionDetector
        while scan is not None and getattr(scan, "sensor_id", getattr(scan, "sensorID", None)) != selectedID:
            scan = getattr(scan, "next", None)
        if scan is None:
            messagebox.showinfo(self.title(), f"ID {selectedID} not exist")
        else:
            if action == "arm":
                scan.arm()
            else:
                scan.disarm()
            # Immediately update status display
            self._update_status()

    def _handle_motion(self, action: str):
        inputNumber = self.inputSensorID_MotionDetector.get()
        if inputNumber == "":
            messagebox.showinfo(self.title(), "input the MotionDetector's ID")
            return
        if not self._validate_digits(inputNumber):
            messagebox.showinfo(self.title(), "only digit allowed")
            return
        selectedID = int(inputNumber)
        scan = DeviceSensorTester.head_MotionDetector
        while scan is not None and getattr(scan, "sensor_id", getattr(scan, "sensorID", None)) != selectedID:
            scan = getattr(scan, "next", None)
        if scan is None:
            messagebox.showinfo(self.title(), f"ID {selectedID} not exist")
        else:
            if action == "detect":
                scan.intrude()
            else:
                scan.release()
            # Immediately update status display
            self._update_status()
