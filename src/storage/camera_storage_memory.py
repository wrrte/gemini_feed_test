from core.surveillance.ICameraDB import ICameraDB
from core.surveillance.safehome_camera import SafeHomeCamera
from core.surveillance.camera_exceptions import (
    CameraAlreadyExistsError,
    CameraNotFoundError,
)
from typing import Dict, Optional, List


class CameraMemoryDB(ICameraDB):

    def __init__(self) -> None:
        self._cameras: Dict[int, SafeHomeCamera] = {}

    def create_camera(self, camera: SafeHomeCamera) -> None:
        if camera.camera_id in self._cameras:
            raise CameraAlreadyExistsError(
                f"Camera with id {camera.camera_id} already exists in DB."
            )
        self._cameras[camera.camera_id] = camera

    def update_camera(self, camera: SafeHomeCamera) -> None:
        self._cameras[camera.camera_id] = camera

    def delete_camera(self, camera_id: int) -> None:
        if camera_id not in self._cameras:
            raise CameraNotFoundError(
                f"No camera with id {camera_id} exists in DB."
            )
        del self._cameras[camera_id]

    def get_camera_by_id(self, camera_id: int) -> Optional[SafeHomeCamera]:
        return self._cameras.get(camera_id)

    def get_all_cameras(self) -> List[SafeHomeCamera]:
        return list(self._cameras.values())
