import tkinter as tk
from typing import Any
from PIL import Image, ImageTk
import os

from core.system import system


class FloorPlanPage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # --- Main container ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # --- Canvas left ---
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            canvas_frame,
            text="SURVEILLANCE FLOOR PLAN VIEW",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "../img/img_floorplan.png")
        floorplan_img = Image.open(image_path)
        floorplan_img = floorplan_img.resize((500, 300))
        self.floorplan_tk = ImageTk.PhotoImage(floorplan_img)

        self.canvas = tk.Canvas(canvas_frame, width=500, height=300)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.create_image(0, 0, anchor="nw", image=self.floorplan_tk)

        # Track temporary unlocks (password entered for this session)
        self.temp_unlocks = set()

        # Camera icons: {canvas_item_id: camera_id}
        self.camera_icons = {}
        self.create_camera_icons()

        # --- Sidebar right ---
        sidebar = tk.Frame(main_frame, width=200, bd=2, relief="groove")
        sidebar.pack(side="right", fill="y", padx=10, pady=10)

        # CAMERA STATUS
        tk.Label(sidebar, text="CAMERA STATUS", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        self.selected_camera_id = None
        self.id_label = tk.Label(sidebar, text="ID: ---", anchor="w")
        self.id_label.pack(fill="x")
        self.lock_label = tk.Label(sidebar, text="LOCK: ---", anchor="w")
        self.lock_label.pack(fill="x")

        # --- View button above ENABLED/DISABLED ---
        self.view_button = tk.Button(sidebar, text="View", command=self.view)
        self.view_button.pack(fill="x", pady=5)

        # RUNNING toggle button
        self.running_button = tk.Button(sidebar, text="---", command=self.toggle_running)
        self.running_button.pack(fill="x", pady=5)

        # PASSWORD section frame
        self.password_frame = tk.Frame(sidebar)
        self.password_frame.pack(fill="x", pady=5)

        # --- Message/Log label at bottom ---
        self.message_label = tk.Label(sidebar, text="", fg="blue", anchor="w", justify="left")
        self.message_label.pack(side="bottom", fill="x", pady=(10, 0))

    def validate_pw_length(self, new_value: str) -> bool:
        return len(new_value) <= 4

    def create_camera_icons(self) -> None:
        """Create initial camera icons based on camera states from CameraController."""
        all_cameras = system.current_camera_controller.get_all_cameras_info()

        for cam_info in all_cameras:
            x, y = cam_info.location
            r = 10

            is_locked = cam_info.has_password

            # Square for locked, circle for unlocked
            if is_locked:
                icon = self.canvas.create_rectangle(
                    x - r, y - r, x + r, y + r,
                    fill="green" if cam_info.enabled else "red",
                    outline="black",
                    width=2
                )
            else:
                icon = self.canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    fill="green" if cam_info.enabled else "red",
                    outline="black",
                    width=2
                )

            self.camera_icons[icon] = cam_info.camera_id
            self.canvas.tag_bind(icon, "<Button-1>", self.camera_clicked)

    def camera_clicked(self, event: tk.Event) -> None:
        clicked_items = self.canvas.find_withtag("current")
        if clicked_items:
            cam_id = self.camera_icons[clicked_items[0]]
            self.selected_camera_id = cam_id

            # Remove from temp unlocks when re-selecting
            if cam_id in self.temp_unlocks:
                self.temp_unlocks.remove(cam_id)

            # Update sidebar
            cam_info = system.current_camera_controller.get_camera_info(cam_id)
            self.id_label.config(text=f"ID: Camera {cam_id}")
            self.lock_label.config(text=f"LOCK: {'ON' if cam_info.has_password else 'OFF'}")

            self.update_sidebar()
            self.update_camera_colors()
            self.log(f"Selected Camera {cam_id}")

    def is_locked(self, camera_id: int) -> bool:
        """Check if camera is locked (has password and not temporarily unlocked)."""
        if camera_id in self.temp_unlocks:
            return False
        cam_info = system.current_camera_controller.get_camera_info(camera_id)
        return cam_info.has_password

    def update_camera_colors(self) -> None:
        """Update camera icons based on running/lock status."""
        # Get fresh camera data
        all_cameras = system.current_camera_controller.get_all_cameras_info()
        camera_data = {cam.camera_id: cam for cam in all_cameras}

        # Store old icon mapping
        old_icons = self.camera_icons.copy()
        self.camera_icons.clear()

        for icon, cam_id in old_icons.items():
            cam_info = camera_data.get(cam_id)
            if not cam_info:
                self.canvas.delete(icon)
                continue

            x, y = cam_info.location
            r = 10
            color = "green" if cam_info.enabled else "red"

            # Determine if should be locked (square) or unlocked (circle)
            should_be_square = cam_info.has_password

            # Check current shape
            current_coords = self.canvas.coords(icon)
            if not current_coords:
                continue

            # Determine if currently a rectangle
            # Rectangle has 4 coords (x1,y1,x2,y2), oval also has 4
            # But we can check the canvas item type
            current_type = self.canvas.type(icon)
            is_currently_rect = (current_type == "rectangle")

            # If shape needs to change, delete and recreate
            if should_be_square != is_currently_rect:
                self.canvas.delete(icon)
                if should_be_square:
                    new_icon = self.canvas.create_rectangle(
                        x - r, y - r, x + r, y + r,
                        fill=color, outline="black", width=2
                    )
                else:
                    new_icon = self.canvas.create_oval(
                        x - r, y - r, x + r, y + r,
                        fill=color, outline="black", width=2
                    )
                self.camera_icons[new_icon] = cam_id
                self.canvas.tag_bind(new_icon, "<Button-1>", self.camera_clicked)
            else:
                # Just update color
                self.canvas.itemconfig(icon, fill=color)
                self.camera_icons[icon] = cam_id

    def update_sidebar(self) -> None:
        """Update sidebar based on selected camera."""
        if self.selected_camera_id is None:
            return

        cam_info = system.current_camera_controller.get_camera_info(self.selected_camera_id)

        # RUNNING button
        state_text = "ENABLED" if cam_info.enabled else "DISABLED"
        self.running_button.config(text=state_text)

        # Disable controls if locked
        if self.is_locked(self.selected_camera_id):
            self.running_button.config(state="disabled")
            self.view_button.config(state="disabled")
        else:
            self.running_button.config(state="normal")
            if cam_info.enabled:
                self.view_button.config(state="normal")
            else:
                self.view_button.config(state="disabled")

        # PASSWORD section
        for widget in self.password_frame.winfo_children():
            widget.destroy()

        vcmd = (self.register(self.validate_pw_length), "%P")

        if self.is_locked(self.selected_camera_id):
            # Camera is locked - show password entry
            tk.Label(self.password_frame, text="Enter Password:").pack(fill="x")
            self.password_entry = tk.Entry(
                self.password_frame,
                show="*",
                validate="key",
                validatecommand=vcmd
            )
            self.password_entry.pack(fill="x")
            tk.Button(self.password_frame, text="Submit", command=self.submit_password).pack(fill="x", pady=2)
        else:
            # Camera is unlocked
            if cam_info.has_password:
                # Has password - show remove button
                tk.Button(self.password_frame, text="Remove Password", command=self.remove_password).pack(fill="x")
            else:
                # No password - show set password UI
                tk.Label(self.password_frame, text="Set Password:").pack(fill="x")
                self.new_password_entry = tk.Entry(
                    self.password_frame,
                    show="*",
                    validate="key",
                    validatecommand=vcmd
                )
                self.new_password_entry.pack(fill="x")
                tk.Button(self.password_frame, text="SET", command=self.set_password).pack(fill="x")

    def toggle_running(self) -> None:
        """Toggle camera enabled/disabled state."""
        if self.selected_camera_id is None:
            return

        if self.is_locked(self.selected_camera_id):
            self.log("Camera is locked!")
            return

        cam_info = system.current_camera_controller.get_camera_info(self.selected_camera_id)

        if cam_info.enabled:
            system.current_camera_controller.disable_camera(self.selected_camera_id)
            self.log(f"Camera {self.selected_camera_id} disabled")
        else:
            system.current_camera_controller.enable_camera(self.selected_camera_id)
            self.log(f"Camera {self.selected_camera_id} enabled")

        self.update_sidebar()
        self.update_camera_colors()

    def set_password(self) -> None:
        """Set password for the selected camera."""
        if self.selected_camera_id is None:
            return

        pw = self.new_password_entry.get().strip()
        if not pw:
            self.log("Cannot set empty password!")
            return

        system.current_camera_controller.set_camera_password(self.selected_camera_id, pw)
        self.log(f"Password set for Camera {self.selected_camera_id}")

        self.update_sidebar()
        self.update_camera_colors()

    def remove_password(self) -> None:
        """Remove password from the selected camera."""
        if self.selected_camera_id is None:
            return

        system.current_camera_controller.delete_camera_password(self.selected_camera_id)
        self.log(f"Password removed from Camera {self.selected_camera_id}")

        # Remove from temp unlocks if present
        self.temp_unlocks.discard(self.selected_camera_id)

        self.update_sidebar()
        self.update_camera_colors()

    def submit_password(self) -> None:
        """Validate entered password for locked camera."""
        if self.selected_camera_id is None:
            return

        entered = self.password_entry.get()

        if system.current_camera_controller.validate_camera_password(self.selected_camera_id, entered):
            self.temp_unlocks.add(self.selected_camera_id)
            self.log(f"Camera {self.selected_camera_id} unlocked (temporary)")
        else:
            self.log("Wrong password!")

        self.update_sidebar()
        self.update_camera_colors()

    def view(self) -> None:
        """Open camera view for selected camera."""
        if self.selected_camera_id is None:
            self.log("No camera selected.")
            return

        if self.is_locked(self.selected_camera_id):
            self.log(f"Camera {self.selected_camera_id} is locked; cannot view.")
            return

        # Tell main controller to open CameraViewPage
        self.controller.open_camera_view(self.selected_camera_id)

    def log(self, message: str) -> None:
        """Update the message/log label."""
        self.message_label.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x400")
    page = FloorPlanPage(root, root)
    page.pack()
    root.mainloop()
