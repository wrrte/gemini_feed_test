import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from gui.gui_securitymode import SecurityModePage


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    return Mock()


@pytest.fixture
def security_mode_page(tk_root, mock_controller):
    """Create a SecurityModePage instance."""
    with patch('gui.gui_securitymode.system') as mock_system:
        mock_system.current_security_manager.sensors.keys.return_value = []
        mock_system.current_security_manager.now_security_mode = None
        mock_system.current_security_manager.update.return_value = None
        mock_system.current_control_panel = None
        page = SecurityModePage(tk_root, mock_controller)
        yield page


# ============================================================
# Initialization Tests
# ============================================================

def test_security_mode_page_initializes(security_mode_page):
    """Test SecurityModePage initializes correctly."""
    assert security_mode_page.controller is not None
    assert security_mode_page.canvas is not None
    assert security_mode_page.sensors is not None


def test_security_mode_page_has_mode_buttons(security_mode_page):
    """Test SecurityModePage creates mode buttons."""
    assert len(security_mode_page.mode_buttons) == 4
    assert "Home" in security_mode_page.mode_buttons
    assert "Away" in security_mode_page.mode_buttons
    assert "Overnight" in security_mode_page.mode_buttons
    assert "Extended" in security_mode_page.mode_buttons


def test_security_mode_page_initializes_current_mode_none(security_mode_page):
    """Test SecurityModePage initializes with no current mode."""
    assert security_mode_page.current_mode is None


@patch('gui.gui_securitymode.system')
def test_security_mode_page_loads_existing_mode(mock_system, tk_root, mock_controller):
    """Test SecurityModePage loads existing security mode."""
    mock_mode = Mock()
    mock_mode.name = "Away"  # Set name as attribute, not Mock
    mock_system.current_security_manager.now_security_mode = 1
    mock_system.current_security_manager.security_modes = [Mock(), mock_mode]
    mock_system.current_security_manager.sensors.keys.return_value = []
    mock_system.current_security_manager.update.return_value = None
    mock_system.current_control_panel = None
    
    page = SecurityModePage(tk_root, mock_controller)
    
    # Should have called select_mode with "Away"
    assert page.current_mode == "Away"


# ============================================================
# refresh_sensor_states Tests
# ============================================================

@patch('gui.gui_securitymode.system')
def test_refresh_sensor_states_updates_sensor_colors(mock_system, security_mode_page):
    """Test refresh_sensor_states updates sensor GUI states."""
    sensor = Mock(armed=True)
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    security_mode_page.refresh_sensor_states()
    
    mock_system.current_security_manager.update.assert_called_once()


@patch('gui.gui_securitymode.system')
def test_refresh_sensor_states_syncs_armed_state(mock_system, security_mode_page):
    """Test refresh_sensor_states syncs armed state from backend."""
    sensor1 = Mock(armed=True)
    sensor2 = Mock(armed=False)
    mock_system.current_security_manager.sensors.keys.return_value = [sensor1, sensor2]
    
    security_mode_page.refresh_sensor_states()
    
    # Should have updated GUI sensor states
    assert security_mode_page.sensors["Sensor 1"]["enabled"] == True
    assert security_mode_page.sensors["Sensor 2"]["enabled"] == False


# ============================================================
# sensor_clicked Tests
# ============================================================

@patch('gui.gui_securitymode.system')
def test_sensor_clicked_toggles_armed_state(mock_system, security_mode_page):
    """Test clicking sensor toggles its armed state."""
    sensor = Mock(armed=False)
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    # Simulate click on first sensor
    event = Mock()
    security_mode_page.canvas.addtag_withtag = Mock()
    security_mode_page.canvas.find_withtag = Mock(return_value=[list(security_mode_page.sensor_icons.keys())[0]])
    
    security_mode_page.sensor_clicked(event)
    
    mock_system.current_security_manager.set_arm.assert_called_once()


# ============================================================
# select_mode Tests
# ============================================================

@patch('gui.gui_securitymode.system')
def test_select_mode_updates_current_mode(mock_system, security_mode_page):
    """Test select_mode updates current_mode variable."""
    security_mode_page.select_mode("Home")
    
    assert security_mode_page.current_mode == "Home"


@patch('gui.gui_securitymode.system')
def test_select_mode_calls_backend(mock_system, security_mode_page):
    """Test select_mode calls backend to set mode."""
    security_mode_page.select_mode("Away")
    
    mock_system.current_security_manager.set_security_mode_name.assert_called_once_with("Away")


@patch('gui.gui_securitymode.system')
def test_select_mode_updates_button_appearance(mock_system, security_mode_page):
    """Test select_mode changes button appearance."""
    security_mode_page.select_mode("Home")
    
    # Selected button should be sunken
    assert security_mode_page.mode_buttons["Home"]["relief"] == "sunken"
    # Others should be raised
    assert security_mode_page.mode_buttons["Away"]["relief"] == "raised"


@patch('gui.gui_securitymode.system')
def test_select_mode_home_updates_control_panel(mock_system, security_mode_page):
    """Test selecting Home mode updates control panel display."""
    mock_panel = Mock()
    mock_system.current_control_panel = mock_panel
    
    security_mode_page.select_mode("Home")
    
    mock_panel.set_display_stay.assert_called_with(True)
    mock_panel.set_display_away.assert_called_with(False)


@patch('gui.gui_securitymode.system')
def test_select_mode_away_updates_control_panel(mock_system, security_mode_page):
    """Test selecting Away mode updates control panel display."""
    mock_panel = Mock()
    mock_system.current_control_panel = mock_panel
    
    security_mode_page.select_mode("Away")
    
    mock_panel.set_display_stay.assert_called_with(False)
    mock_panel.set_display_away.assert_called_with(True)


@patch('gui.gui_securitymode.system')
def test_select_mode_other_clears_control_panel(mock_system, security_mode_page):
    """Test selecting other modes clears control panel indicators."""
    mock_panel = Mock()
    mock_system.current_control_panel = mock_panel
    
    security_mode_page.select_mode("Overnight")
    
    mock_panel.set_display_stay.assert_called_with(False)
    mock_panel.set_display_away.assert_called_with(False)


# ============================================================
# save_current_mode Tests
# ============================================================

@patch('gui.gui_securitymode.system')
def test_save_current_mode_does_nothing_if_no_mode(mock_system, security_mode_page):
    """Test save_current_mode does nothing when no mode selected."""
    security_mode_page.current_mode = None
    
    security_mode_page.save_current_mode()
    
    mock_system.current_security_manager.update_security_mode.assert_not_called()


@patch('gui.gui_securitymode.system')
def test_save_current_mode_saves_armed_sensors(mock_system, security_mode_page):
    """Test save_current_mode saves only armed sensors."""
    security_mode_page.current_mode = "Home"
    sensor1 = Mock(armed=True)
    sensor2 = Mock(armed=False)
    sensor3 = Mock(armed=True)
    mock_system.current_security_manager.sensors.keys.return_value = [sensor1, sensor2, sensor3]
    
    security_mode_page.save_current_mode()
    
    # Should save only armed sensors (sensor1, sensor3)
    call_args = mock_system.current_security_manager.update_security_mode.call_args
    assert call_args[0][0] == "Home"
    saved_sensors = call_args[0][1]
    assert sensor1 in saved_sensors
    assert sensor2 not in saved_sensors
    assert sensor3 in saved_sensors


@patch('gui.gui_securitymode.system')
def test_save_current_mode_resets_manual_arms(mock_system, security_mode_page):
    """Test save_current_mode resets all manual arm flags to None."""
    security_mode_page.current_mode = "Away"
    sensor1 = Mock(armed=True)
    sensor2 = Mock(armed=False)
    mock_system.current_security_manager.sensors.keys.return_value = [sensor1, sensor2]
    
    security_mode_page.save_current_mode()
    
    # Should call set_arm with None for all sensors
    assert mock_system.current_security_manager.set_arm.call_count == 2


# ============================================================
# arm_all Tests
# ============================================================

@patch('gui.gui_securitymode.system')
def test_arm_all_arms_all_sensors(mock_system, security_mode_page):
    """Test arm_all arms all sensors."""
    sensor1 = Mock()
    sensor2 = Mock()
    sensor3 = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor1, sensor2, sensor3]
    
    security_mode_page.arm_all()
    
    assert mock_system.current_security_manager.arm.call_count == 3


# ============================================================
# disarm_all Tests
# ============================================================

@patch('gui.gui_securitymode.system')
def test_disarm_all_disarms_all_sensors(mock_system, security_mode_page):
    """Test disarm_all disarms all sensors."""
    sensor1 = Mock()
    sensor2 = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor1, sensor2]
    
    security_mode_page.disarm_all()
    
    assert mock_system.current_security_manager.disarm.call_count == 2


# ============================================================
# default_all Tests
# ============================================================

@patch('gui.gui_securitymode.system')
def test_default_all_sets_all_to_none(mock_system, security_mode_page):
    """Test default_all sets all sensors to None (mode default)."""
    sensor1 = Mock()
    sensor2 = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor1, sensor2]
    
    security_mode_page.default_all()
    
    # Should call set_arm with None for each sensor
    calls = mock_system.current_security_manager.set_arm.call_args_list
    assert len(calls) == 2
    assert all(call[0][1] is None for call in calls)


# ============================================================
# log Tests
# ============================================================

def test_log_updates_message_label(security_mode_page):
    """Test log method updates message label."""
    security_mode_page.log("Test message")
    
    assert security_mode_page.message_label.cget("text") == "Test message"
