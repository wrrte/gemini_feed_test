from __future__ import annotations

from typing import Dict, List, Set

import pytest
from PIL import Image

from storage.storage_sqlite import StorageManager
from storage.camera_storage_sqlite import CameraSqliteDB
from core.surveillance.camera_controller import CameraController
from core.surveillance.camera_exceptions import (
    CameraNotFoundError,
    InvalidLocationError,
    CameraDisabledError,
)
from device.device_camera import DeviceCamera


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_device_camera_image(monkeypatch):
    """
    Patch DeviceCamera.Image.open so that integration tests do not depend on
    real image files or a GUI environment.
    """

    import device.device_camera as device_camera_module

    def fake_open(path: str) -> Image.Image:
        size = device_camera_module.DeviceCamera.SOURCE_SIZE
        return Image.new("RGB", (size, size), "white")

    monkeypatch.setattr(device_camera_module.Image, "open", fake_open)


@pytest.fixture
def storage_manager(tmp_path) -> StorageManager:
    """
    Use a temporary SQLite file for each test, but still use the real init.sql
    schema and seed data.
    """
    init_script_path = "src/init.sql"
    db_path = tmp_path / "safehome_integration.db"

    manager = StorageManager(init_script_path, str(db_path))
    # Ensure we always start from a clean, seeded DB state.
    manager.reset()
    return manager


@pytest.fixture
def camera_db(storage_manager) -> CameraSqliteDB:
    return CameraSqliteDB(storage_manager)


@pytest.fixture
def controller(camera_db) -> CameraController:
    return CameraController(camera_db=camera_db)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _all_ids_from_db(camera_db: CameraSqliteDB) -> Set[int]:
    return {cam.camera_id for cam in camera_db.get_all_cameras()}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_next_camera_id_respects_db_state(camera_db):
    """
    Integration: controller.next_camera_id is based on the IDs actually stored
    in the database when the controller is created.
    """
    ctrl = CameraController(camera_db=camera_db)

    db_ids = _all_ids_from_db(camera_db)
    if db_ids:
        assert ctrl.next_camera_id == max(db_ids) + 1
    else:
        # If init.sql ever starts with no cameras, next id should be 1.
        assert ctrl.next_camera_id == 1


def test_get_all_cameras_info_matches_db(camera_db, controller):
    """
    Integration: CameraInfo snapshots reflect the state stored in the DB.
    """
    ctrl = controller

    db_cameras = {cam.camera_id: cam for cam in camera_db.get_all_cameras()}
    infos = {info.camera_id: info for info in ctrl.get_all_cameras_info()}

    assert set(db_cameras.keys()) == set(infos.keys())

    for cid, cam in db_cameras.items():
        info = infos[cid]
        assert info.camera_id == cam.camera_id
        assert info.location == cam.location
        assert info.enabled == cam.enabled
        assert info.has_password == cam.has_password


def test_add_camera_invalid_location_leaves_db_unchanged(camera_db, controller):
    """
    Integration: Invalid location in add_camera raises and does not modify DB.
    """
    ctrl = controller
    before_ids = _all_ids_from_db(camera_db)

    # Negative coordinates should be rejected
    with pytest.raises(InvalidLocationError):
        ctrl.add_camera(camera_id=99, location=(-1, 0))

    after_ids = _all_ids_from_db(camera_db)
    assert after_ids == before_ids


def test_add_camera_duplicate_id_leaves_db_unchanged(camera_db, controller):
    """
    Integration: Attempting to add a camera with an existing ID raises and does
    not modify DB.
    """
    ctrl = controller

    existing_ids = sorted(_all_ids_from_db(camera_db))
    assert existing_ids, "init.sql should seed at least one camera"
    existing_id = existing_ids[0]

    before = camera_db.get_camera_by_id(existing_id)

    # Controller should reject duplicate ID before touching the DB
    with pytest.raises(ValueError):
        ctrl.add_camera(camera_id=existing_id, location=(10, 10))

    after = camera_db.get_camera_by_id(existing_id)

    # Nothing about that camera should have changed due to the failed call
    assert after is not None
    assert after.location == before.location
    assert after.pan_angle == before.pan_angle
    assert after.zoom_level == before.zoom_level
    assert after.password == before.password
    assert after.enabled == before.enabled


def test_disabled_camera_cannot_be_controlled_and_db_unchanged(camera_db, controller):
    """
    Integration: A disabled camera cannot be zoomed/panned, and failed
    operations do not update the DB.
    """
    ctrl = controller

    # Use any existing camera from the DB
    cameras = camera_db.get_all_cameras()
    assert cameras, "init.sql should seed some cameras"
    target_id = cameras[0].camera_id

    # Disable it via the controller so DB is also updated
    ctrl.disable_camera(target_id)

    before = camera_db.get_camera_by_id(target_id)
    assert before is not None
    assert before.enabled is False

    # Attempting to control a disabled camera should raise
    with pytest.raises(CameraDisabledError):
        ctrl.zoom_in(target_id)

    with pytest.raises(CameraDisabledError):
        ctrl.pan_left(target_id)

    after = camera_db.get_camera_by_id(target_id)
    assert after is not None
    # Pan/zoom must remain unchanged after failed operations
    assert after.zoom_level == before.zoom_level
    assert after.pan_angle == before.pan_angle
    assert after.enabled is False


def test_multiple_cameras_state_persisted_independently(camera_db, controller):
    """
    Integration: Zoom/pan changes on one camera do not affect others and are
    correctly persisted in the DB and visible to a new controller instance.
    """
    ctrl = controller
    db_cameras = camera_db.get_all_cameras()
    assert len(db_cameras) >= 2, "Need at least two seed cameras for this test"

    cam1_id = db_cameras[0].camera_id
    cam2_id = db_cameras[1].camera_id

    # Ensure both cameras are enabled so control operations won't raise
    ctrl.enable_camera(cam1_id)
    ctrl.enable_camera(cam2_id)

    before1 = camera_db.get_camera_by_id(cam1_id)
    before2 = camera_db.get_camera_by_id(cam2_id)
    assert before1 is not None and before2 is not None

    # Apply different changes to each camera via the controller
    ctrl.zoom_in(cam1_id)
    ctrl.zoom_in(cam1_id)
    ctrl.pan_right(cam2_id)

    after1 = camera_db.get_camera_by_id(cam1_id)
    after2 = camera_db.get_camera_by_id(cam2_id)
    assert after1 is not None and after2 is not None

    assert after1.zoom_level == before1.zoom_level + 2
    assert after1.pan_angle == before1.pan_angle

    assert after2.zoom_level == before2.zoom_level
    assert after2.pan_angle == before2.pan_angle + 1

    # New controller instance should see the same persisted state
    ctrl2 = CameraController(camera_db=camera_db)
    cam1_again = ctrl2._cameras[cam1_id]
    cam2_again = ctrl2._cameras[cam2_id]

    assert cam1_again.zoom_level == after1.zoom_level
    assert cam1_again.pan_angle == after1.pan_angle
    assert cam2_again.zoom_level == after2.zoom_level
    assert cam2_again.pan_angle == after2.pan_angle


def test_enable_disable_all_persists_across_controller_instances(camera_db):
    """
    Integration: enable_all / disable_all modify the DB and the effect is
    visible to newly created controllers.
    """
    ctrl = CameraController(camera_db=camera_db)

    # Disable all and verify DB state
    ctrl.disable_all()
    cameras = camera_db.get_all_cameras()
    assert cameras
    assert all(not cam.enabled for cam in cameras)

    # New controller should see them all disabled
    ctrl2 = CameraController(camera_db=camera_db)
    infos = ctrl2.get_all_cameras_info()
    assert all(not info.enabled for info in infos)

    # Re-enable all and check again
    ctrl2.enable_all()
    cameras_after = camera_db.get_all_cameras()
    assert all(cam.enabled for cam in cameras_after)


def test_get_single_view_returns_image_with_real_db(camera_db, controller):
    """
    Integration: get_single_view goes through controller -> SafeHomeCamera ->
    DeviceCamera and returns a Pillow Image.
    """
    ctrl = controller

    cameras = camera_db.get_all_cameras()
    assert cameras, "init.sql should seed some cameras"
    target_id = cameras[0].camera_id

    # Ensure it is enabled so display_view does not raise
    ctrl.enable_camera(target_id)

    img = ctrl.get_single_view(target_id)
    assert isinstance(img, Image.Image)
    assert img.size == (DeviceCamera.RETURN_SIZE, DeviceCamera.RETURN_SIZE)


def test_thumbnail_views_use_locked_and_disabled_placeholders(camera_db, controller):
    """
    Integration: get_thumbnail_views returns different placeholder images for
    locked vs disabled cameras, and real thumbnails for others.
    """
    ctrl = controller

    cameras = camera_db.get_all_cameras()
    assert len(cameras) >= 2, "Need at least two cameras for this test"

    cam1_id = cameras[0].camera_id
    cam2_id = cameras[1].camera_id

    # Camera 1: enabled and locked with a password
    ctrl.enable_camera(cam1_id)
    ctrl.set_camera_password(cam1_id, "secret")

    # Camera 2: disabled and no password
    ctrl.disable_camera(cam2_id)
    ctrl.delete_camera_password(cam2_id)

    thumbs = ctrl.get_thumbnail_views()

    # Should have entries for all cameras known to controller
    assert set(thumbs.keys()) == {c.camera_id for c in ctrl._cameras.values()}

    img1 = thumbs[cam1_id]
    img2 = thumbs[cam2_id]

    assert isinstance(img1, Image.Image)
    assert isinstance(img2, Image.Image)
    assert img1.size == (160, 160)
    assert img2.size == (160, 160)

    # Locked and Disabled placeholders should not be identical images.
    # (Not checking exact pixels, just that they're not trivially the same.)
    assert list(img1.getdata()) != list(img2.getdata())


def test_validate_password_roundtrip_with_db(camera_db, controller):
    """
    Integration: setting / deleting passwords via the controller is correctly
    persisted in DB and checked by validate_camera_password.
    """
    ctrl = controller

    cameras = camera_db.get_all_cameras()
    assert cameras, "init.sql should seed some cameras"
    target_id = cameras[0].camera_id

    # Initially, whatever the DB has, validating with empty string should
    # reflect the actual stored password.
    original = camera_db.get_camera_by_id(target_id)
    assert original is not None

    # Set a new password
    ctrl.set_camera_password(target_id, "9999")
    assert ctrl.validate_camera_password(target_id, "9999") is True
    assert ctrl.validate_camera_password(target_id, "0000") is False

    # Delete the password
    result = ctrl.delete_camera_password(target_id)
    assert result is True  # There *was* a password to delete
    # Our convention: "" is used to test "no password"
    assert ctrl.validate_camera_password(target_id, "") is True
    assert ctrl.validate_camera_password(target_id, "9999") is False
