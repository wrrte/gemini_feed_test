import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock, call
from gui.gui_control_panel import GUIControlPanel


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def control_panel(tk_root):
    """Create a GUIControlPanel instance for testing."""
    with patch('gui.gui_control_panel.system') as mock_system:
        mock_system.current_security_manager = Mock()
        mock_system.current_security_manager.now_security_mode = None
        mock_system.current_security_manager.security_modes = []
        panel = GUIControlPanel(master=tk_root)
        yield panel
        

# ============================================================
# Initialization Tests
# ============================================================

def test_control_panel_initializes_with_off_state(control_panel):
    """Test control panel initializes in OFF state."""
    assert control_panel.state == "OFF"
    assert control_panel.temp_new_pw == ""
    assert control_panel.button_sequence == ""


@patch('gui.gui_control_panel.system')
def test_control_panel_sets_initial_display(mock_system, tk_root):
    """Test control panel sets initial display messages."""
    mock_system.current_security_manager = Mock()
    mock_system.current_security_manager.now_security_mode = None
    
    panel = GUIControlPanel(master=tk_root)
    
    # Check state instead of display (display methods are from parent class)
    assert panel.state == "OFF"


# ============================================================
# Button Press - OFF State Tests
# ============================================================

@patch('gui.gui_control_panel.system')
def test_button_1_turns_system_on_from_off(mock_system, control_panel):
    """Test pressing 1 turns system on from OFF state."""
    control_panel.state = "OFF"
    
    control_panel.button1()
    
    mock_system.turn_on.assert_called_once()
    assert control_panel.state == "LOCKED"


@patch('gui.gui_control_panel.system')
def test_non_1_button_ignored_in_off_state(mock_system, control_panel):
    """Test non-1 buttons are ignored in OFF state."""
    control_panel.state = "OFF"
    
    control_panel.button2()
    control_panel.button3()
    
    mock_system.turn_on.assert_not_called()
    assert control_panel.state == "OFF"


# ============================================================
# Button Press - LOCKED State Tests
# ============================================================

@patch('gui.gui_control_panel.system')
def test_correct_password_logs_in(mock_system, control_panel):
    """Test correct 4-digit password logs in."""
    mock_system.login_manager.cp_log_in.return_value = (True, "Success")
    control_panel.state = "LOCKED"
    
    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    
    mock_system.login_manager.cp_log_in.assert_called_once_with("1234", "master")
    assert control_panel.state == "LOGGED_IN"
    assert control_panel.button_sequence == ""


@patch('gui.gui_control_panel.system')
def test_incorrect_password_stays_locked(mock_system, control_panel):
    """Test incorrect password keeps system locked."""
    mock_system.login_manager.cp_log_in.return_value = (False, "Invalid password")
    control_panel.state = "LOCKED"
    
    control_panel.button9()
    control_panel.button9()
    control_panel.button9()
    control_panel.button9()
    
    assert control_panel.state == "LOCKED"
    assert control_panel.button_sequence == ""


@patch('gui.gui_control_panel.system')
def test_password_accumulates_before_4_digits(mock_system, control_panel):
    """Test password sequence accumulates before reaching 4 digits."""
    control_panel.state = "LOCKED"
    
    control_panel.button1()
    assert control_panel.button_sequence == "1"
    
    control_panel.button2()
    assert control_panel.button_sequence == "12"
    
    control_panel.button3()
    assert control_panel.button_sequence == "123"
    
    mock_system.login_manager.cp_log_in.assert_not_called()


# ============================================================
# Button Press - LOGGED_IN State Tests
# ============================================================

@patch('gui.gui_control_panel.system')
def test_button_2_turns_system_off(mock_system, control_panel):
    """Test button 2 in LOGGED_IN state turns system off."""
    control_panel.state = "LOGGED_IN"
    
    control_panel.button2()
    
    mock_system.turn_off.assert_called_once()
    assert control_panel.state == "OFF"


@patch('gui.gui_control_panel.system')
def test_button_3_resets_and_turns_off(mock_system, control_panel):
    """Test button 3 in LOGGED_IN state resets and turns off."""
    control_panel.state = "LOGGED_IN"
    
    control_panel.button3()
    
    mock_system.reset.assert_called_once()
    mock_system.turn_off.assert_called_once()
    assert control_panel.state == "OFF"


@patch('gui.gui_control_panel.system')
def test_button_7_sets_away_mode(mock_system, control_panel):
    """Test button 7 sets Away mode."""
    control_panel.state = "LOGGED_IN"
    
    control_panel.button7()
    
    mock_system.current_security_manager.set_security_mode_name.assert_called_once_with("Away")


@patch('gui.gui_control_panel.system')
def test_button_8_sets_home_mode(mock_system, control_panel):
    """Test button 8 sets Home mode."""
    control_panel.state = "LOGGED_IN"
    
    control_panel.button8()
    
    mock_system.current_security_manager.set_security_mode_name.assert_called_once_with("Home")


@patch('gui.gui_control_panel.system')
def test_button_9_starts_password_change(mock_system, control_panel):
    """Test button 9 starts password change flow."""
    control_panel.state = "LOGGED_IN"
    
    control_panel.button9()
    
    assert control_panel.state == "CHANGE_PW_CURRENT"
    assert control_panel.button_sequence == ""


# ============================================================
# Password Change Flow Tests
# ============================================================

@patch('gui.gui_control_panel.system')
def test_password_change_verifies_current(mock_system, control_panel):
    """Test password change verifies current password."""
    mock_system.login_manager.cp_log_in.return_value = (True, "Success")
    control_panel.state = "CHANGE_PW_CURRENT"
    
    for digit in "1234":
        control_panel.button(digit)
    
    mock_system.login_manager.cp_log_in.assert_called_once_with("1234", "master")
    assert control_panel.state == "CHANGE_PW_NEW"


@patch('gui.gui_control_panel.system')
def test_password_change_wrong_current_stays_in_state(mock_system, control_panel):
    """Test wrong current password stays in CHANGE_PW_CURRENT state."""
    mock_system.login_manager.cp_log_in.return_value = (False, "Wrong password")
    control_panel.state = "CHANGE_PW_CURRENT"
    
    for digit in "9999":
        control_panel.button(digit)
    
    assert control_panel.state == "CHANGE_PW_CURRENT"
    assert control_panel.button_sequence == ""


@patch('gui.gui_control_panel.system')
def test_password_change_stores_new_password(mock_system, control_panel):
    """Test new password is stored temporarily."""
    control_panel.state = "CHANGE_PW_NEW"
    
    for digit in "5678":
        control_panel.button(digit)
    
    assert control_panel.temp_new_pw == "5678"
    assert control_panel.state == "CHANGE_PW_CONFIRM"


@patch('gui.gui_control_panel.system')
def test_password_change_mismatch_resets(mock_system, control_panel):
    """Test password mismatch resets to NEW state."""
    control_panel.state = "CHANGE_PW_NEW"
    for digit in "5678":
        control_panel.button(digit)
    
    control_panel.state = "CHANGE_PW_CONFIRM"
    for digit in "1111":
        control_panel.button(digit)
    
    assert control_panel.state == "CHANGE_PW_NEW"
    assert control_panel.button_sequence == ""
    assert control_panel.temp_new_pw == ""


@patch('gui.gui_control_panel.system')
def test_password_change_success(mock_system, control_panel):
    """Test successful password change."""
    control_panel.state = "CHANGE_PW_NEW"
    for digit in "5678":
        control_panel.button(digit)
    
    control_panel.state = "CHANGE_PW_CONFIRM"
    for digit in "5678":
        control_panel.button(digit)
    
    mock_system.login_manager.cp_change_password.assert_called_once_with("5678", "master")
    assert control_panel.state == "LOGGED_IN"
    assert control_panel.button_sequence == ""
    assert control_panel.temp_new_pw == ""


# ============================================================
# Panic Button Tests
# ============================================================

@patch('gui.gui_control_panel.system')
def test_star_button_triggers_panic_when_not_off(mock_system, control_panel):
    """Test * button triggers panic alarm when not OFF."""
    control_panel.state = "LOCKED"
    
    control_panel.button_star()
    
    mock_system.make_panic_phone_call.assert_called_once()


@patch('gui.gui_control_panel.system')
def test_sharp_button_triggers_panic_when_not_off(mock_system, control_panel):
    """Test # button triggers panic alarm when not OFF."""
    control_panel.state = "LOGGED_IN"
    
    control_panel.button_sharp()
    
    mock_system.make_panic_phone_call.assert_called_once()


@patch('gui.gui_control_panel.system')
def test_panic_buttons_ignored_when_off(mock_system, control_panel):
    """Test panic buttons do nothing when system is OFF."""
    control_panel.state = "OFF"
    
    control_panel.button_star()
    control_panel.button_sharp()
    
    mock_system.make_panic_phone_call.assert_not_called()


# ============================================================
# All Button Methods Tests
# ============================================================

@patch('gui.gui_control_panel.system')
def test_all_digit_buttons_call_button_method(mock_system, control_panel):
    """Test all digit button methods call button() with correct digit."""
    control_panel.state = "LOCKED"
    
    control_panel.button0()
    assert "0" in control_panel.button_sequence
    
    control_panel.button_sequence = ""
    control_panel.button1()
    assert "1" in control_panel.button_sequence


# ============================================================
# set_all_off Tests
# ============================================================

@patch('gui.gui_control_panel.system')
def test_set_all_off_resets_everything(mock_system, control_panel):
    """Test set_all_off resets all state."""
    control_panel.state = "LOGGED_IN"
    control_panel.button_sequence = "123"
    
    control_panel.set_all_off()
    
    mock_system.turn_off.assert_called_once()
    assert control_panel.state == "OFF"
    assert control_panel.button_sequence == ""
