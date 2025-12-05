import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from gui.gui_securityzone import SecurityZonePage
from core.security.security_zone_geometry.area import Square


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    return Mock()


@pytest.fixture
def security_zone_page(tk_root, mock_controller):
    """Create a SecurityZonePage instance."""
    with patch('gui.gui_securityzone.system') as mock_system:
        mock_system.current_security_manager.sensors.keys.return_value = []
        mock_system.current_security_manager.security_zones = []
        page = SecurityZonePage(tk_root, mock_controller)
        yield page


# ============================================================
# Initialization Tests
# ============================================================

def test_security_zone_page_initializes(security_zone_page):
    """Test SecurityZonePage initializes correctly."""
    assert security_zone_page.controller is not None
    assert security_zone_page.canvas is not None
    assert security_zone_page.sensors is not None
    assert security_zone_page.security_zones is not None


def test_security_zone_page_has_sensor_icons(security_zone_page):
    """Test SecurityZonePage creates sensor icons."""
    assert security_zone_page.sensor_icons is not None


def test_security_zone_page_has_zone_icons(security_zone_page):
    """Test SecurityZonePage creates zone icons."""
    assert security_zone_page.zone_icons is not None


def test_security_zone_page_initializes_state_variables(security_zone_page):
    """Test SecurityZonePage initializes state variables."""
    assert security_zone_page.selected_zone is None
    assert security_zone_page.dragging is False
    assert security_zone_page.resizing is False
    assert security_zone_page.resize_handle is None


# ============================================================
# refresh_security_zones Tests
# ============================================================

@patch('gui.gui_securityzone.system')
def test_refresh_security_zones_syncs_with_backend(mock_system, security_zone_page):
    """Test refresh_security_zones syncs with backend zones."""
    zone1 = Mock(id=1, enabled=True)
    zone1.area = Mock(up_left=(10, 20), down_right=(100, 200))
    mock_system.current_security_manager.security_zones = [zone1]
    
    security_zone_page.refresh_security_zones()
    
    assert "Zone 1" in security_zone_page.security_zones


@patch('gui.gui_securityzone.system')
def test_refresh_security_zones_clears_selection(mock_system, security_zone_page):
    """Test refresh_security_zones clears selection."""
    security_zone_page.selected_zone = "Zone A"
    mock_system.current_security_manager.security_zones = []
    
    security_zone_page.refresh_security_zones()
    
    assert security_zone_page.selected_zone is None


# ============================================================
# push_zone_to_backend Tests
# ============================================================

@patch('gui.gui_securityzone.system')
def test_push_zone_to_backend_updates_backend(mock_system, security_zone_page):
    """Test push_zone_to_backend updates SecurityManager."""
    security_zone_page.security_zones = {
        "Zone 1": {
            "top_left": (10, 20),
            "bottom_right": (100, 200),
            "enabled": True
        }
    }
    
    security_zone_page.push_zone_to_backend("Zone 1")
    
    mock_system.current_security_manager.update_security_zone.assert_called_once()


# ============================================================
# refresh_sensor_states Tests
# ============================================================

@patch('gui.gui_securityzone.system')
def test_refresh_sensor_states_updates_colors(mock_system, security_zone_page):
    """Test refresh_sensor_states updates sensor colors."""
    sensor = Mock(armed=True)
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    mock_system.current_security_manager.update.return_value = None
    
    security_zone_page.refresh_sensor_states()
    
    mock_system.current_security_manager.update.assert_called_once()


# ============================================================
# add_zone Tests
# ============================================================

@patch('gui.gui_securityzone.system')
def test_add_zone_adds_to_backend(mock_system, security_zone_page):
    """Test add_zone adds zone to backend."""
    new_zone = Mock(id=5)
    mock_system.current_security_manager.add_security_zone.return_value = new_zone
    mock_system.current_security_manager.security_zones = [new_zone]
    new_zone.area = Mock(up_left=(0, 0), down_right=(100, 100))
    
    security_zone_page.add_zone()
    
    mock_system.current_security_manager.add_security_zone.assert_called_once()


# ============================================================
# delete_zone Tests
# ============================================================

@patch('gui.gui_securityzone.system')
def test_delete_zone_does_nothing_if_no_selection(mock_system, security_zone_page):
    """Test delete_zone does nothing when no zone selected."""
    security_zone_page.selected_zone = None
    
    security_zone_page.delete_zone()
    
    mock_system.current_security_manager.remove_security_zone.assert_not_called()


@patch('gui.gui_securityzone.system')
def test_delete_zone_removes_from_backend(mock_system, security_zone_page):
    """Test delete_zone removes zone from backend."""
    security_zone_page.selected_zone = "Zone 3"
    security_zone_page.zone_icons = {Mock(): "Zone 3"}
    security_zone_page.zone_handles = {}
    mock_system.current_security_manager.security_zones = []
    
    security_zone_page.delete_zone()
    
    mock_system.current_security_manager.remove_security_zone.assert_called_once_with(3)


@patch('gui.gui_securityzone.system')
def test_delete_zone_clears_selection(mock_system, security_zone_page):
    """Test delete_zone clears selection after deletion."""
    security_zone_page.selected_zone = "Zone 1"
    security_zone_page.zone_icons = {Mock(): "Zone 1"}
    security_zone_page.zone_handles = {}
    mock_system.current_security_manager.security_zones = []
    
    security_zone_page.delete_zone()
    
    assert security_zone_page.selected_zone is None


# ============================================================
# toggle_zone Tests
# ============================================================

@patch('gui.gui_securityzone.system')
def test_toggle_zone_does_nothing_if_no_selection(mock_system, security_zone_page):
    """Test toggle_zone does nothing when no zone selected."""
    security_zone_page.selected_zone = None
    
    security_zone_page.toggle_zone()
    
    mock_system.current_security_manager.arm_security_zone.assert_not_called()
    mock_system.current_security_manager.disarm_security_zone.assert_not_called()


@patch('gui.gui_securityzone.system')
def test_toggle_zone_arms_disabled_zone(mock_system, security_zone_page):
    """Test toggle_zone arms a disabled zone."""
    security_zone_page.selected_zone = "Zone 2"
    security_zone_page.security_zones = {
        "Zone 2": {"enabled": False, "top_left": (0, 0), "bottom_right": (100, 100)}
    }
    mock_system.current_security_manager.security_zones = []
    
    security_zone_page.toggle_zone()
    
    mock_system.current_security_manager.arm_security_zone.assert_called_once_with(2)


@patch('gui.gui_securityzone.system')
def test_toggle_zone_disarms_enabled_zone(mock_system, security_zone_page):
    """Test toggle_zone disarms an enabled zone."""
    security_zone_page.selected_zone = "Zone 2"
    security_zone_page.security_zones = {
        "Zone 2": {"enabled": True, "top_left": (0, 0), "bottom_right": (100, 100)}
    }
    mock_system.current_security_manager.security_zones = []
    
    security_zone_page.toggle_zone()
    
    mock_system.current_security_manager.disarm_security_zone.assert_called_once_with(2)


# ============================================================
# Drag and Resize Tests
# ============================================================

def test_zone_dragging_sets_dragging_flag(security_zone_page):
    """Test zone_dragging sets dragging flag."""
    security_zone_page.selected_zone = "Zone A"
    
    # Create a mock rectangle
    mock_rect = security_zone_page.canvas.create_rectangle(50, 50, 150, 150)
    security_zone_page.zone_icons = {mock_rect: "Zone A"}
    security_zone_page.security_zones = {
        "Zone A": {"top_left": (50, 50), "bottom_right": (150, 150), "enabled": True}
    }
    
    event = Mock(x=100, y=100)
    security_zone_page.zone_dragging(event)
    
    assert security_zone_page.dragging is True


def test_stop_drag_resets_flag(security_zone_page):
    """Test stop_drag resets dragging flag."""
    security_zone_page.dragging = True
    
    security_zone_page.stop_drag(Mock())
    
    assert security_zone_page.dragging is False


def test_start_resize_sets_resizing_flag(security_zone_page):
    """Test start_resize sets resizing flag."""
    # Create a handle first
    handle = security_zone_page.canvas.create_rectangle(10, 10, 20, 20, fill="white")
    
    # Mock the event with proper canvas tag setup
    security_zone_page.canvas.addtag_withtag("current", handle)
    event = Mock()
    
    security_zone_page.start_resize(event)
    
    assert security_zone_page.resizing is True


def test_stop_resize_resets_flag(security_zone_page):
    """Test stop_resize resets resizing flag."""
    security_zone_page.resizing = True
    
    security_zone_page.stop_resize(Mock())
    
    assert security_zone_page.resizing is False
