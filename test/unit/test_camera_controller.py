# tests/test_camera_controller.py

from __future__ import annotations

from typing import Dict, List, Optional, Iterable

import pytest
from PIL import Image

# Adjust imports to match your layout
from core.surveillance.camera_controller import CameraController
from core.surveillance.safehome_camera import SafeHomeCamera
from device.device_camera import DeviceCamera
from core.surveillance.camera_exceptions import (
    CameraNotFoundError,
    InvalidLocationError,
)


@pytest.fixture(autouse=True)
def patch_device_camera_image(monkeypatch):
    """
    Patch DeviceCamera.Image.open so controller tests don't depend
    on real ../camera{id}.jpg files.
    """
    import device.device_camera as device_camera_module

    def fake_open(path):
        size = device_camera_module.DeviceCamera.SOURCE_SIZE
        return Image.new("RGB", (size, size), "white")

    monkeypatch.setattr(device_camera_module.Image, "open", fake_open)


class InMemoryCameraDB:
    """
    Simple in-memory DB used for controller tests.

    It stores *real* SafeHomeCamera instances (with real DeviceCameras),
    but just keeps them in a dict so we can assert create/update/delete calls.
    """

    def __init__(self, initial: Optional[Iterable[SafeHomeCamera]] = None):
        self._store: Dict[int, SafeHomeCamera] = {}
        if initial:
            for cam in initial:
                self._store[cam.camera_id] = cam

        self.created: List[int] = []
        self.updated: List[int] = []
        self.deleted: List[int] = []

    def create_camera(self, camera: SafeHomeCamera) -> None:
        if camera.camera_id in self._store:
            raise ValueError("duplicate camera_id in DB")
        self._store[camera.camera_id] = camera
        self.created.append(camera.camera_id)

    def update_camera(self, camera: SafeHomeCamera) -> None:
        self._store[camera.camera_id] = camera
        self.updated.append(camera.camera_id)

    def delete_camera(self, camera_id: int) -> None:
        if camera_id not in self._store:
            raise CameraNotFoundError(
                f"No camera with id {camera_id} exists in DB."
            )
        del self._store[camera_id]
        self.deleted.append(camera_id)

    def get_camera_by_id(self, camera_id: int) -> Optional[SafeHomeCamera]:
        return self._store.get(camera_id)

    def get_all_cameras(self) -> List[SafeHomeCamera]:
        return list(self._store.values())


@pytest.fixture
def controller():
    """
    Fresh CameraController + InMemoryCameraDB for each test.
    """
    db = InMemoryCameraDB()
    ctrl = CameraController(camera_db=db)
    return ctrl, db


def make_camera(camera_id: int, location=(0, 0)) -> SafeHomeCamera:
    """
    Helper to construct a SafeHomeCamera with a real DeviceCamera for
    pre-populating the DB.
    """
    hw = DeviceCamera()
    cam = SafeHomeCamera(
        camera_id=camera_id,
        location=location,
        hardware_camera=hw,
        has_password=False,
        password=None,
        enabled=True,
    )
    return cam


def test_init_with_prepopulated_db():
    cam = make_camera(5, location=(1, 2))
    db = InMemoryCameraDB(initial=[cam])

    ctrl = CameraController(camera_db=db)

    assert 5 in ctrl._cameras
    assert ctrl.total_camera_number == 1
    assert ctrl.next_camera_id == 6


def test_add_camera_success(controller):
    ctrl, db = controller

    ctrl.add_camera(camera_id=1, location=(0, 0), password=None)

    assert 1 in ctrl._cameras
    cam = ctrl._cameras[1]
    assert isinstance(cam.hardware_camera, DeviceCamera)
    assert cam.location == (0, 0)
    assert db.get_camera_by_id(1) is cam
    assert ctrl.total_camera_number == 1
    assert ctrl.next_camera_id >= 2
    assert 1 in db.created


def test_add_camera_duplicate_id_raises(controller):
    ctrl, _ = controller

    ctrl.add_camera(camera_id=1, location=(0, 0))

    with pytest.raises(ValueError):
        ctrl.add_camera(camera_id=1, location=(10, 10))


def test_add_camera_invalid_location_raises(controller):
    ctrl, _ = controller

    with pytest.raises(InvalidLocationError):
        ctrl.add_camera(camera_id=1, location=(-1, 0))

    with pytest.raises(InvalidLocationError):
        ctrl.add_camera(camera_id=2, location=(0, -2))


def test_delete_camera_success(controller):
    ctrl, db = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))

    result = ctrl.delete_camera(1)

    assert result is True
    assert 1 not in ctrl._cameras
    assert db.get_camera_by_id(1) is None
    assert ctrl.total_camera_number == 0
    assert 1 in db.deleted


def test_delete_camera_not_found_raises(controller):
    ctrl, _ = controller

    with pytest.raises(CameraNotFoundError):
        ctrl.delete_camera(999)


def test_require_camera_returns_camera_and_raises_on_missing(controller):
    ctrl, _ = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))

    cam = ctrl._require_camera(1)
    assert cam is ctrl._cameras[1]

    with pytest.raises(CameraNotFoundError):
        ctrl._require_camera(999)


def test_enable_disable_camera_updates_db(controller):
    ctrl, db = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))

    ctrl.disable_camera(1)
    cam = ctrl._cameras[1]
    assert cam.enabled is False
    assert 1 in db.updated

    ctrl.enable_camera(1)
    assert cam.enabled is True
    assert db.updated.count(1) >= 2  # updated twice


def test_enable_disable_cameras_list(controller):
    ctrl, _ = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))
    ctrl.add_camera(camera_id=2, location=(1, 1))

    ctrl.disable_cameras([1, 2])
    assert not ctrl._cameras[1].enabled
    assert not ctrl._cameras[2].enabled

    ctrl.enable_cameras([1])
    assert ctrl._cameras[1].enabled
    assert not ctrl._cameras[2].enabled


def test_enable_disable_all(controller):
    ctrl, _ = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))
    ctrl.add_camera(camera_id=2, location=(1, 1))

    ctrl.disable_all()
    assert all(not cam.enabled for cam in ctrl._cameras.values())

    ctrl.enable_all()
    assert all(cam.enabled for cam in ctrl._cameras.values())


def test_zoom_and_pan_delegate_to_camera_and_update_db(controller):
    ctrl, db = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))
    cam = ctrl._cameras[1]
    cam.enabled = True  # ensure controllable

    start_zoom = cam.zoom_level
    assert ctrl.zoom_in(1) is True
    assert cam.zoom_level == start_zoom + 1

    assert ctrl.zoom_out(1) is True
    assert cam.zoom_level == start_zoom

    start_pan = cam.pan_angle
    assert ctrl.pan_right(1) is True
    assert cam.pan_angle == start_pan + 1

    assert ctrl.pan_left(1) is True
    assert cam.pan_angle == start_pan

    # DB should have several updates registered
    assert 1 in db.updated


def test_zoom_and_pan_missing_camera_raises(controller):
    ctrl, _ = controller

    with pytest.raises(CameraNotFoundError):
        ctrl.zoom_in(999)
    with pytest.raises(CameraNotFoundError):
        ctrl.zoom_out(999)
    with pytest.raises(CameraNotFoundError):
        ctrl.pan_left(999)
    with pytest.raises(CameraNotFoundError):
        ctrl.pan_right(999)


def test_get_single_view_returns_image(controller):
    ctrl, _ = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))
    cam = ctrl._cameras[1]
    cam.enabled = True

    img = ctrl.get_single_view(1)
    assert isinstance(img, Image.Image)
    assert img.size == (DeviceCamera.RETURN_SIZE, DeviceCamera.RETURN_SIZE)


def test_get_single_view_missing_camera_raises(controller):
    ctrl, _ = controller

    with pytest.raises(CameraNotFoundError):
        ctrl.get_single_view(1234)


def test_get_thumbnail_views_locked_and_unlocked(controller):
    ctrl, _ = controller

    # unlocked camera
    ctrl.add_camera(camera_id=1, location=(0, 0))
    cam1 = ctrl._cameras[1]
    cam1.enabled = True
    cam1.has_password = False
    cam1.set_password(None)

    # locked camera
    ctrl.add_camera(camera_id=2, location=(1, 1))
    cam2 = ctrl._cameras[2]
    cam2.enabled = True
    cam2.has_password = True
    cam2.set_password("secret")

    thumbs = ctrl.get_thumbnail_views()
    assert set(thumbs.keys()) == {1, 2}

    assert isinstance(thumbs[1], Image.Image)
    assert thumbs[1].size == (160, 160)

    assert isinstance(thumbs[2], Image.Image)
    assert thumbs[2].size == (160, 160)

    # At least exercise both branches (with and without password)
    # without asserting too much about the exact pixel contents.


def test_password_management(controller):
    ctrl, _ = controller
    ctrl.add_camera(camera_id=1, location=(0, 0))

    # no password set yet
    assert ctrl.validate_camera_password(1, "") is True
    assert ctrl.validate_camera_password(1, "anything") is False

    ctrl.set_camera_password(1, "secret")
    assert ctrl.validate_camera_password(1, "secret") is True
    assert ctrl.validate_camera_password(1, "wrong") is False

    # delete password
    result = ctrl.delete_camera_password(1)
    assert result is True
    assert ctrl.validate_camera_password(1, "") is True
    assert ctrl.validate_camera_password(1, "secret") is False


def test_password_methods_missing_camera_raises(controller):
    ctrl, _ = controller

    with pytest.raises(CameraNotFoundError):
        ctrl.set_camera_password(999, "x")

    with pytest.raises(CameraNotFoundError):
        ctrl.validate_camera_password(999, "")

    with pytest.raises(CameraNotFoundError):
        ctrl.delete_camera_password(999)


def test_add_camera_with_smaller_id_does_not_change_next_id(controller):
    """
    Covers line 97 false-branch (camera_id < next_camera_id).
    """
    ctrl, _ = controller

    # First add a camera with a *larger* id so next_camera_id jumps up.
    ctrl.add_camera(camera_id=5, location=(0, 0))
    next_after_first = ctrl.next_camera_id
    assert next_after_first == 6  # sanity: should be max_id + 1

    # Now add a camera with a *smaller* id than next_camera_id.
    # This exercises the branch where `camera_id >= self.next_camera_id` is False.
    ctrl.add_camera(camera_id=3, location=(1, 1))

    # Both cameras exist…
    assert set(ctrl._cameras.keys()) == {5, 3}

    # …and next_camera_id should *not* shrink back down.
    assert ctrl.next_camera_id == next_after_first
    # Also still respects the general invariant.
    assert ctrl.next_camera_id == max(ctrl._cameras.keys()) + 1


def test_get_camera_info_returns_snapshot(controller):
    """
    Covers lines 123–124: get_camera_info() happy path.
    """
    ctrl, _ = controller

    ctrl.add_camera(camera_id=1, location=(3, 4))
    cam = ctrl._cameras[1]

    # Flip some state to make sure fields really propagate.
    cam.enabled = False

    info = ctrl.get_camera_info(1)

    assert info.camera_id == cam.camera_id
    assert info.location == cam.get_location()
    assert info.enabled == cam.enabled
    assert info.has_password == cam.has_password


def test_get_all_cameras_info_matches_internal_state(controller):
    """
    Covers line 133: get_all_cameras_info() list comprehension.
    """
    ctrl, _ = controller

    ctrl.add_camera(camera_id=1, location=(1, 1))
    ctrl.add_camera(camera_id=2, location=(2, 2))

    infos = ctrl.get_all_cameras_info()
    info_by_id = {info.camera_id: info for info in infos}

    # We should have info for each camera
    assert set(info_by_id.keys()) == {1, 2}

    # Each CameraInfo mirrors its underlying SafeHomeCamera
    for cid in (1, 2):
        cam = ctrl._cameras[cid]
        info = info_by_id[cid]
        assert info.location == cam.get_location()
        assert info.enabled == cam.enabled
        assert info.has_password == cam.has_password


def test_get_thumbnail_views_normal(controller):
    """
    Covers lines 238–241: the `elif not camera.enabled` branch in get_thumbnail_views().
    """
    ctrl, _ = controller

    # Camera 1: disabled, no password -> should use "disabled" placeholder.
    ctrl.add_camera(camera_id=1, location=(0, 0))
    ctrl.enable_camera(1)
    # Camera 2: enabled and unlocked -> should call display_thumbnail().
    ctrl.add_camera(camera_id=2, location=(1, 1))
    ctrl.disable_camera(2)

    ctrl.add_camera(camera_id=3, location=(2, 1), password="hello")

    thumbs = ctrl.get_thumbnail_views()

    # We get thumbnails for both cameras.

    assert set(thumbs.keys()) == {1, 2, 3}
    # Both are real PIL images with the expected thumbnail size.
    assert isinstance(thumbs[1], Image.Image)
    assert isinstance(thumbs[2], Image.Image)
    assert isinstance(thumbs[3], Image.Image)
    assert thumbs[1].size == (160, 160)
    assert thumbs[2].size == (160, 160)
    assert thumbs[3].size == (160, 160)
