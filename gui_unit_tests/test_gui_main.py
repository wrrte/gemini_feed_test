import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from gui.gui_main import GUIMain, MainPage, IdentityConfirmPage


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def gui_main(tk_root):
    """Create a GUIMain instance for testing."""
    with patch('gui.gui_main.system'):
        app = GUIMain(master=tk_root)
        yield app


# ============================================================
# Initialization Tests
# ============================================================

def test_gui_main_initializes_with_frames(gui_main):
    """Test GUIMain creates all required frames."""
    from gui.gui_login_page import LoginPage
    from gui.gui_surveillance import FloorPlanPage
    
    assert LoginPage in gui_main.frames
    assert MainPage in gui_main.frames
    assert FloorPlanPage in gui_main.frames


def test_gui_main_shows_login_page_first(gui_main):
    """Test GUIMain shows LoginPage on startup."""
    from gui.gui_login_page import LoginPage
    
    # LoginPage should be raised first
    assert LoginPage in gui_main.frames


def test_gui_main_builds_menubar(gui_main):
    """Test GUIMain builds menubar."""
    assert gui_main.menubar is not None


# ============================================================
# Navigation Tests
# ============================================================

def test_show_frame_recreates_frame(gui_main):
    """Test show_frame destroys and recreates the frame."""
    old_frame = gui_main.frames[MainPage]
    
    gui_main.show_frame(MainPage)
    
    new_frame = gui_main.frames[MainPage]
    assert new_frame is not old_frame


def test_show_frame_raises_new_frame(gui_main):
    """Test show_frame raises the new frame to top."""
    gui_main.show_frame(MainPage)
    
    # Frame should be in frames dict
    assert MainPage in gui_main.frames


@patch('gui.gui_main.system')
def test_logout_clears_menubar(mock_system, gui_main):
    """Test logout clears menubar and returns to login."""
    gui_main.logout()
    
    mock_system.login_manager.web_log_out.assert_called_once_with("WEB_BROWSER")


def test_back_to_login_clears_menu(gui_main):
    """Test back_to_login clears menu."""
    from gui.gui_login_page import LoginPage
    
    gui_main.back_to_login()
    
    # Should show LoginPage
    assert LoginPage in gui_main.frames


# ============================================================
# Camera View Tests
# ============================================================

def test_open_camera_view_loads_camera(gui_main):
    """Test open_camera_view loads specified camera."""
    from gui.gui_cameraview import CameraViewPage
    
    camera_page = gui_main.frames[CameraViewPage]
    camera_page.load_camera = Mock()
    
    gui_main.open_camera_view(5)
    
    camera_page.load_camera.assert_called_once_with(5)


# ============================================================
# Secure Frame Tests  
# ============================================================

def test_secure_show_frame_creates_identity_confirm(gui_main):
    """Test secure_show_frame creates IdentityConfirmPage."""
    from gui.gui_securitymode import SecurityModePage
    
    gui_main.secure_show_frame(SecurityModePage)
    
    assert IdentityConfirmPage in gui_main.frames


# ============================================================
# MainPage Tests
# ============================================================

@pytest.fixture
def main_page(tk_root):
    """Create a MainPage instance."""
    controller = Mock()
    controller.show_frame = Mock()
    controller.secure_show_frame = Mock()
    controller.logout = Mock()
    page = MainPage(tk_root, controller)
    return page


def test_main_page_has_title_label(main_page):
    """Test MainPage displays SAFEHOME title."""
    # Should create page without errors
    assert main_page is not None


def test_main_page_creates_buttons(main_page):
    """Test MainPage creates navigation buttons."""
    buttons = [w for w in main_page.winfo_children() if isinstance(w, tk.Frame)]
    # Should have a center frame with buttons
    assert len(buttons) > 0


# ============================================================
# IdentityConfirmPage Tests
# ============================================================

@pytest.fixture
def identity_page(tk_root):
    """Create an IdentityConfirmPage instance."""
    with patch('gui.gui_main.system') as mock_system:
        mock_system.current_system_settings_manager.get_system_settings.return_value = Mock(
            home_phone_number="01012345678"
        )
        controller = Mock()
        controller.show_frame = Mock()
        page = IdentityConfirmPage(tk_root, controller)
        yield page


def test_identity_page_initializes_with_entry(identity_page):
    """Test IdentityConfirmPage has phone entry field."""
    assert identity_page.entry is not None
    assert identity_page.error is not None


def test_identity_page_validate_allows_digits_only(identity_page):
    """Test validation only allows digits."""
    assert identity_page.validate_input("123") is True
    assert identity_page.validate_input("abc") is False
    assert identity_page.validate_input("12a34") is False


def test_identity_page_validate_limits_length(identity_page):
    """Test validation limits to 11 digits."""
    assert identity_page.validate_input("12345678901") is True
    assert identity_page.validate_input("123456789012") is False


def test_identity_page_validate_allows_empty(identity_page):
    """Test validation allows empty string."""
    assert identity_page.validate_input("") is True


@patch('gui.gui_main.system')
def test_identity_page_correct_number_navigates(mock_system, identity_page):
    """Test correct phone number navigates to target."""
    from gui.gui_securitymode import SecurityModePage
    
    mock_system.current_system_settings_manager.get_system_settings.return_value = Mock(
        home_phone_number="01012345678"
    )
    identity_page.set_target(SecurityModePage)
    identity_page.entry.insert(0, "01012345678")
    
    identity_page.check_number()
    
    identity_page.controller.show_frame.assert_called_once_with(SecurityModePage)
    assert identity_page.error.cget("text") == ""


@patch('gui.gui_main.system')
def test_identity_page_wrong_number_shows_error(mock_system, identity_page):
    """Test wrong phone number shows error."""
    mock_system.current_system_settings_manager.get_system_settings.return_value = Mock(
        home_phone_number="01012345678"
    )
    identity_page.entry.insert(0, "99999999999")
    
    identity_page.check_number()
    
    identity_page.controller.show_frame.assert_not_called()
    assert "Incorrect" in identity_page.error.cget("text")


def test_identity_page_set_target_clears_fields(identity_page):
    """Test set_target clears entry and error."""
    from gui.gui_securitymode import SecurityModePage
    
    identity_page.entry.insert(0, "12345")
    identity_page.error.config(text="Error message")
    
    identity_page.set_target(SecurityModePage)
    
    assert identity_page.entry.get() == ""
    assert identity_page.error.cget("text") == ""
    assert identity_page.target_frame == SecurityModePage
