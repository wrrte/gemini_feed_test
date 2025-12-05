# tests/test_safehome_camera.py

import pytest
from PIL import Image

from core.surveillance.safehome_camera import SafeHomeCamera
from device.device_camera import DeviceCamera
from core.surveillance.camera_exceptions import (
    InvalidLocationError,
    CameraDisabledError,
)


@pytest.fixture(autouse=True)
def patch_device_camera_image(monkeypatch):
    # Patch DeviceCamera.Image.open so tests don't depend on real
    # ../camera{id}.jpg files or trigger Tk message boxes.
    import device.device_camera as device_camera_module

    def fake_open(path):
        size = device_camera_module.DeviceCamera.SOURCE_SIZE
        return Image.new("RGB", (size, size), "white")

    monkeypatch.setattr(device_camera_module.Image, "open", fake_open)


@pytest.fixture
def camera_and_hw():
    # Create a real DeviceCamera + SafeHomeCamera pair.
    # has_password starts False; password=None; enabled=False.
    hw = DeviceCamera()
    cam = SafeHomeCamera(
        camera_id=1,
        location=(10, 20),
        hardware_camera=hw,
        has_password=False,
        password=None,
        enabled=False,
    )
    return cam, hw


def test_init_sets_id_and_location_and_updates_hardware(camera_and_hw):
    cam, hw = camera_and_hw

    assert cam.get_id() == 1
    assert cam.get_location() == (10, 20)

    # Interaction with the real driver: SafeHomeCamera.__post_init calls set_id
    assert hw.get_id() == 1


def test_set_location_valid_and_invalid(camera_and_hw):
    cam, _ = camera_and_hw

    cam.set_location((5, 7))
    assert cam.get_location() == (5, 7)

    # Negative coordinates should raise and not change the current location
    with pytest.raises(InvalidLocationError):
        cam.set_location((-1, 0))
    assert cam.get_location() == (5, 7)

    with pytest.raises(InvalidLocationError):
        cam.set_location((0, -3))
    assert cam.get_location() == (5, 7)


def test_set_id_validation_and_hardware_update(camera_and_hw):
    cam, hw = camera_and_hw

    with pytest.raises(ValueError):
        cam.set_id(0)
    with pytest.raises(ValueError):
        cam.set_id(-5)

    cam.set_id(42)
    assert cam.get_id() == 42
    assert hw.get_id() == 42


def test_enable_and_disable_toggle_enabled_flag(camera_and_hw):
    cam, _ = camera_and_hw

    cam.enable()
    assert cam.enabled is True

    cam.disable()
    assert cam.enabled is False


def test_display_view_raises_when_disabled(camera_and_hw):
    cam, _ = camera_and_hw

    with pytest.raises(CameraDisabledError):
        cam.display_view()


def test_display_view_returns_image_when_enabled(camera_and_hw):
    cam, _ = camera_and_hw

    cam.enabled = True

    img = cam.display_view()
    assert isinstance(img, Image.Image)
    assert img.size == (DeviceCamera.RETURN_SIZE, DeviceCamera.RETURN_SIZE)


def test_display_thumbnail_returns_resized_image(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = True

    thumb = cam.display_thumbnail()
    assert isinstance(thumb, Image.Image)
    assert thumb.size == (160, 160)


def test_control_methods_raise_when_disabled(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = False

    with pytest.raises(CameraDisabledError):
        cam.zoom_in()
    with pytest.raises(CameraDisabledError):
        cam.zoom_out()
    with pytest.raises(CameraDisabledError):
        cam.pan_left()
    with pytest.raises(CameraDisabledError):
        cam.pan_right()


def test_zoom_in_and_zoom_out_change_zoom_level(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = True

    start_zoom = cam.zoom_level
    assert cam.zoom_in() is True
    assert cam.zoom_level == start_zoom + 1

    assert cam.zoom_out() is True
    assert cam.zoom_level == start_zoom


def test_zoom_in_clamps_at_driver_limit(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = True

    results = [cam.zoom_in() for _ in range(8)]
    assert any(r is False for r in results)


def test_zoom_out_clamps_at_driver_limit(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = True

    assert cam.zoom_out() is True  # 2 -> 1
    result = cam.zoom_out()  # 1 -> clamp
    assert result is False


def test_pan_right_and_left_change_pan_angle(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = True

    start_pan = cam.pan_angle
    assert cam.pan_right() is True
    assert cam.pan_angle == start_pan + 1

    assert cam.pan_left() is True
    assert cam.pan_angle == start_pan


def test_pan_right_clamps_at_driver_limit(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = True

    results = [cam.pan_right() for _ in range(7)]
    assert any(r is False for r in results)


def test_pan_left_clamps_at_driver_limit(camera_and_hw):
    cam, _ = camera_and_hw
    cam.enabled = True

    results = [cam.pan_left() for _ in range(7)]
    assert any(r is False for r in results)


def test_set_and_get_password(camera_and_hw):
    cam, _ = camera_and_hw

    assert cam.get_password() is None
    cam.set_password("secret")
    assert cam.get_password() == "secret"

    cam.set_password(None)
    assert cam.get_password() is None
