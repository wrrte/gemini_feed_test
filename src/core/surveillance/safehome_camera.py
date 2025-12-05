# src/device/safehome_camera.py
#
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from .camera_exceptions import (
    InvalidLocationError,
    CameraDisabledError
)
from PIL import Image

from device.device_camera import DeviceCamera


@dataclass
class SafeHomeCamera:
    """
    Manage state information of a given camera and control the operation
    of that camera.

    SDS responsibilities (adapted):
    - Manage camera state information (id, location, pan angle, zoom degree,
      password, working state)
    - Display a view (single / thumbnail)
    - Zoom in / zoom out
    - Pan left / pan right
    - Get/Set password
    - Enable/Disable the camera (working state)
    """

    camera_id: int
    location: Tuple[int, int]
    hardware_camera: DeviceCamera

    pan_angle: int = field(default=0, init=False)
    zoom_level: int = field(default=2, init=False)

    has_password: bool
    password: str = ""
    enabled: bool = False

    def __post_init__(self) -> None:
        # Set data for internal camera
        self.set_id(self.camera_id)
        self.set_location(self.location)

    def get_location(self) -> Tuple[int, int]:
        # Return location on the floorplan
        return self.location

    def set_location(self, in_location: Tuple[int, int]) -> None:
        # Set location on the floorplan
        x, y = in_location
        if x < 0 or y < 0:
            raise InvalidLocationError(
                f"Location co-ordinates must be non negative, got: {
                    in_location}"
            )
        self.location = in_location

    def get_id(self) -> int:
        # Returns ID of the camera
        return self.camera_id

    def set_id(self, in_id: int) -> None:
        # Sets ID of the camera
        if in_id <= 0:
            raise ValueError("camera_id must be a positive integer.")
        self.camera_id = in_id
        self.hardware_camera.set_id(in_id)

    def enable(self) -> None:
        # Enable this camera
        self.enabled = True

    def disable(self) -> None:
        # Disable this camera
        self.enabled = False

    def display_view(self) -> Image.Image:
        # Display a still image from this camera.
        if not self.enabled:
            raise CameraDisabledError(
                f"Camera {self.camera_id} is disabled and cannot provide a view."
            )
        image = self.hardware_camera.get_view()
        return image

    def display_thumbnail(self) -> Image.Image:
        return self.display_view().resize((160, 160))

    def zoom_in(self) -> bool:
        # Attempt to zoom in in the hardware camera
        # Return True if successful and False otherwise
        if not self.enabled:
            raise CameraDisabledError(
                f"Camera {self.camera_id} is disabled and cannot be controlled."
            )
        changed = self.hardware_camera.zoom_in()
        if changed is True:
            self.zoom_level += 1
            return True
        return False

    def zoom_out(self) -> bool:
        # Attempt to pan zoom out the hardware camera
        # Return True if successful and False otherwise
        if not self.enabled:
            raise CameraDisabledError(
                f"Camera {self.camera_id} is disabled and cannot be controlled."
            )
        changed = self.hardware_camera.zoom_out()
        if changed is True:
            self.zoom_level -= 1
            return True
        return False

    def pan_right(self) -> bool:
        # Attempt to pan right in the hardware camera
        # Return True if successful and False otherwise
        if not self.enabled:
            raise CameraDisabledError(
                f"Camera {self.camera_id} is disabled and cannot be controlled."
            )
        changed = self.hardware_camera.pan_right()
        if changed is True:
            self.pan_angle += 1
            return True
        return False

    def pan_left(self) -> bool:
        # Attempt to pan left in the hardware camera
        # Return True if successful and False otherwise
        if not self.enabled:
            raise CameraDisabledError(
                f"Camera {self.camera_id} is disabled and cannot be controlled."
            )
        changed = self.hardware_camera.pan_left()
        if changed is True:
            self.pan_angle -= 1
            return True
        return False

    def set_password(self, password: str) -> None:
        # Set or clear password for this camera (used by the UI / controller).
        self.password = password
        self.has_password = (password != "")

    def get_password(self) -> str:
        # Return current password for this camera (if any).
        return self.password

    def stop(self) -> None:
        # Stops current camera's threading
        self.hardware_camera.stop()
