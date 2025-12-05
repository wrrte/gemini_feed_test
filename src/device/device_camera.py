import threading
import time
from PIL import Image, ImageDraw, ImageFont
from tkinter import messagebox
from .interface_camera import InterfaceCamera
import os


class DeviceCamera(threading.Thread, InterfaceCamera):
    RETURN_SIZE = 500
    SOURCE_SIZE = 200

    def __init__(self):
        super().__init__(daemon=True)

        self.cameraId = 0
        self.time = 0
        self.pan = 0
        self.zoom = 2
        self.imgSource = None
        self.centerWidth = 0
        self.centerHeight = 0
        self._running = True
        self._lock = threading.Lock()
        # Font was previously missing; using a default PIL font prevents AttributeError in getView
        self.font = ImageFont.load_default()

        self.start()

    def set_id(self, id_):
        """Set the camera ID and load associated image (synchronized)."""
        with self._lock:
            self.cameraId = id_

            fileName = os.path.join(os.path.dirname(os.path.dirname(__file__)), "img", f"camera{id_}.jpg")

            try:
                self.imgSource = Image.open(fileName)
                self.centerWidth = self.imgSource.width // 2
                self.centerHeight = self.imgSource.height // 2
            except FileNotFoundError:
                self.imgSource = None
                try:
                    messagebox.showerror(
                        "File Error", f"{fileName} file open error")
                except:
                    print(f"ERROR: {fileName} file open error")
                return

    def get_id(self):
        """Get the camera ID."""
        return self.cameraId

    def get_view(self):
        """Get the current camera view as a PIL Image (synchronized)."""
        with self._lock:

            view = "Time = "
            if self.time < 10:
                view += "0"
            view += f"{self.time}, zoom x{self.zoom}, "

            if self.pan > 0:
                view += f"right {self.pan}"
            elif self.pan == 0:
                view += "center"
            else:
                view += f"left {-self.pan}"

            # Create the view image (500x500)
            imgView = Image.new(
                'RGB', (self.RETURN_SIZE, self.RETURN_SIZE), 'black')

            if self.imgSource is not None:

                zoomed = self.SOURCE_SIZE * (10 - self.zoom) // 10
                panned = self.pan * self.SOURCE_SIZE // 5

                left = self.centerWidth + panned - zoomed
                top = self.centerHeight - zoomed
                right = self.centerWidth + panned + zoomed
                bottom = self.centerHeight + zoomed

                # Crop and resize to fill the view
                try:
                    cropped = self.imgSource.crop((left, top, right, bottom))
                    resized = cropped.resize(
                        (self.RETURN_SIZE, self.RETURN_SIZE), Image.LANCZOS)
                    imgView.paste(resized, (0, 0))
                except Exception:
                    # If crop fails, keep black background
                    pass

            draw = ImageDraw.Draw(imgView)

            # Get text size
            bbox = draw.textbbox((0, 0), view, font=self.font)
            wText = bbox[2] - bbox[0]
            hText = bbox[3] - bbox[1]

            # Draw rounded rectangle background (gray)
            rX = 0
            rY = 0
            draw.rounded_rectangle(
                [(rX, rY), (rX + wText + 10, rY + hText + 5)],
                radius=hText // 2,
                fill='gray'
            )

            # Draw text (cyan)
            xText = rX + 5
            yText = rY + 2
            draw.text((xText, yText), view, fill='cyan', font=self.font)

            return imgView

    def pan_right(self):
        """Pan camera to the right (synchronized)."""
        with self._lock:
            self.pan += 1
            if self.pan > 5:
                self.pan = 5
                return False
            return True

    def pan_left(self):
        """Pan camera to the left (synchronized)."""
        with self._lock:
            self.pan -= 1
            if self.pan < -5:
                self.pan += 1
                return False
            return True

    def zoom_in(self):
        """Zoom in (synchronized)."""
        with self._lock:
            self.zoom += 1
            if self.zoom > 9:
                self.zoom -= 1
                return False
            return True

    def zoom_out(self):
        """Zoom out (synchronized)."""
        with self._lock:
            self.zoom -= 1
            if self.zoom < 1:
                self.zoom += 1
                return False
            return True

    def _tick(self):
        """Increment time counter (synchronized, private)."""
        with self._lock:
            self.time += 1
            if self.time >= 100:
                self.time = 0

    def run(self):
        """Thread run method - updates time every second."""
        while self._running:
            try:
                time.sleep(1.0)
            except InterruptedError:
                pass
            self._tick()

    def stop(self):
        """Stop the camera thread."""
        self._running = False
