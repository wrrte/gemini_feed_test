import tkinter as tk
from typing import Any
from PIL import Image, ImageTk
import os
from core.system import system


class SecurityModePage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(parent)
        self.controller = controller

        # --- Main container ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # --- Canvas left ---
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            canvas_frame,
            text="SECURITY MODES",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "../img/img_floorplan.png")

        floorplan_img = Image.open(image_path).resize((500, 300))
        self.floorplan_tk = ImageTk.PhotoImage(floorplan_img)

        self.canvas = tk.Canvas(canvas_frame, width=500, height=300)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.create_image(0, 0, anchor="nw", image=self.floorplan_tk)

        self.sensors = {
            "Sensor 1": {"pos": (20, 80), "enabled": True},
            "Sensor 2": {"pos": (70, 20), "enabled": True},
            "Sensor 3": {"pos": (20, 200), "enabled": False},
            "Sensor 4": {"pos": (400, 20), "enabled": False},
            "Sensor 5": {"pos": (470, 80), "enabled": False},
            "Sensor 6": {"pos": (475, 210), "enabled": False},
            "Sensor 7": {"pos": (250, 20), "enabled": False},
            "Sensor 8": {"pos": (80, 280), "enabled": False},
            "Sensor 9": {"pos": (245, 80), "enabled": False},
            "Sensor 10": {"pos": (90, 205), "enabled": False},
        }

        self.sensor_icons = {}
        self.create_sensor_icons()
        self.refresh_sensor_states()

        # --- Sidebar right ---
        sidebar = tk.Frame(main_frame, width=200, bd=2, relief="groove")
        sidebar.pack(side="right", fill="y", padx=10, pady=10)

        self.selected_sensor = None

        # --- Security mode selection ---
        tk.Label(sidebar, text="SECURITY MODES", font=("Arial", 12, "bold")).pack(pady=(20, 5))

        mode_frame = tk.Frame(sidebar)
        mode_frame.pack(fill="x", pady=(0, 10))

        self.security_modes = ["Home", "Away", "Overnight", "Extended"]
        self.current_mode = None
        self.mode_buttons = {}

        for mode in self.security_modes:
            btn = tk.Button(mode_frame, text=mode, width=12,
                            relief="raised", command=lambda m=mode: self.select_mode(m))
            btn.pack(fill="x", pady=2)
            self.mode_buttons[mode] = btn

        # --- Save button ---
        self.save_button = tk.Button(sidebar, text="Save Current State to Mode", command=self.save_current_mode)
        self.save_button.pack(fill="x", pady=(5, 5))

        tk.Label(sidebar, text="ALL SENSORS", font=("Arial", 12, "bold")).pack(pady=(5, 5))

        # --- Arm/Disarm All ---
        self.arm_button = tk.Button(sidebar, text="Arm All", command=self.arm_all)
        self.arm_button.pack(fill="x", pady=2)

        self.disarm_button = tk.Button(sidebar, text="Disarm All", command=self.disarm_all)
        self.disarm_button.pack(fill="x", pady=(0, 2))

        self.default_button = tk.Button(sidebar, text="Default All", command=self.default_all)
        self.default_button.pack(fill="x", pady=(0, 10))

        # Log/message
        self.message_label = tk.Label(sidebar, text="", fg="blue", anchor="w", justify="left")
        self.message_label.pack(side="bottom", fill="x", pady=(10, 0))

        if system.current_security_manager.now_security_mode is not None:
            current_mode_name = system.current_security_manager.security_modes[
                system.current_security_manager.now_security_mode
            ].name
            self.select_mode(current_mode_name)

    def refresh_sensor_states(self):
        """Sync GUI sensor enabled state with backend sensor armed state."""
        system.current_security_manager.update()
        system_sensors = list(system.current_security_manager.sensors.keys())

        for i, (name, gui_sensor) in enumerate(self.sensors.items()):
            if i >= len(system_sensors):
                break

            sensor_obj = system_sensors[i]

            gui_sensor["enabled"] = sensor_obj.armed

            icon = [icon for icon, n in self.sensor_icons.items() if n == name][0]
            color = "green" if sensor_obj.armed else "red"
            self.canvas.itemconfig(icon, fill=color)

    # --- Create icons ---
    def create_sensor_icons(self) -> None:
        for name, info in self.sensors.items():
            x, y = info["pos"]
            r = 8
            color = "green" if info["enabled"] else "red"

            icon = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline="black", width=2
            )

            self.sensor_icons[icon] = name
            self.canvas.tag_bind(icon, "<Button-1>", self.sensor_clicked)

    def sensor_clicked(self, event: tk.Event) -> None:
        clicked_items = self.canvas.find_withtag("current")
        if not clicked_items:
            return

        icon = clicked_items[0]
        name = self.sensor_icons[icon]

        self.selected_sensor = name

        # --- BACKEND ARM/DISARM ---
        system_sensors = list(system.current_security_manager.sensors.keys())
        index = list(self.sensors.keys()).index(name)
        sensor_obj = system_sensors[index]

        new_state = not sensor_obj.armed
        system.current_security_manager.set_arm(sensor_obj, new_state)
        self.refresh_sensor_states()
        self.log(f"{name} {'ARMED' if new_state else 'DISARMED'}")

    def toggle_enabled(self):
        if not self.selected_sensor:
            return

        # get backend object
        system_sensors = list(system.current_security_manager.sensors.keys())
        index = list(self.sensors.keys()).index(self.selected_sensor)
        sensor_obj = system_sensors[index]

        system.current_security_manager.set_arm(sensor_obj, not sensor_obj.armed)

        self.refresh_sensor_states()

        self.log(f"{self.selected_sensor} {'ENABLED' if sensor_obj.armed else 'DISABLED'}")

    def save_current_mode(self) -> None:
        if not self.current_mode:
            self.log("Select a mode first.")
            return

        # Get backend sensor objects
        system_sensors = list(system.current_security_manager.sensors.keys())

        # Filter only those that are currently ARMED
        armed_sensors = [s for s in system_sensors if s.armed]

        # Save armed sensors to backend mode
        system.current_security_manager.update_security_mode(
            self.current_mode,
            armed_sensors,
        )

        for sensor_obj in system_sensors:
            system.current_security_manager.set_arm(sensor_obj, None)

        self.log(f"Mode '{self.current_mode}' saved ({len(armed_sensors)} sensors armed).")

    def select_mode(self, mode: str) -> None:
        self.current_mode = mode

        # Update button appearances
        for m, btn in self.mode_buttons.items():
            if m == mode:
                btn.config(relief="sunken", bg="lightblue")
            else:
                btn.config(relief="raised", bg="SystemButtonFace")

        system.current_security_manager.set_security_mode_name(mode)

        if system.current_control_panel:
            if mode == "Home":
                system.current_control_panel.set_display_stay(True)
                system.current_control_panel.set_display_away(False)
            elif mode == "Away":
                system.current_control_panel.set_display_stay(False)
                system.current_control_panel.set_display_away(True)
            else:
                system.current_control_panel.set_display_stay(False)
                system.current_control_panel.set_display_away(False)

        self.refresh_sensor_states()

        self.log(f"Mode applied: {mode}")

    def arm_all(self):
        system_sensors = list(system.current_security_manager.sensors.keys())

        for sensor_obj in system_sensors:
            system.current_security_manager.arm(sensor_obj)
        self.refresh_sensor_states()
        self.log("All sensors ARMED")

    def disarm_all(self):
        system_sensors = list(system.current_security_manager.sensors.keys())

        for sensor_obj in system_sensors:
            system.current_security_manager.disarm(sensor_obj)
        self.refresh_sensor_states()
        self.log("All sensors DISARMED")

    def default_all(self):
        system_sensors = list(system.current_security_manager.sensors.keys())

        for sensor_obj in system_sensors:
            system.current_security_manager.set_arm(sensor_obj, None)

        self.refresh_sensor_states()
        self.log("All sensors DEFAULTED")

    # --- Log ---
    def log(self, message: str) -> None:
        self.message_label.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x400")
    page = SecurityModePage(root, root)
    page.pack()
    root.mainloop()
