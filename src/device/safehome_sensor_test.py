import tkinter as tk
from tkinter import Label, Button, messagebox


class SafeHomeSensorTest(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Sensor Test")
        self.geometry("355x170")
        self.resizable(False, False)
        self.config(bg='orange')

        # Left panel - Window/Door Sensors
        left_frame = tk.Frame(self, bg='orange')
        left_frame.place(x=15, y=15, width=150, height=100)

        # Grid layout for left panel
        Label(left_frame, text="      WinDoor", bg='orange').grid(row=0, column=0)
        Label(left_frame, text=" Sensors", bg='orange').grid(row=0, column=1)
        Label(left_frame, text="   ID range", bg='orange').grid(row=1, column=0)
        Label(left_frame, text="   input ID", bg='orange').grid(row=1, column=1)

        self.range_sensor_id_windoor = tk.Entry(left_frame, justify='center',
                                                state='readonly', bg='white', fg='black')
        self.range_sensor_id_windoor.insert(0, "N/A")
        self.range_sensor_id_windoor.grid(row=2, column=0, sticky='ew')

        self.input_sensor_id_windoor = tk.Entry(left_frame, justify='center',
                                                bg='white', fg='black')
        self.input_sensor_id_windoor.grid(row=2, column=1, sticky='ew')

        button_open = Button(left_frame, text="open", bg='light gray',
                             command=lambda: self.handle_windoor_action("open"))
        button_open.grid(row=3, column=0, sticky='ew')

        button_close = Button(left_frame, text="close", bg='light gray',
                              command=lambda: self.handle_windoor_action("close"))
        button_close.grid(row=3, column=1, sticky='ew')

        # Right panel - Motion Detectors
        right_frame = tk.Frame(self, bg='orange')
        right_frame.place(x=180, y=15, width=150, height=100)

        # Grid layout for right panel
        Label(right_frame, text="          Motion", bg='orange').grid(row=0, column=0)
        Label(right_frame, text="Sensors", bg='orange').grid(row=0, column=1)
        Label(right_frame, text="   ID range", bg='orange').grid(row=1, column=0)
        Label(right_frame, text="   input ID", bg='orange').grid(row=1, column=1)

        self.range_sensor_id_motion = tk.Entry(right_frame, justify='center',
                                               state='readonly', bg='white', fg='black')
        self.range_sensor_id_motion.insert(0, "N/A")
        self.range_sensor_id_motion.grid(row=2, column=0, sticky='ew')

        self.input_sensor_id_motion = tk.Entry(right_frame, justify='center',
                                               bg='white', fg='black')
        self.input_sensor_id_motion.grid(row=2, column=1, sticky='ew')

        button_detect = Button(right_frame, text="detect", bg='light gray',
                               command=lambda: self.handle_motion_action("detect"))
        button_detect.grid(row=3, column=0, sticky='ew')

        button_clear = Button(right_frame, text="clear", bg='light gray',
                              command=lambda: self.handle_motion_action("clear"))
        button_clear.grid(row=3, column=1, sticky='ew')

        # Will be set by DeviceSensorTester
        self.head_windoor = None
        self.head_motion = None

    def handle_windoor_action(self, action):
        """Handle Window/Door sensor actions (open/close)."""
        input_number = self.input_sensor_id_windoor.get().strip()

        if not input_number:
            messagebox.showwarning("Input Error", "input the WinDoorSensor's ID")
            return

        if not input_number.isdigit():
            messagebox.showwarning("Input Error", "only digit allowed")
            return

        selected_id = int(input_number)

        # Search for sensor with matching ID
        scan = self.head_windoor
        while scan is not None and scan.sensor_id != selected_id:
            scan = scan.next_sensor

        if scan is None:
            messagebox.showwarning("Sensor Not Found", f"ID {selected_id} not exist")
        else:
            if action == "open":
                scan.intrude()
            else:  # close
                scan.release()

    def handle_motion_action(self, action):
        """Handle Motion Detector actions (detect/clear)."""
        input_number = self.input_sensor_id_motion.get().strip()

        if not input_number:
            messagebox.showwarning("Input Error", "input the MotionDetector's ID")
            return

        if not input_number.isdigit():
            messagebox.showwarning("Input Error", "only digit allowed")
            return

        selected_id = int(input_number)

        # Search for sensor with matching ID
        scan = self.head_motion
        while scan is not None and scan.sensor_id != selected_id:
            scan = scan.next_sensor

        if scan is None:
            messagebox.showwarning("Sensor Not Found", f"ID {selected_id} not exist")
        else:
            if action == "detect":
                scan.intrude()
            else:  # clear
                scan.release()


if __name__ == "__main__":
    # Test the sensor GUI
    root = tk.Tk()
    root.withdraw()  # Hide main window

    sensor_test = SafeHomeSensorTest(root)
    print("Sensor Test GUI started")
    sensor_test.mainloop()
