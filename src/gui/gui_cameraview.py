import tkinter as tk
from PIL import Image, ImageTk
from core.system import system


class CameraViewPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.camera_id = None
        self._after_id = None
        self.photo = None
        self.canvas_image_id = None

        # ============================================================
        # HEADER
        # ============================================================
        self.header = tk.Label(
            self,
            text="Viewing Camera None",
            font=('Arial', 16, 'bold'),
            bg='lightgray'
        )
        self.header.pack(fill="x", pady=5)

        # ============================================================
        # MAIN FRAME — split left/right
        # ============================================================
        main = tk.Frame(self)
        main.pack(fill="both", expand=True)

        # ---------- LEFT: Camera Canvas ----------
        left = tk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(
            left, width=400, height=300,
            bg="black", highlightthickness=2, highlightbackground="gray"
        )
        self.canvas.pack(expand=True)

        # placeholder black image
        placeholder = Image.new("RGB", (400, 300), "black")
        self.photo = ImageTk.PhotoImage(placeholder, master=self.canvas)
        self.canvas_image_id = self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        # ---------- RIGHT: Controls ----------
        right = tk.Frame(main, bg="lightgray", bd=2, relief="groove")
        right.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(
            right,
            text="Camera Controls",
            font=("Arial", 12, "bold"),
            bg="lightgray"
        ).pack(pady=10)

        # PAN CONTROLS
        pan_label = tk.Label(right, text="Pan", bg="lightgray", font=('Arial', 10, 'bold'))
        pan_label.pack(pady=(10, 5))

        pan_frame = tk.Frame(right, bg="lightgray")
        pan_frame.pack(pady=5)

        tk.Button(
            pan_frame, text="◀◀ Left",
            width=12, bg="lightblue",
            command=lambda: system.current_camera_controller.pan_left(self.camera_id)
        ).pack(side="left", padx=5)

        tk.Button(
            pan_frame, text="Right ▶▶",
            width=12, bg="lightblue",
            command=lambda: system.current_camera_controller.pan_right(self.camera_id)
        ).pack(side="left", padx=5)

        # ZOOM CONTROLS
        zoom_label = tk.Label(right, text="Zoom", bg="lightgray", font=('Arial', 10, 'bold'))
        zoom_label.pack(pady=(20, 5))

        zoom_frame = tk.Frame(right, bg="lightgray")
        zoom_frame.pack(pady=5)

        tk.Button(
            zoom_frame, text="🔍+ Zoom In",
            width=12, bg="lightgreen",
            command=lambda: system.current_camera_controller.zoom_in(self.camera_id)
        ).pack(side="left", padx=5)

        tk.Button(
            zoom_frame, text="🔍- Zoom Out",
            width=12, bg="lightgreen",
            command=lambda: system.current_camera_controller.zoom_out(self.camera_id)
        ).pack(side="left", padx=5)

        tk.Button(
            right, text="← Back to Floorplan",
            bg="lightgray",
            command=self.back_to_floorplan
        ).pack(pady=20, fill="x")

    # ============================================================
    # PUBLIC API: Called from controller
    # ============================================================
    def load_camera(self, cam_id: int):
        self.stop_updates()
        self.camera_id = cam_id

        self.header.config(
            text=f"Viewing Camera {self.camera_id}")

        try:
            img = system.current_camera_controller.get_single_view(cam_id).resize((400, 300))
        except Exception:
            img = Image.new("RGB", (400, 300), "black")

        if img.mode != "RGB":
            img = img.convert("RGB")

        self.photo = ImageTk.PhotoImage(img, master=self.canvas)
        self.canvas.itemconfig(self.canvas_image_id, image=self.photo)
        self.canvas._cached_image = self.photo

        self.start_updates()

    # ============================================================
    # PERIODIC UPDATE LOOP
    # ============================================================
    def start_updates(self):
        if self._after_id is None:
            self._schedule_next()

    def stop_updates(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception as e:
                print("Error cancelling after:", e)
            self._after_id = None

    def _schedule_next(self):
        self._after_id = self.after(100, self._update_view_internal)

    def _update_view_internal(self):
        try:
            img = system.current_camera_controller.get_single_view(self.camera_id).resize((400, 300))
            if img.mode != "RGB":
                img = img.convert("RGB")

            self.photo = ImageTk.PhotoImage(img, master=self.canvas)
            self.canvas.itemconfig(self.canvas_image_id, image=self.photo)
            self.canvas._cached_image = self.photo
        except Exception as e:
            print("Camera update error:", e)

        self._schedule_next()

    def back_to_floorplan(self) -> None:
        """Stop updates and switch back to floor plan."""
        self.stop_updates()
        try:
            from gui.gui_surveillance import FloorPlanPage
            self.controller.show_frame(FloorPlanPage)
        except Exception as e:
            print("Back navigation failed:", e)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x400")
    page = CameraViewPage(root, root)
    page.load_camera(1)
    page.pack()
    root.mainloop()
