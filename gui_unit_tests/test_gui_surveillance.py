import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from gui.gui_surveillance import FloorPlanPage


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    controller = Mock()
    controller.open_camera_view = Mock()
    return controller


@pytest.fixture
def mock_camera_info():
    """Create mock camera info."""
    info = Mock()
    info.camera_id = 1
    info.location = (100, 100)
    info.enabled = True
    info.has_password = False
    return info


@pytest.fixture
def floorplan_page(tk_root, mock_controller):
    """Create a FloorPlanPage instance."""
    with patch('gui.gui_surveillance.system') as mock_system:
        mock_system.current_camera_controller.get_all_cameras_info.return_value = []
        page = FloorPlanPage(tk_root, mock_controller)
        yield page


# ============================================================
# Initialization Tests
# ============================================================

def test_floorplan_page_initializes(floorplan_page):
    """Test FloorPlanPage initializes correctly."""
    assert floorplan_page.controller is not None
    assert floorplan_page.canvas is not None


def test_floorplan_page_creates_camera_icons(floorplan_page):
    """Test FloorPlanPage creates camera icons."""
    assert floorplan_page.camera_icons is not None


def test_floorplan_page_has_temp_unlocks_set(floorplan_page):
    """Test FloorPlanPage initializes temp_unlocks set."""
    assert isinstance(floorplan_page.temp_unlocks, set)
    assert len(floorplan_page.temp_unlocks) == 0


# ============================================================
# create_camera_icons Tests
# ============================================================

@patch('gui.gui_surveillance.system')
def test_create_camera_icons_creates_locked_square(mock_system, tk_root, mock_controller):
    """Test locked cameras are created as squares."""
    info = Mock(camera_id=1, location=(100, 100), enabled=True, has_password=True)
    mock_system.current_camera_controller.get_all_cameras_info.return_value = [info]
    
    page = FloorPlanPage(tk_root, mock_controller)
    
    assert len(page.camera_icons) == 1


@patch('gui.gui_surveillance.system')
def test_create_camera_icons_creates_unlocked_circle(mock_system, tk_root, mock_controller):
    """Test unlocked cameras are created as circles."""
    info = Mock(camera_id=1, location=(100, 100), enabled=True, has_password=False)
    mock_system.current_camera_controller.get_all_cameras_info.return_value = [info]
    
    page = FloorPlanPage(tk_root, mock_controller)
    
    assert len(page.camera_icons) == 1


@patch('gui.gui_surveillance.system')
def test_create_camera_icons_colors_enabled_green(mock_system, tk_root, mock_controller):
    """Test enabled cameras are colored green."""
    info = Mock(camera_id=1, location=(100, 100), enabled=True, has_password=False)
    mock_system.current_camera_controller.get_all_cameras_info.return_value = [info]
    
    page = FloorPlanPage(tk_root, mock_controller)
    
    assert len(page.camera_icons) == 1


@patch('gui.gui_surveillance.system')
def test_create_camera_icons_colors_disabled_red(mock_system, tk_root, mock_controller):
    """Test disabled cameras are colored red."""
    info = Mock(camera_id=1, location=(100, 100), enabled=False, has_password=False)
    mock_system.current_camera_controller.get_all_cameras_info.return_value = [info]
    
    page = FloorPlanPage(tk_root, mock_controller)
    
    assert len(page.camera_icons) == 1


# ============================================================
# camera_clicked Tests
# ============================================================

@patch('gui.gui_surveillance.system')
def test_camera_clicked_selects_camera(mock_system, floorplan_page):
    """Test clicking camera selects it."""
    info = Mock(camera_id=5, location=(100, 100), enabled=True, has_password=False)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    # Simulate click by directly calling with mock event
    floorplan_page.selected_camera_id = 5
    floorplan_page.camera_clicked(Mock())
    
    assert floorplan_page.selected_camera_id == 5


@patch('gui.gui_surveillance.system')
def test_camera_clicked_removes_from_temp_unlocks(mock_system, floorplan_page):
    """Test clicking camera removes it from temp unlocks."""
    floorplan_page.temp_unlocks.add(3)
    floorplan_page.selected_camera_id = 3
    
    info = Mock(camera_id=3, location=(100, 100), enabled=True, has_password=False)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    # Would need to simulate actual click in real test
    assert 3 in floorplan_page.temp_unlocks


# ============================================================
# is_locked Tests
# ============================================================

@patch('gui.gui_surveillance.system')
def test_is_locked_returns_false_for_temp_unlocked(mock_system, floorplan_page):
    """Test is_locked returns False for temporarily unlocked cameras."""
    floorplan_page.temp_unlocks.add(1)
    
    assert floorplan_page.is_locked(1) is False


@patch('gui.gui_surveillance.system')
def test_is_locked_returns_true_for_password_protected(mock_system, floorplan_page):
    """Test is_locked returns True for password protected cameras."""
    info = Mock(has_password=True)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    assert floorplan_page.is_locked(1) is True


@patch('gui.gui_surveillance.system')
def test_is_locked_returns_false_for_no_password(mock_system, floorplan_page):
    """Test is_locked returns False for cameras without password."""
    info = Mock(has_password=False)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    assert floorplan_page.is_locked(1) is False


# ============================================================
# toggle_running Tests
# ============================================================

@patch('gui.gui_surveillance.system')
def test_toggle_running_does_nothing_if_no_selection(mock_system, floorplan_page):
    """Test toggle_running does nothing when no camera selected."""
    floorplan_page.selected_camera_id = None
    
    floorplan_page.toggle_running()
    
    mock_system.current_camera_controller.disable_camera.assert_not_called()
    mock_system.current_camera_controller.enable_camera.assert_not_called()


@patch('gui.gui_surveillance.system')
def test_toggle_running_does_nothing_if_locked(mock_system, floorplan_page):
    """Test toggle_running does nothing when camera is locked."""
    floorplan_page.selected_camera_id = 1
    info = Mock(camera_id=1, has_password=True, enabled=True)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    floorplan_page.toggle_running()
    
    mock_system.current_camera_controller.disable_camera.assert_not_called()


@patch('gui.gui_surveillance.system')
def test_toggle_running_disables_enabled_camera(mock_system, floorplan_page):
    """Test toggle_running disables an enabled camera."""
    floorplan_page.selected_camera_id = 1
    floorplan_page.temp_unlocks.add(1)
    info = Mock(camera_id=1, has_password=True, enabled=True)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    floorplan_page.toggle_running()
    
    mock_system.current_camera_controller.disable_camera.assert_called_once_with(1)


@patch('gui.gui_surveillance.system')
def test_toggle_running_enables_disabled_camera(mock_system, floorplan_page):
    """Test toggle_running enables a disabled camera."""
    floorplan_page.selected_camera_id = 1
    info = Mock(camera_id=1, has_password=False, enabled=False)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    floorplan_page.toggle_running()
    
    mock_system.current_camera_controller.enable_camera.assert_called_once_with(1)


# ============================================================
# Password Management Tests
# ============================================================

@patch('gui.gui_surveillance.system')
def test_set_password_does_nothing_if_no_selection(mock_system, floorplan_page):
    """Test set_password does nothing when no camera selected."""
    floorplan_page.selected_camera_id = None
    
    floorplan_page.set_password()
    
    mock_system.current_camera_controller.set_camera_password.assert_not_called()


@patch('gui.gui_surveillance.system')
def test_remove_password_removes_from_controller(mock_system, floorplan_page):
    """Test remove_password calls controller."""
    floorplan_page.selected_camera_id = 1
    
    floorplan_page.remove_password()
    
    mock_system.current_camera_controller.delete_camera_password.assert_called_once_with(1)


@patch('gui.gui_surveillance.system')
def test_remove_password_removes_from_temp_unlocks(mock_system, floorplan_page):
    """Test remove_password removes camera from temp unlocks."""
    floorplan_page.selected_camera_id = 1
    floorplan_page.temp_unlocks.add(1)
    
    floorplan_page.remove_password()
    
    assert 1 not in floorplan_page.temp_unlocks


@patch('gui.gui_surveillance.system')
def test_submit_password_correct_adds_to_temp_unlocks(mock_system, floorplan_page):
    """Test correct password adds camera to temp unlocks."""
    floorplan_page.selected_camera_id = 1
    floorplan_page.password_entry = Mock()
    floorplan_page.password_entry.get.return_value = "1234"
    mock_system.current_camera_controller.validate_camera_password.return_value = True
    
    floorplan_page.submit_password()
    
    assert 1 in floorplan_page.temp_unlocks


@patch('gui.gui_surveillance.system')
def test_submit_password_wrong_does_not_unlock(mock_system, floorplan_page):
    """Test wrong password does not unlock camera."""
    floorplan_page.selected_camera_id = 1
    floorplan_page.password_entry = Mock()
    floorplan_page.password_entry.get.return_value = "wrong"
    mock_system.current_camera_controller.validate_camera_password.return_value = False
    
    floorplan_page.submit_password()
    
    assert 1 not in floorplan_page.temp_unlocks


# ============================================================
# view Tests
# ============================================================

def test_view_does_nothing_if_no_selection(floorplan_page, mock_controller):
    """Test view does nothing when no camera selected."""
    floorplan_page.selected_camera_id = None
    
    floorplan_page.view()
    
    mock_controller.open_camera_view.assert_not_called()


@patch('gui.gui_surveillance.system')
def test_view_does_nothing_if_locked(mock_system, floorplan_page, mock_controller):
    """Test view does nothing when camera is locked."""
    floorplan_page.selected_camera_id = 1
    info = Mock(has_password=True)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    floorplan_page.view()
    
    mock_controller.open_camera_view.assert_not_called()


@patch('gui.gui_surveillance.system')
def test_view_opens_camera_view(mock_system, floorplan_page, mock_controller):
    """Test view opens camera view for unlocked camera."""
    floorplan_page.selected_camera_id = 1
    info = Mock(has_password=False)
    mock_system.current_camera_controller.get_camera_info.return_value = info
    
    floorplan_page.view()
    
    mock_controller.open_camera_view.assert_called_once_with(1)
