import tkinter as tk
from typing import Any
from PIL import Image, ImageTk
import os
from core.security.security_zone_geometry.area import Square
from core.system import system


class SecurityZonePage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        super().__init__(parent)
        self.controller = controller

        # Layout
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Canvas
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            canvas_frame,
            text="SECURITY ZONES",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "../img/img_floorplan.png")
        fp_img = Image.open(image_path).resize((500, 300))
        self.floorplan_tk = ImageTk.PhotoImage(fp_img)

        self.canvas = tk.Canvas(canvas_frame, width=500, height=300)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.create_image(0, 0, anchor="nw", image=self.floorplan_tk)

        system.current_security_manager.sensors.keys()

        # Sensors
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

        # Security zones
        self.security_zones = {
            "Zone A": {"top_left": (100, 50), "bottom_right": (200, 120), "enabled": True},
            "Zone B": {"top_left": (250, 30), "bottom_right": (380, 140), "enabled": False},
            "Zone C": {"top_left": (50, 170), "bottom_right": (180, 260), "enabled": True},
        }

        self.zone_icons = {}
        self.create_zone_icons()

        # Sidebar
        sidebar = tk.Frame(main_frame, width=200, bd=2, relief="groove")
        sidebar.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(sidebar, text="SECURITY ZONES", font=("Arial", 12, "bold")).pack(pady=(0, 5))

        # Selected zone
        self.selected_zone = None

        # Zone dragging / resizing state
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
        self.drag_offset = (0, 0)
        self.zone_handles = {}  # rect -> handle ids

        # Zone name
        self.id_label = tk.Label(sidebar, text="Zone: ---", anchor="w")
        self.id_label.pack(fill="x")

        # NEW: State Toggle Button (replaces STATE label)
        self.state_button = tk.Button(sidebar, text="---", state="disabled", command=self.toggle_zone)
        self.state_button.pack(fill="x", pady=5)

        # Zone actions
        tk.Button(sidebar, text="Add Security Zone", command=self.add_zone).pack(fill="x", pady=3)
        tk.Button(sidebar, text="Delete Security Zone", command=self.delete_zone).pack(fill="x", pady=3)

        # Log
        self.message_label = tk.Label(sidebar, text="", fg="blue", anchor="w")
        self.message_label.pack(side="bottom", fill="x", pady=(10, 0))

        self.refresh_security_zones()

    def refresh_security_zones(self):
        """
        Sync self.security_zones with system.current_security_manager.security_zones.
        Rebuilds the dict to match backend objects.
        """
        backend_zones = system.current_security_manager.security_zones  # list[SecurityZone]

        new_dict = {}

        for zone in backend_zones:
            # Name based on ID
            name = f"Zone {zone.id}"

            # Extract square coordinates
            x1, y1 = zone.area.up_left  # (left, up)
            x2, y2 = zone.area.down_right  # (right, down)

            new_dict[name] = {
                "top_left": (x1, y1),
                "bottom_right": (x2, y2),
                "enabled": zone.enabled
            }

        # Replace local dict
        self.security_zones = new_dict

        # Redraw everything visually
        self.redraw_zones()
        self.refresh_sensor_states()

        # Clear selection (optional)
        self.selected_zone = None
        self.id_label.config(text="Zone: ---")
        self.state_button.config(text="---", state="disabled")

    def push_zone_to_backend(self, zone_name):
        """Push updated coordinates into SecurityManager using update_security_zone()."""
        zone_id = int(zone_name.split(" ")[1])  # "Zone 3" -> 3

        z = self.security_zones[zone_name]
        x1, y1 = z["top_left"]
        x2, y2 = z["bottom_right"]

        area = Square(y1, y2, x1, x2)  # Square(up, down, left, right)

        system.current_security_manager.update_security_zone(zone_id, area)
        self.refresh_sensor_states()

    def refresh_sensor_states(self):
        """Synchronize GUI sensor enabled states with system sensors."""
        system.current_security_manager.update()
        system_sensors = list(system.current_security_manager.sensors.keys())

        # Loop through GUI sensors in index order
        for i, (name, gui_sensor) in enumerate(self.sensors.items()):
            if i >= len(system_sensors):
                break  # Safety: avoid out-of-range

            sensor_obj = system_sensors[i]

            # Update armed state
            gui_sensor["enabled"] = sensor_obj.armed

            # Update color on canvas
            icon = [icon for icon, n in self.sensor_icons.items() if n == name][0]
            color = "green" if sensor_obj.armed else "red"
            self.canvas.itemconfig(icon, fill=color)

    def create_sensor_icons(self) -> None:
        for name, info in self.sensors.items():
            x, y = info["pos"]
            r = 8
            icon = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="green" if info["enabled"] else "red",
                outline="black", width=2
            )
            self.sensor_icons[icon] = name
            self.canvas.tag_bind(icon, "<Button-1>", self.sensor_clicked)

    def create_zone_icons(self) -> None:
        for name, z in self.security_zones.items():
            x1, y1 = z["top_left"]
            x2, y2 = z["bottom_right"]

            color = "blue" if z["enabled"] else "gray"

            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=color, width=3, fill=color, stipple="gray12"
            )

            self.zone_icons[rect] = name

            # Bind rectangle click + drag
            self.canvas.tag_bind(rect, "<Button-1>", self.zone_clicked)
            self.canvas.tag_bind(rect, "<B1-Motion>", self.zone_dragging)
            self.canvas.tag_bind(rect, "<ButtonRelease-1>", self.stop_drag)

    def show_resize_handles(self, rect: int) -> None:
        zone_name = self.selected_zone
        x1, y1, x2, y2 = self.canvas.coords(rect)

        # If handles already exist, just update positions and lift
        if zone_name in self.zone_handles:
            handles = self.zone_handles[zone_name]
            positions = {"tl": (x1, y1), "tr": (x2, y1), "bl": (x1, y2), "br": (x2, y2)}
            for key, (hx, hy) in positions.items():
                self.canvas.coords(handles[key], hx - 6, hy - 6, hx + 6, hy + 6)
                self.canvas.tag_raise(handles[key])  # <-- lift handle above everything
            return

        # Otherwise, create handles
        handle_size = 6
        handles = {}
        corners = {"tl": (x1, y1), "tr": (x2, y1), "bl": (x1, y2), "br": (x2, y2)}
        for key, (hx, hy) in corners.items():
            h = self.canvas.create_rectangle(
                hx - handle_size, hy - handle_size, hx + handle_size, hy + handle_size,
                fill="white", outline="black"
            )
            handles[key] = h

            self.canvas.tag_bind(h, "<Button-1>", self.start_resize)
            self.canvas.tag_bind(h, "<B1-Motion>", self.resize_drag)
            self.canvas.tag_bind(h, "<ButtonRelease-1>", self.stop_resize)

            self.canvas.tag_raise(h)  # <-- lift handle above everything

        self.zone_handles[zone_name] = handles

    def hide_resize_handles(self) -> None:
        for handles in self.zone_handles.values():
            for h in handles.values():
                self.canvas.delete(h)
        self.zone_handles.clear()

    def sensor_clicked(self, event: tk.Event) -> None:
        sensor = self.sensor_icons[self.canvas.find_withtag("current")[0]]
        self.log(f"Sensor clicked: {sensor}")

    def zone_clicked(self, event: tk.Event) -> None:
        icon = self.canvas.find_withtag("current")[0]
        zone = self.zone_icons[icon]
        self.selected_zone = zone
        info = self.security_zones[zone]

        self.id_label.config(text=f"Zone: {zone}")
        self.state_button.config(text="DISARM" if info["enabled"] else "ARM",
                                 state="normal")

        # Show resize handles
        self.show_resize_handles(icon)

        self.log(f"Selected {zone}")

    def zone_dragging(self, event: tk.Event) -> None:
        if self.resizing:
            return

        rect = [r for r, name in self.zone_icons.items() if name == self.selected_zone][0]

        if not self.dragging:
            x1, y1, x2, y2 = self.canvas.coords(rect)
            self.drag_offset = (event.x - x1, event.y - y1)
            self.dragging = True

        dx = event.x - self.drag_offset[0]
        dy = event.y - self.drag_offset[1]

        # Get rectangle size
        x1, y1, x2, y2 = self.canvas.coords(rect)
        width = x2 - x1
        height = y2 - y1

        # Canvas size
        canvas_width = int(self.canvas["width"])
        canvas_height = int(self.canvas["height"])

        # Constrain dx/dy so rectangle stays inside canvas
        dx = max(0, min(dx, canvas_width - width))
        dy = max(0, min(dy, canvas_height - height))

        # Move rectangle
        x2 = dx + width
        y2 = dy + height
        self.canvas.coords(rect, dx, dy, x2, y2)

        # Update zone data
        self.security_zones[self.selected_zone]["top_left"] = (dx, dy)
        self.security_zones[self.selected_zone]["bottom_right"] = (x2, y2)

        # Move handles
        self.show_resize_handles(rect)

    def stop_drag(self, event: tk.Event) -> None:
        self.dragging = False
        if self.selected_zone:
            self.push_zone_to_backend(self.selected_zone)

    def start_resize(self, event: tk.Event) -> None:
        self.resizing = True
        handle = self.canvas.find_withtag("current")[0]
        self.resize_handle = handle

    def resize_drag(self, event: tk.Event) -> None:
        if not self.resizing:
            return

        zone_name = self.selected_zone
        rect = [r for r, n in self.zone_icons.items() if n == zone_name][0]
        x1, y1, x2, y2 = self.canvas.coords(rect)

        handle_key = None
        for key, hid in self.zone_handles[zone_name].items():
            if hid == self.resize_handle:
                handle_key = key

        canvas_width = int(self.canvas["width"])
        canvas_height = int(self.canvas["height"])

        if handle_key == "tl":
            x1 = min(event.x, x2 - 10)  # min width 10
            y1 = min(event.y, y2 - 10)
            # clamp to canvas
            x1 = max(0, x1)
            y1 = max(0, y1)
        elif handle_key == "tr":
            x2 = max(event.x, x1 + 10)
            y1 = min(event.y, y2 - 10)
            # clamp to canvas
            x2 = min(canvas_width, x2)
            y1 = max(0, y1)
        elif handle_key == "bl":
            x1 = min(event.x, x2 - 10)
            y2 = max(event.y, y1 + 10)
            # clamp to canvas
            x1 = max(0, x1)
            y2 = min(canvas_height, y2)
        elif handle_key == "br":
            x2 = max(event.x, x1 + 10)
            y2 = max(event.y, y1 + 10)
            # clamp to canvas
            x2 = min(canvas_width, x2)
            y2 = min(canvas_height, y2)

        self.canvas.coords(rect, x1, y1, x2, y2)
        self.security_zones[zone_name]["top_left"] = (x1, y1)
        self.security_zones[zone_name]["bottom_right"] = (x2, y2)

        # Move handles without deleting
        self.show_resize_handles(rect)

    def stop_resize(self, event: tk.Event) -> None:
        self.resizing = False
        self.resize_handle = None
        if self.selected_zone:
            self.push_zone_to_backend(self.selected_zone)

    # Add zone
    def add_zone(self) -> None:
        zone = system.current_security_manager.add_security_zone()
        self.refresh_security_zones()
        self.log(f"Added Zone {zone.id}")

    # Delete zone
    def delete_zone(self) -> None:
        if not self.selected_zone:
            self.log("No zone selected.")
            return

        zone_name = self.selected_zone
        zone_id = int(zone_name.split(" ")[1])  # "Zone 3" → 3

        # ---- 1. DELETE FROM BACKEND ----
        try:
            system.current_security_manager.remove_security_zone(zone_id)
        except Exception as e:
            self.log(f"Error: {e}")
            return

        # ---- 2. DELETE RESIZE HANDLES ----
        if zone_name in self.zone_handles:
            for h in self.zone_handles[zone_name].values():
                self.canvas.delete(h)
            del self.zone_handles[zone_name]

        # ---- 3. DELETE THE RECTANGLE ----
        rect_to_delete = [r for r, n in self.zone_icons.items() if n == zone_name]
        if rect_to_delete:
            self.canvas.delete(rect_to_delete[0])
            del self.zone_icons[rect_to_delete[0]]

        # ---- 4. CLEAR SELECTION / SIDEBAR ----
        self.selected_zone = None
        self.id_label.config(text="Zone: ---")
        self.state_button.config(text="---", state="disabled")

        # ---- 5. REFRESH FROM BACKEND (rebuilds self.security_zones properly) ----
        self.refresh_security_zones()

        self.log(f"Deleted {zone_name}")

    # NEW: Toggle enabled/disabled zone
    def toggle_zone(self):
        if not self.selected_zone:
            return

        zone_name = self.selected_zone
        zone_id = int(zone_name.split(" ")[1])

        current_state = self.security_zones[zone_name]["enabled"]
        new_state = not current_state

        if new_state:
            system.current_security_manager.arm_security_zone(zone_id)
        else:
            system.current_security_manager.disarm_security_zone(zone_id)

        # Refresh GUI state
        self.refresh_security_zones()

        self.log(f"{zone_name} {'ENABLED' if new_state else 'DISABLED'}")

    # Redraw all zones
    def redraw_zones(self) -> None:
        for r in list(self.zone_icons.keys()):
            self.canvas.delete(r)
        self.zone_icons.clear()
        self.create_zone_icons()

    # Log
    def log(self, message: str) -> None:
        self.message_label.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x400")
    page = SecurityZonePage(root, root)
    page.pack()
    root.mainloop()
