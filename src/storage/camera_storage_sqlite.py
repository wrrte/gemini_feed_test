from typing import Optional, List

from core.surveillance.ICameraDB import ICameraDB

from device.device_camera import DeviceCamera
from core.surveillance.safehome_camera import SafeHomeCamera


class CameraSqliteDB(ICameraDB):
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager

    def create_camera(self, camera: SafeHomeCamera) -> None:
        pass

    def update_camera(self, camera: SafeHomeCamera) -> None:
        """Persist changes to an existing camera."""
        query = """
        UPDATE cameras
        SET 
            location_x = ?,
            location_y = ?,
            pan_angle  = ?,
            zoom_level = ?,
            password   = ?,
            enabled    = ?
        WHERE camera_id = ?
        """
        self.storage_manager.execute(
            query,
            (
                camera.location[0],
                camera.location[1],
                camera.pan_angle,
                camera.zoom_level,
                camera.password,
                camera.enabled,
                camera.camera_id
            )
        )

    def delete_camera(self, camera_id: int) -> None:
        pass

    def get_camera_by_id(self, camera_id: int) -> Optional[SafeHomeCamera]:
        """Return a camera by id, or None if not found."""

        query = """
        SELECT *
        FROM cameras
        WHERE camera_id=?
        """
        rows = self.storage_manager.execute(query, (camera_id,))

        if len(rows) == 0:
            return None

        row = rows[0]

        camera = SafeHomeCamera(
            camera_id=row[0],
            location=(row[1], row[2]),
            hardware_camera=DeviceCamera(),
            has_password=row[5] != "",
            password=row[5],
            enabled=bool(row[6])
        )
        camera.pan_angle = row[3]
        camera.zoom_level = row[4]

        return camera

    def get_all_cameras(self) -> List[SafeHomeCamera]:
        """Return all persisted cameras."""

        query = """
        SELECT *
        FROM cameras
        """
        rows = self.storage_manager.execute(query)

        cameras = []

        for row in rows:
            camera = SafeHomeCamera(
                camera_id=row[0],
                location=(row[1], row[2]),
                hardware_camera=DeviceCamera(),
                has_password=row[5] != "",
                password=row[5],
                enabled=bool(row[6])
            )

            camera.pan_angle = row[3]
            camera.zoom_level = row[4]

            cameras.append(camera)

        return cameras
