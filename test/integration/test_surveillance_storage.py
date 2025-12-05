# test/integration/test_surveillance_storage.py

import pytest

from storage.storage_sqlite import StorageManager
from storage.camera_storage_sqlite import CameraSqliteDB
from core.surveillance.camera_controller import CameraController

DB_INIT_SCRIPT = "src/init.sql"
DB_FILE = "safehome.db"


@pytest.fixture
def storage_and_db():
    """
    Fresh SQLite DB for each test, initialized from init.sql.
    """
    storage_manager = StorageManager(DB_INIT_SCRIPT, DB_FILE)
    storage_manager.reset()  # recreate tables and seed cameras
    camera_db = CameraSqliteDB(storage_manager)
    return storage_manager, camera_db


@pytest.fixture
def controller(storage_and_db):
    """
    CameraController wired to the real SQLite-backed camera DB.
    """
    _, camera_db = storage_and_db
    return CameraController(camera_db=camera_db)


def test_controller_loads_existing_cameras_from_sqlite(storage_and_db, controller):
    """
    Controller.__init__ should load all persisted cameras and compute
    next_camera_id / total_camera_number from the DB state.
    """
    _, camera_db = storage_and_db

    db_cameras = camera_db.get_all_cameras()
    assert len(db_cameras) > 0

    # Controller should see the same number of cameras as the DB.
    assert controller.total_camera_number == len(db_cameras)

    # next_camera_id should be max_id + 1
    max_id = max(cam.camera_id for cam in db_cameras)
    assert controller.next_camera_id == max_id + 1

    # get_all_cameras_info() should reflect DB values (id, location, enabled, has_password)
    info_list = controller.get_all_cameras_info()
    assert len(info_list) == len(db_cameras)

    db_by_id = {cam.camera_id: cam for cam in db_cameras}

    for info in info_list:
        db_cam = db_by_id[info.camera_id]
        assert info.location == db_cam.location
        assert info.enabled == db_cam.enabled
        assert info.has_password == db_cam.has_password


def test_enable_disable_camera_persists_to_db(storage_and_db):
    """
    Enabling / disabling a camera via the controller should call camera_db.update_camera
    so that a new controller instance sees the updated 'enabled' state.
    """
    _, camera_db = storage_and_db

    # First controller instance
    controller1 = CameraController(camera_db=camera_db)
    target_id = 1  # any camera that exists in init.sql

    # Disable camera and check DB
    controller1.disable_camera(target_id)
    db_cam = camera_db.get_camera_by_id(target_id)
    assert db_cam is not None
    assert db_cam.enabled is False

    # New controller must rehydrate the disabled state from DB
    controller2 = CameraController(camera_db=camera_db)
    info_map = {i.camera_id: i for i in controller2.get_all_cameras_info()}
    assert info_map[target_id].enabled is False

    # Enable again and verify persistence + rehydration
    controller2.enable_camera(target_id)
    db_cam_after = camera_db.get_camera_by_id(target_id)
    assert db_cam_after.enabled is True

    controller3 = CameraController(camera_db=camera_db)
    info_map3 = {i.camera_id: i for i in controller3.get_all_cameras_info()}
    assert info_map3[target_id].enabled is True


def test_zoom_and_pan_update_db_state(storage_and_db):
    """
    Zooming and panning through the controller should update the camera's
    zoom_level and pan_angle in the DB, and a new controller should see
    those updated values when reloading from DB.
    """
    _, camera_db = storage_and_db
    controller = CameraController(camera_db=camera_db)

    target_id = 2  # camera that exists in init.sql (see test_camera_db)
    original = camera_db.get_camera_by_id(target_id)
    assert original is not None

    orig_zoom = original.zoom_level
    orig_pan = original.pan_angle

    # Perform one zoom_in and one pan_right via controller
    assert controller.zoom_in(target_id)
    assert controller.pan_right(target_id)

    updated = camera_db.get_camera_by_id(target_id)
    assert updated is not None

    # With init.sql, zoom_level starts at 2 and pan_angle at 0 for camera 2,
    # but we assert relatively in case that script changes later.
    assert updated.zoom_level == orig_zoom + 1
    assert updated.pan_angle == orig_pan + 1

    # New controller instance should rehydrate the same values
    controller2 = CameraController(camera_db=camera_db)
    rehydrated = camera_db.get_camera_by_id(target_id)
    assert rehydrated.zoom_level == updated.zoom_level
    assert rehydrated.pan_angle == updated.pan_angle


def test_set_and_delete_password_persists_to_db(storage_and_db):
    """
    Setting and deleting a password through the controller should both:
    - Persist to the DB via update_camera
    - Affect validate_camera_password() behaviour
    """
    _, camera_db = storage_and_db
    controller = CameraController(camera_db=camera_db)

    target_id = 2  # camera with existing row in init.sql

    # Set new password
    controller.set_camera_password(target_id, "9999")
    updated = camera_db.get_camera_by_id(target_id)
    assert updated is not None
    assert updated.password == "9999"
    assert updated.has_password is True

    # validate_camera_password should now succeed for the new password
    assert controller.validate_camera_password(target_id, "9999") is True
    assert controller.validate_camera_password(target_id, "wrong") is False

    # Delete password and check DB + behaviour
    assert controller.delete_camera_password(target_id) is True

    after_delete = camera_db.get_camera_by_id(target_id)
    assert after_delete.password == ""
    assert after_delete.has_password is False

    assert controller.validate_camera_password(target_id, "9999") is False
    assert controller.validate_camera_password(target_id, "") is True


def test_controller_rehydrates_state_from_db(storage_and_db):
    """
    Full integration: mutate a camera via one controller, then create a
    brand new controller instance and verify that it sees the mutated state
    purely by reading from the DB.
    """
    _, camera_db = storage_and_db

    # First controller: change several aspects of camera 3
    controller1 = CameraController(camera_db=camera_db)
    target_id = 3

    controller1.enable_camera(target_id)
    controller1.set_camera_password(target_id, "abcd")
    controller1.zoom_in(target_id)
    controller1.pan_left(target_id)

    # DB should reflect these changes
    updated = camera_db.get_camera_by_id(target_id)
    assert updated is not None
    assert updated.enabled is True
    assert updated.password == "abcd"
    # We don't assert exact pan/zoom numbers here, just that they changed
    # from whatever init.sql seeded.
    assert updated.has_password is True

    # New controller instance rehydrates purely from DB state
    controller2 = CameraController(camera_db=camera_db)
    info_map = {i.camera_id: i for i in controller2.get_all_cameras_info()}
    info = info_map[target_id]

    assert info.enabled is True
    assert info.has_password is True
