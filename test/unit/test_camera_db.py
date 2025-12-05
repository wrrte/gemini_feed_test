from storage.storage_sqlite import StorageManager
from storage.camera_storage_sqlite import CameraSqliteDB
from core.surveillance.safehome_camera import SafeHomeCamera
from device.device_camera import DeviceCamera


def test_get_all_camera():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    camera_db = CameraSqliteDB(storage_manager)

    cameras = camera_db.get_all_cameras()

    assert len(cameras) == 3


def test_update_camera():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    camera_db = CameraSqliteDB(storage_manager)

    camera = SafeHomeCamera(
                camera_id       = 1              ,
                location        = (200, 250)     , 
                hardware_camera = DeviceCamera() ,
                has_password    = False          ,
                password        = ""             ,
                enabled         = False
            )

    camera_db.update_camera(camera)

    cameras = camera_db.get_all_cameras()

    assert cameras[0].camera_id == 1
    assert cameras[0].location == (200, 250)
    assert cameras[0].password == ""
    assert cameras[0].has_password == False
    assert cameras[0].enabled == False


def test_get_camera_by_id():
    storage_manager = StorageManager("src/init.sql", "safehome.db")
    storage_manager.reset()

    camera_db = CameraSqliteDB(storage_manager)

    camera = camera_db.get_camera_by_id(2)
    assert camera.camera_id == 2
    assert camera.location == (220, 180)
    assert camera.pan_angle == 0
    assert camera.zoom_level == 2
    assert camera.password == "1234"
    assert camera.has_password == True
    assert camera.enabled == True
