import tkinter as tk
from typing import Any
from PIL import Image, ImageTk
from core.system import system

THUMB_WIDTH = 200
THUMB_HEIGHT = 200


class ThumbnailsPage(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: Any) -> None:
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # --- Main container ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        tk.Label(
            main_frame,
            text="SURVEILLANCE THUMBNAIL VIEW",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # A frame that holds all thumbnails
        self.thumb_frame = tk.Frame(main_frame)
        self.thumb_frame.pack(expand=True, fill="both")

        self.thumb_frame.grid_columnconfigure(0, weight=1)
        self.thumb_frame.grid_columnconfigure(1, weight=1)
        self.thumb_frame.grid_columnconfigure(2, weight=1)

        self.thumbnail_widgets = {}
        self.load_thumbnails()

    def load_thumbnails(self) -> None:
        # Clear old thumbnails
        for widget in self.thumb_frame.winfo_children():
            widget.destroy()

        # Get thumbnails directly - controller handles all logic
        thumbnails: dict[int, Image.Image] = system.current_camera_controller.get_thumbnail_views()

        # Make Tkinter-safe images stored to avoid garbage collection
        self.tk_thumbnails = {}

        row = 0
        col = 0

        for cam_id, pil_img in thumbnails.items():
            frame = tk.Frame(self.thumb_frame, bd=2, relief="groove", padx=5, pady=5)
            frame.grid(row=row, column=col, padx=10, pady=10)

            # Title
            tk.Label(frame, text=f"Camera {cam_id}", font=("Arial", 12, "bold")).pack()

            # Create a fixed-size canvas
            canvas = tk.Canvas(frame, width=THUMB_WIDTH, height=THUMB_HEIGHT)
            canvas.pack()

            # Resize while maintaining aspect ratio
            pil_img = pil_img.copy()
            pil_img.thumbnail((THUMB_WIDTH, THUMB_HEIGHT))

            tk_img = ImageTk.PhotoImage(pil_img)
            self.tk_thumbnails[cam_id] = tk_img

            # Center the image
            w, h = pil_img.size
            canvas.create_image(
                (THUMB_WIDTH - w) // 2,
                (THUMB_HEIGHT - h) // 2,
                anchor="nw",
                image=tk_img
            )

            # Move to next grid position
            col += 1
            if col == 3:
                row += 1
                col = 0


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x400")
    page = ThumbnailsPage(root, root)
    page.pack()
    root.mainloop()
