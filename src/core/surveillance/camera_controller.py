# src/device/camera_controller.py

from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Iterable, Optional, List, Tuple
from storage.camera_storage_memory import CameraMemoryDB
from .safehome_camera import SafeHomeCamera
from .ICameraDB import ICameraDB
from device.device_camera import DeviceCamera
from .camera_exceptions import (
    CameraNotFoundError,
    InvalidLocationError,
)


@dataclass(frozen=True)
class CameraInfo:
    """
    Lightweight, read-only snapshot of a camera's state for use by the GUI.
    Exposes only the data the GUI needs without leaking SafeHomeCamera itself.
    """

    camera_id: int
    location: Tuple[int, int]
    enabled: bool

    has_password: bool


class CameraController:
    """
    Controller class that creates, deletes, and manages a list of
    SafeHomeCamera objects.
    SDS responsibilities (adapted):
    - Add a camera at the specified position
    - Delete a camera with a specific id
    - Enable/disable specific cameras
    - Enable/disable all cameras
    - Zoom/Pan a specific camera
    - Display thumbnail view(s)
    - Display a single view
    """

    def __init__(self, camera_db: Optional[ICameraDB] = None) -> None:
        self._camera_db: ICameraDB = camera_db or CameraMemoryDB()
        # Map from camera_id to SafeHomeCamera
        self._cameras: Dict[int, SafeHomeCamera] = {}
        for cam in self._camera_db.get_all_cameras():
            self._cameras[cam.camera_id] = cam
        self.next_camera_id: int = (
            max(self._cameras.keys(), default=0) + 1
        )
        self.total_camera_number: int = len(self._cameras)

    def _validate_location(self, location: tuple[int, int]) -> None:
        # Helper to check validity of location
        x, y = location
        if x < 0 or y < 0:
            raise InvalidLocationError(
                f"Location coordinates must be non-negative, got {location}."
            )

    def add_camera(
            self,
            camera_id: int,
            location: Tuple[int, int],
            password: str = "",
    ) -> None:

        # Creates SafeHomeCamera home camera instance
        # Ands adds it to database
        if camera_id in self._cameras:
            raise ValueError(f"Camera with id '{camera_id}' already exists")

        self._validate_location(location)

        device_camera = DeviceCamera()
        device_camera.set_id(camera_id)
        has_pass = (password != "")

        camera = SafeHomeCamera(
            camera_id=camera_id,
            location=location,
            hardware_camera=device_camera,
            enabled=True,
            password=password,
            has_password=has_pass,
        )

        self._cameras[camera_id] = camera
        self._camera_db.create_camera(camera)

        self.total_camera_number += 1

        if camera_id >= self.next_camera_id:
            self.next_camera_id = camera_id + 1

    def delete_camera(self, camera_id: int) -> bool:
        # Deletes camera from controller and Database
        camera = self._cameras.pop(camera_id, None)
        if camera is None:
            raise CameraNotFoundError(
                f"No camera with id {camera_id} exists."
            )

        self._camera_db.delete_camera(camera_id)
        self.total_camera_number -= 1
        return True

    def _require_camera(self, camera_id: int) -> SafeHomeCamera:
        # Helper to return SafeHomeCamera Object
        camera = self._cameras.get(camera_id)
        if camera is None:
            raise CameraNotFoundError(
                f"No camera with id {camera_id} exists."
            )
        return camera

    def get_camera_info(self, camera_id: int) -> CameraInfo:
        # Return a CameraInfo tuple to the caller with the specific camera info
        camera = self._require_camera(camera_id)
        return CameraInfo(
            camera_id=camera.camera_id,
            location=camera.get_location(),
            enabled=camera.enabled,
            has_password=camera.has_password
        )

    def get_all_cameras_info(self) -> List[CameraInfo]:
        # Return a list of all camera info to the user
        return [self.get_camera_info(cam_id) for cam_id in self._cameras.keys()]

    def enable_camera(self, camera_id: int) -> None:
        # Enable specific camera
        camera = self._require_camera(camera_id)
        camera.enable()
        self._camera_db.update_camera(camera)

    def disable_camera(self, camera_id: int) -> None:
        # Disable specific camera
        camera = self._require_camera(camera_id)
        camera.disable()
        self._camera_db.update_camera(camera)

    def enable_cameras(self, camera_ids: Iterable[int]) -> None:
        # Enable a list of specific cameras.
        for cid in camera_ids:
            self.enable_camera(cid)

    def disable_cameras(self, camera_ids: Iterable[int]) -> None:
        # Disable a list of specific cameras.
        for cid in camera_ids:
            self.disable_camera(cid)

    def enable_all(self) -> None:
        # Enable all cameras.
        for camera in self._cameras.values():
            camera.enable()
            self._camera_db.update_camera(camera)

    def disable_all(self) -> None:
        # Disable all cameras.
        for camera in self._cameras.values():
            camera.disable()
            self._camera_db.update_camera(camera)

    def zoom_in(self, camera_id: int) -> bool:
        # Attempt to zoom in in the hardware camera
        # Return True if successful and False otherwise
        camera = self._require_camera(camera_id)
        result = camera.zoom_in()
        self._camera_db.update_camera(camera)
        return result

    def zoom_out(self, camera_id: int) -> bool:
        # Attempt to pan zoom out the hardware camera
        # Return True if successful and False otherwise
        camera = self._require_camera(camera_id)
        result = camera.zoom_out()
        self._camera_db.update_camera(camera)
        return result

    def pan_left(self, camera_id: int) -> bool:
        # Attempt to pan left in the hardware camera
        # Return True if successful and False otherwise
        camera = self._require_camera(camera_id)
        result = camera.pan_left()
        self._camera_db.update_camera(camera)
        return result

    def pan_right(self, camera_id: int) -> bool:
        # Attempt to pan right in the hardware camera
        # Return True if successful and False otherwise
        camera = self._require_camera(camera_id)
        result = camera.pan_right()
        self._camera_db.update_camera(camera)
        return result

    def get_single_view(self, camera_id: int) -> Image.Image:
        # Display a single view (or return data for UI to display)
        # for a specific camera.
        camera = self._require_camera(camera_id)
        return camera.display_view()

    def get_thumbnail_views(self) -> Dict[int, Image.Image]:
        # Return thumbnail views for all cameras
        # If camera is protected by password displays "Locked" image
        locked = Image.new("RGB", (160, 160), "black")
        draw = ImageDraw.Draw(locked)
        text = "Locked"
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (160 - text_width) / 2
        y = (160 - text_height) / 2

        draw.text((x, y), text, font=font, fill="white")

        disabled = Image.new("RGB", (160, 160), "black")
        draw = ImageDraw.Draw(disabled)
        text = "Disabled"
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (160 - text_width) / 2
        y = (160 - text_height) / 2

        draw.text((x, y), text, font=font, fill="white")

        result: Dict[int, Image.Image] = {}
        for cid, camera in self._cameras.items():
            if camera.has_password:
                result[cid] = locked
            elif not camera.enabled:
                result[cid] = disabled
            else:
                result[cid] = camera.display_thumbnail()
        return result

    def set_camera_password(self, camera_id: int,
                            password: str) -> None:
        # Sets password to the camera with the ID
        camera = self._require_camera(camera_id)
        camera.set_password(password)
        self._camera_db.update_camera(camera)

    def validate_camera_password(self, camera_id: int, password: str) -> bool:
        # Checks if input matches camera password
        # Can be used to check if camera has password by inputting ""
        camera = self._require_camera(camera_id)
        stored = camera.get_password()

        return password == stored

    def delete_camera_password(self, camera_id: int) -> bool:
        # Deletes camera's password
        # Returns True if password existed and False otherwise
        camera = self._require_camera(camera_id)
        had_password = camera.has_password
        camera.set_password("")
        self._camera_db.update_camera(camera)
        return had_password

    def __del__(self):
        for _, camera in self._cameras.items():
            camera.stop()
