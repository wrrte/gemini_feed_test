import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from gui.gui_login_page import LoginPage


# Use tk_root from conftest.py - no need to define root fixture

@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    controller = Mock()
    controller.menubar = Mock()
    controller.main_page_class = Mock()
    return controller


@pytest.fixture
def login_page(tk_root, mock_controller):
    """Create a LoginPage instance for testing."""
    return LoginPage(tk_root, mock_controller)


# ============================================================
# Initialization Tests
# ============================================================

def test_login_page_initializes_correctly(login_page):
    """Test that LoginPage initializes with correct widgets."""
    assert login_page.username_entry is not None
    assert login_page.password_entry is not None
    assert login_page.error_label is not None


def test_username_entry_has_validation(login_page):
    """Test that username entry has character limit validation."""
    # Try entering 11 characters (should be blocked)
    login_page.username_entry.insert(0, "12345678901")
    login_page.username_entry.update()
    
    # Should only have 10 characters due to validation
    assert len(login_page.username_entry.get()) <= 10


def test_password_entry_has_validation(login_page):
    """Test that password entry has character limit validation."""
    # Try entering 11 characters
    login_page.password_entry.insert(0, "12345678901")
    login_page.password_entry.update()
    
    # Should only have 10 characters
    assert len(login_page.password_entry.get()) <= 10


def test_password_entry_hides_input(login_page):
    """Test that password entry masks input with asterisks."""
    assert login_page.password_entry['show'] == '*'


# ============================================================
# Login Success Tests
# ============================================================

@patch('gui.gui_login_page.system')
def test_login_success_clears_error(mock_system, login_page, mock_controller):
    """Test successful login clears error label."""
    mock_system.login_manager.web_log_in.return_value = (True, "Success")
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "pass")
    
    login_page.login()
    
    assert login_page.error_label.cget("text") == ""


@patch('gui.gui_login_page.system')
def test_login_success_sets_menubar(mock_system, login_page, mock_controller):
    """Test successful login sets controller menubar."""
    mock_system.login_manager.web_log_in.return_value = (True, "Success")
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "pass")
    
    login_page.login()
    
    mock_controller.config.assert_called_once_with(menu=mock_controller.menubar)


@patch('gui.gui_login_page.system')
def test_login_success_shows_main_page(mock_system, login_page, mock_controller):
    """Test successful login navigates to main page."""
    mock_system.login_manager.web_log_in.return_value = (True, "Success")
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "pass")
    
    login_page.login()
    
    mock_controller.show_frame.assert_called_once_with(mock_controller.main_page_class)


@patch('gui.gui_login_page.system')
def test_login_calls_system_with_correct_credentials(mock_system, login_page, mock_controller):
    """Test login passes correct credentials to system."""
    mock_system.login_manager.web_log_in.return_value = (True, "Success")
    
    login_page.username_entry.insert(0, "testuser")
    login_page.password_entry.insert(0, "testpass")
    
    login_page.login()
    
    mock_system.login_manager.web_log_in.assert_called_once_with(
        "testuser", "testpass", "WEB_BROWSER"
    )


# ============================================================
# Login Failure Tests
# ============================================================

@patch('gui.gui_login_page.system')
def test_login_failure_shows_error_message(mock_system, login_page, mock_controller):
    """Test failed login displays error message."""
    error_msg = "Invalid credentials"
    mock_system.login_manager.web_log_in.return_value = (False, error_msg)
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "wrong")
    
    login_page.login()
    
    assert login_page.error_label.cget("text") == error_msg


@patch('gui.gui_login_page.system')
def test_login_failure_does_not_set_menubar(mock_system, login_page, mock_controller):
    """Test failed login does not set menubar."""
    mock_system.login_manager.web_log_in.return_value = (False, "Error")
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "wrong")
    
    login_page.login()
    
    mock_controller.config.assert_not_called()


@patch('gui.gui_login_page.system')
def test_login_failure_does_not_navigate(mock_system, login_page, mock_controller):
    """Test failed login does not navigate to main page."""
    mock_system.login_manager.web_log_in.return_value = (False, "Error")
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "wrong")
    
    login_page.login()
    
    mock_controller.show_frame.assert_not_called()


# ============================================================
# Edge Case Tests
# ============================================================

@patch('gui.gui_login_page.system')
def test_login_with_empty_username(mock_system, login_page, mock_controller):
    """Test login with empty username."""
    mock_system.login_manager.web_log_in.return_value = (False, "Username required")
    
    login_page.password_entry.insert(0, "pass")
    
    login_page.login()
    
    mock_system.login_manager.web_log_in.assert_called_once_with("", "pass", "WEB_BROWSER")


@patch('gui.gui_login_page.system')
def test_login_with_empty_password(mock_system, login_page, mock_controller):
    """Test login with empty password."""
    mock_system.login_manager.web_log_in.return_value = (False, "Password required")
    
    login_page.username_entry.insert(0, "user")
    
    login_page.login()
    
    mock_system.login_manager.web_log_in.assert_called_once_with("user", "", "WEB_BROWSER")


@patch('gui.gui_login_page.system')
def test_login_with_both_fields_empty(mock_system, login_page, mock_controller):
    """Test login with both fields empty."""
    mock_system.login_manager.web_log_in.return_value = (False, "Credentials required")
    
    login_page.login()
    
    mock_system.login_manager.web_log_in.assert_called_once_with("", "", "WEB_BROWSER")


@patch('gui.gui_login_page.system')
def test_login_with_maximum_length_inputs(mock_system, login_page, mock_controller):
    """Test login with maximum length username and password."""
    mock_system.login_manager.web_log_in.return_value = (True, "Success")
    
    max_username = "a" * 10
    max_password = "b" * 10
    
    login_page.username_entry.insert(0, max_username)
    login_page.password_entry.insert(0, max_password)
    
    login_page.login()
    
    mock_system.login_manager.web_log_in.assert_called_once_with(
        max_username, max_password, "WEB_BROWSER"
    )


@patch('gui.gui_login_page.system')
def test_login_with_whitespace_username(mock_system, login_page, mock_controller):
    """Test login preserves whitespace in username."""
    mock_system.login_manager.web_log_in.return_value = (True, "Success")
    
    login_page.username_entry.insert(0, " user ")
    login_page.password_entry.insert(0, "pass")
    
    login_page.login()
    
    # Should not strip whitespace
    mock_system.login_manager.web_log_in.assert_called_once_with(
        " user ", "pass", "WEB_BROWSER"
    )


# ============================================================
# Validation Tests
# ============================================================

def test_validation_allows_empty_string(login_page):
    """Test validation allows clearing the field."""
    login_page.username_entry.insert(0, "test")
    login_page.username_entry.delete(0, tk.END)
    
    assert login_page.username_entry.get() == ""


def test_validation_blocks_11th_character_username(login_page):
    """Test validation blocks 11th character in username."""
    login_page.username_entry.insert(0, "1234567890")  # 10 chars
    login_page.username_entry.insert(tk.END, "X")      # Try to add 11th
    login_page.username_entry.update()
    
    assert len(login_page.username_entry.get()) == 10


def test_validation_blocks_11th_character_password(login_page):
    """Test validation blocks 11th character in password."""
    login_page.password_entry.insert(0, "1234567890")  # 10 chars
    login_page.password_entry.insert(tk.END, "X")      # Try to add 11th
    login_page.password_entry.update()
    
    assert len(login_page.password_entry.get()) == 10


# ============================================================
# Multiple Login Attempt Tests
# ============================================================

@patch('gui.gui_login_page.system')
def test_multiple_failed_login_attempts(mock_system, login_page, mock_controller):
    """Test multiple failed login attempts update error each time."""
    mock_system.login_manager.web_log_in.side_effect = [
        (False, "Error 1"),
        (False, "Error 2"),
        (False, "Error 3")
    ]
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "wrong1")
    login_page.login()
    assert login_page.error_label.cget("text") == "Error 1"
    
    login_page.password_entry.delete(0, tk.END)
    login_page.password_entry.insert(0, "wrong2")
    login_page.login()
    assert login_page.error_label.cget("text") == "Error 2"
    
    login_page.password_entry.delete(0, tk.END)
    login_page.password_entry.insert(0, "wrong3")
    login_page.login()
    assert login_page.error_label.cget("text") == "Error 3"


@patch('gui.gui_login_page.system')
def test_success_after_failed_attempt(mock_system, login_page, mock_controller):
    """Test successful login after failed attempt clears error."""
    mock_system.login_manager.web_log_in.side_effect = [
        (False, "Invalid credentials"),
        (True, "Success")
    ]
    
    login_page.username_entry.insert(0, "user")
    login_page.password_entry.insert(0, "wrong")
    login_page.login()
    assert login_page.error_label.cget("text") == "Invalid credentials"
    
    login_page.password_entry.delete(0, tk.END)
    login_page.password_entry.insert(0, "correct")
    login_page.login()
    assert login_page.error_label.cget("text") == ""
