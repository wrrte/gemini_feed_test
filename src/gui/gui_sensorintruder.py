import tkinter as tk
from core.system import system

class GUISensorIntruder(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Sensor Tester")
        self.geometry("160x400")
        self.resizable(False, False)

        tk.Label(self, text="Sensor Intruder", font=("Arial", 10)).pack(pady=(8, 4))

        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(fill="both", expand=True, padx=8)

        # Store button references
        self.buttons = []

        for i in range(1, 11):
            btn = tk.Button(
                self.btn_frame,
                text=f"Trigger Sensor {i}",
                width=20,
                command=lambda idx=i-1: self.toggle_sensor(idx)
            )
            btn.pack(pady=3)
            self.buttons.append(btn)

        self.status = tk.Label(self, text="", font=("Arial", 9), fg="blue")
        self.status.pack(pady=(6, 6))

    def toggle_sensor(self, index: int) -> None:
        try:
            sensors_list = list(system.current_security_manager.sensors.keys())
            sensor_obj = sensors_list[index]
            button = self.buttons[index]
            text = button.cget("text")

            if text.startswith("Trigger"):
                sensor_obj.intrude()
                button.config(text=f"Release Sensor {index+1}")
                self.status.config(text=f"Triggered sensor #{index+1}", fg="blue")

            else:
                sensor_obj.release()
                button.config(text=f"Trigger Sensor {index+1}")
                self.status.config(text=f"Released sensor #{index+1}", fg="blue")

        except Exception as e:
            self.status.config(text=f"Error: {e}", fg="red")
