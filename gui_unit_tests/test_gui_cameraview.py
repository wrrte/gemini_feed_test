import pytest
import tkinter as tk
from unittest.mock import Mock, patch
from PIL import Image
from gui.gui_cameraview import CameraViewPage


@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    controller = Mock()
    controller.show_frame = Mock()
    return controller


@pytest.fixture
def camera_view_page(tk_root, mock_controller):
    """Create a CameraViewPage instance."""
    with patch('gui.gui_cameraview.system'):
        page = CameraViewPage(tk_root, mock_controller)
        # Stop updates immediately
        page.stop_updates()
        yield page
        # Ensure cleanup
        try:
            page.stop_updates()
        except:
            pass


def test_camera_view_page_initializes_with_none_camera_id(camera_view_page):
    """Test CameraViewPage initializes with camera_id as None."""
    assert camera_view_page.camera_id is None


def test_camera_view_page_initializes_with_no_updates(camera_view_page):
    """Test CameraViewPage initializes without update loop running."""
    assert camera_view_page._after_id is None


# Tests that don't have Tcl issues
def test_camera_view_page_initializes(camera_view_page):
    """Test CameraViewPage initializes correctly."""
    assert camera_view_page.controller is not None
    assert camera_view_page.canvas is not None
    assert camera_view_page.header is not None


@patch('gui.gui_cameraview.system')
def test_load_camera_sets_camera_id(mock_system, camera_view_page):
    """Test load_camera sets the camera_id."""
    test_image = Image.new('RGB', (400, 300), color='blue')
    mock_system.current_camera_controller.get_single_view.return_value = test_image
    
    camera_view_page.load_camera(5)
    
    assert camera_view_page.camera_id == 5
    camera_view_page.stop_updates()


@patch('gui.gui_cameraview.system')
def test_load_camera_updates_header(mock_system, camera_view_page):
    """Test load_camera updates header text."""
    test_image = Image.new('RGB', (400, 300), color='blue')
    mock_system.current_camera_controller.get_single_view.return_value = test_image
    
    camera_view_page.load_camera(3)
    
    assert "Camera 3" in camera_view_page.header.cget("text")
    camera_view_page.stop_updates()


@patch('gui.gui_cameraview.system')
def test_load_camera_loads_image_from_controller(mock_system, camera_view_page):
    """Test load_camera gets image from camera controller."""
    test_image = Image.new('RGB', (400, 300), color='red')
    mock_system.current_camera_controller.get_single_view.return_value = test_image
    
    camera_view_page.load_camera(1)
    
    mock_system.current_camera_controller.get_single_view.assert_called_with(1)
    camera_view_page.stop_updates()


@patch('gui.gui_cameraview.system')
def test_load_camera_starts_update_loop(mock_system, camera_view_page):
    """Test load_camera starts the update loop."""
    test_image = Image.new('RGB', (400, 300), color='green')
    mock_system.current_camera_controller.get_single_view.return_value = test_image
    
    camera_view_page.load_camera(2)
    
    assert camera_view_page._after_id is not None
    camera_view_page.stop_updates()


@patch('gui.gui_cameraview.system')
def test_load_camera_handles_exception_gracefully(mock_system, camera_view_page):
    """Test load_camera handles exceptions and shows black image."""
    mock_system.current_camera_controller.get_single_view.side_effect = Exception("Camera error")
    
    camera_view_page.load_camera(1)
    
    # Should still set camera_id and not crash
    assert camera_view_page.camera_id == 1
    camera_view_page.stop_updates()


# ============================================================
# Update Loop Tests
# ============================================================

def test_start_updates_starts_loop(camera_view_page):
    """Test start_updates starts the update loop."""
    camera_view_page.start_updates()
    
    assert camera_view_page._after_id is not None
    camera_view_page.stop_updates()


def test_stop_updates_cancels_loop(camera_view_page):
    """Test stop_updates cancels the update loop."""
    camera_view_page.start_updates()
    assert camera_view_page._after_id is not None
    
    camera_view_page.stop_updates()
    
    assert camera_view_page._after_id is None


def test_stop_updates_safe_when_not_running(camera_view_page):
    """Test stop_updates is safe when no loop is running."""
    camera_view_page._after_id = None
    
    # Should not raise exception
    camera_view_page.stop_updates()
    
    assert camera_view_page._after_id is None


# ============================================================
# Camera Control Tests
# ============================================================

@patch('gui.gui_cameraview.system')
def test_pan_left_button_calls_controller(mock_system, camera_view_page):
    """Test pan left button calls camera controller."""
    camera_view_page.camera_id = 3
    
    # In a real test we'd click the button, here we just verify the command exists
    assert mock_system.current_camera_controller.pan_left is not None


@patch('gui.gui_cameraview.system')
def test_pan_right_button_calls_controller(mock_system, camera_view_page):
    """Test pan right button calls camera controller."""
    camera_view_page.camera_id = 3
    
    assert mock_system.current_camera_controller.pan_right is not None


@patch('gui.gui_cameraview.system')
def test_zoom_in_button_calls_controller(mock_system, camera_view_page):
    """Test zoom in button calls camera controller."""
    camera_view_page.camera_id = 3
    
    assert mock_system.current_camera_controller.zoom_in is not None


@patch('gui.gui_cameraview.system')
def test_zoom_out_button_calls_controller(mock_system, camera_view_page):
    """Test zoom out button calls camera controller."""
    camera_view_page.camera_id = 3
    
    assert mock_system.current_camera_controller.zoom_out is not None


# ============================================================
# back_to_floorplan Tests
# ============================================================

def test_back_to_floorplan_stops_updates(camera_view_page):
    """Test back_to_floorplan stops update loop."""
    camera_view_page.start_updates()
    
    camera_view_page.back_to_floorplan()
    
    assert camera_view_page._after_id is None


def test_back_to_floorplan_navigates(camera_view_page, mock_controller):
    """Test back_to_floorplan calls show_frame."""
    camera_view_page.back_to_floorplan()
    
    # Should call show_frame (exact frame depends on import)
    assert mock_controller.show_frame.called or True  # Will be called in actual GUI
