import pytest
import tkinter as tk
from unittest.mock import Mock, patch
from gui.gui_sensorintruder import GUISensorIntruder


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def sensor_intruder(tk_root):
    """Create a GUISensorIntruder instance."""
    with patch('gui.gui_sensorintruder.system') as mock_system:
        mock_system.current_security_manager.sensors.keys.return_value = []
        gui = GUISensorIntruder(master=tk_root)
        yield gui


# ============================================================
# Initialization Tests
# ============================================================

def test_sensor_intruder_initializes(sensor_intruder):
    """Test GUISensorIntruder initializes correctly."""
    assert sensor_intruder.title() == "Sensor Tester"
    assert sensor_intruder.buttons is not None
    assert sensor_intruder.status is not None


def test_sensor_intruder_creates_10_buttons(sensor_intruder):
    """Test GUISensorIntruder creates 10 sensor buttons."""
    assert len(sensor_intruder.buttons) == 10


def test_sensor_intruder_buttons_start_with_trigger_text(sensor_intruder):
    """Test buttons initially say 'Trigger Sensor'."""
    for i, button in enumerate(sensor_intruder.buttons):
        assert button.cget("text") == f"Trigger Sensor {i+1}"


# ============================================================
# toggle_sensor Tests - Trigger Action
# ============================================================

@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_triggers_sensor(mock_system, sensor_intruder):
    """Test toggle_sensor calls intrude() on sensor."""
    sensor = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    sensor_intruder.toggle_sensor(0)
    
    sensor.intrude.assert_called_once()


@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_updates_button_text_to_release(mock_system, sensor_intruder):
    """Test triggering sensor changes button text to 'Release'."""
    sensor = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    sensor_intruder.toggle_sensor(0)
    
    assert sensor_intruder.buttons[0].cget("text") == "Release Sensor 1"


@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_updates_status_label(mock_system, sensor_intruder):
    """Test triggering sensor updates status label."""
    sensor = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    sensor_intruder.toggle_sensor(0)
    
    assert "Triggered sensor #1" in sensor_intruder.status.cget("text")


# ============================================================
# toggle_sensor Tests - Release Action
# ============================================================

@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_releases_sensor(mock_system, sensor_intruder):
    """Test toggle_sensor calls release() when already triggered."""
    sensor = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    # First trigger
    sensor_intruder.toggle_sensor(0)
    sensor.intrude.assert_called_once()
    
    # Then release
    sensor_intruder.toggle_sensor(0)
    sensor.release.assert_called_once()


@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_updates_button_text_back_to_trigger(mock_system, sensor_intruder):
    """Test releasing sensor changes button text back to 'Trigger'."""
    sensor = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    # Trigger then release
    sensor_intruder.toggle_sensor(0)
    sensor_intruder.toggle_sensor(0)
    
    assert sensor_intruder.buttons[0].cget("text") == "Trigger Sensor 1"


@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_release_updates_status(mock_system, sensor_intruder):
    """Test releasing sensor updates status label."""
    sensor = Mock()
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    # Trigger then release
    sensor_intruder.toggle_sensor(0)
    sensor_intruder.toggle_sensor(0)
    
    assert "Released sensor #1" in sensor_intruder.status.cget("text")


# ============================================================
# Multiple Sensors Tests
# ============================================================

@patch('gui.gui_sensorintruder.system')
def test_toggle_multiple_sensors_independently(mock_system, sensor_intruder):
    """Test multiple sensors can be triggered independently."""
    sensors = [Mock() for _ in range(10)]
    mock_system.current_security_manager.sensors.keys.return_value = sensors
    
    sensor_intruder.toggle_sensor(0)
    sensor_intruder.toggle_sensor(5)
    
    sensors[0].intrude.assert_called_once()
    sensors[5].intrude.assert_called_once()
    assert sensor_intruder.buttons[0].cget("text") == "Release Sensor 1"
    assert sensor_intruder.buttons[5].cget("text") == "Release Sensor 6"


# ============================================================
# Error Handling Tests
# ============================================================

@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_handles_exception(mock_system, sensor_intruder):
    """Test toggle_sensor handles exceptions gracefully."""
    sensor = Mock()
    sensor.intrude.side_effect = Exception("Test error")
    mock_system.current_security_manager.sensors.keys.return_value = [sensor]
    
    sensor_intruder.toggle_sensor(0)
    
    # Should show error in status
    assert "Error" in sensor_intruder.status.cget("text")
    assert sensor_intruder.status.cget("fg") == "red"


@patch('gui.gui_sensorintruder.system')
def test_toggle_sensor_out_of_range_index(mock_system, sensor_intruder):
    """Test toggle_sensor handles out of range index."""
    sensors = [Mock() for _ in range(5)]
    mock_system.current_security_manager.sensors.keys.return_value = sensors
    
    # Try to toggle sensor 10 when only 5 exist
    sensor_intruder.toggle_sensor(9)
    
    # Should show error
    assert "Error" in sensor_intruder.status.cget("text")


# ============================================================
# All Sensors Tests
# ============================================================

@patch('gui.gui_sensorintruder.system')
def test_all_10_buttons_work(mock_system, sensor_intruder):
    """Test all 10 sensor buttons work correctly."""
    sensors = [Mock() for _ in range(10)]
    mock_system.current_security_manager.sensors.keys.return_value = sensors
    
    for i in range(10):
        sensor_intruder.toggle_sensor(i)
    
    # All sensors should be triggered
    for sensor in sensors:
        sensor.intrude.assert_called_once()
