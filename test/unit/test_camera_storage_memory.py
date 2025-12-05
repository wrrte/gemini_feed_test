import pytest

from core.surveillance.camera_exceptions import (
    CameraAlreadyExistsError,
    CameraNotFoundError,
)
from core.surveillance.safehome_camera import SafeHomeCamera
from device.device_camera import DeviceCamera
from storage.camera_storage_memory import CameraMemoryDB


@pytest.fixture
def camera_factory():
    created = []

    def _make(camera_id=1, location=(0, 0), has_password=False, password="", enabled=False):
        camera = SafeHomeCamera(
            camera_id=camera_id,
            location=location,
            hardware_camera=DeviceCamera(),
            has_password=has_password,
            password=password,
            enabled=enabled,
        )
        created.append(camera)
        return camera

    yield _make

    for camera in created:
        camera.hardware_camera.stop()


def test_initial_cameras_loaded(camera_factory):
    camera_one = camera_factory(1, (10, 20))
    camera_two = camera_factory(2, (30, 40))

    db = CameraMemoryDB()
    db.create_camera(camera_one)
    db.create_camera(camera_two)

    assert db.get_all_cameras() == [camera_one, camera_two]
    assert db.get_camera_by_id(2) is camera_two


def test_create_camera_rejects_duplicate_ids(camera_factory):
    db = CameraMemoryDB()

    db.create_camera(camera_factory(1, (5, 5)))

    with pytest.raises(CameraAlreadyExistsError):
        db.create_camera(camera_factory(1, (15, 25)))


def test_update_camera_overwrites_existing(camera_factory):
    db = CameraMemoryDB()
    original = camera_factory(1, (1, 1))
    db.create_camera(original)

    updated = camera_factory(
        1, (50, 75), has_password=True, password="secret", enabled=True)
    db.update_camera(updated)

    stored = db.get_camera_by_id(1)
    assert stored is updated
    assert stored.location == (50, 75)
    assert stored.has_password is True
    assert stored.password == "secret"
    assert stored.enabled is True


def test_delete_camera_and_missing_error(camera_factory):
    db = CameraMemoryDB()
    camera = camera_factory(2, (3, 4))
    db.create_camera(camera)

    db.delete_camera(2)
    assert db.get_camera_by_id(2) is None

    with pytest.raises(CameraNotFoundError):
        db.delete_camera(2)


def test_get_camera_by_id_returns_none_when_missing():
    db = CameraMemoryDB()

    assert db.get_camera_by_id(99) is None
    assert db.get_all_cameras() == []
