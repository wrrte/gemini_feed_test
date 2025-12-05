from abc import ABC, abstractmethod
from typing import List, Optional

from .safehome_camera import SafeHomeCamera


class ICameraDB(ABC):

    """A safehome_camera stores the following:

        camera_id: int
        location: Tuple[int, int]
        hardware_camera:  DeviceCamera

        pan_angle: int = field(default=0, init=False)
        zoom_level: int = field(default=2, init=False)

        has_password: bool
        password: Optional[str] = None (Instead of none it can simply be "")
        enabled: bool = False

       The Database should have the fields:
       camera_id, location, pan_angle, zoom_level, password, enabled
       When getting stored the input SafeHomeCamera is broken down into these
       When updating the camera is searched using camera_id as key
       When getting the camera is searched using camera_id as key
         and a newly constructed SafeHomeCamera is returned,
         with a new instance of DeviceCamera()
    """

    @abstractmethod
    def create_camera(self, camera: SafeHomeCamera) -> None:
        """Persist a newly created camera."""

    @abstractmethod
    def update_camera(self, camera: SafeHomeCamera) -> None:
        """Persist changes to an existing camera."""

    @abstractmethod
    def delete_camera(self, camera_id: int) -> None:
        """Delete persisted camera information."""

    @abstractmethod
    def get_camera_by_id(self, camera_id: int) -> Optional[SafeHomeCamera]:
        """Return a camera by id, or None if not found."""

    @abstractmethod
    def get_all_cameras(self) -> List[SafeHomeCamera]:
        """Return all persisted cameras."""
