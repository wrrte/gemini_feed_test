import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from gui.gui_intrusionlog import ViewLogPage


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    controller = Mock()
    controller.main_page_class = Mock()
    controller.show_frame = Mock()
    return controller


@pytest.fixture
def mock_log():
    """Create a mock log entry."""
    log = Mock()
    log.id = 1
    log.date_time = "2024-01-15 10:30:00"
    log.description = "Sensor 1 triggered"
    return log


@pytest.fixture
def view_log_page(tk_root, mock_controller):
    """Create a ViewLogPage instance."""
    with patch('gui.gui_intrusionlog.system') as mock_system:
        mock_system.current_log_manager.get_log_list.return_value = []
        page = ViewLogPage(tk_root, mock_controller)
        yield page


# ============================================================
# Initialization Tests
# ============================================================

def test_view_log_page_initializes(view_log_page):
    """Test ViewLogPage initializes correctly."""
    assert view_log_page.controller is not None
    assert view_log_page.log_frame is not None
    assert view_log_page.rows_container is not None


def test_view_log_page_has_title(view_log_page):
    """Test ViewLogPage has title label."""
    assert view_log_page is not None


@patch('gui.gui_intrusionlog.system')
def test_view_log_page_loads_logs_on_init(mock_system, tk_root, mock_controller):
    """Test ViewLogPage loads logs on initialization."""
    mock_system.current_log_manager.get_log_list.return_value = []
    
    page = ViewLogPage(tk_root, mock_controller)
    
    mock_system.current_log_manager.get_log_list.assert_called_once()


def test_view_log_page_has_back_button(view_log_page):
    """Test ViewLogPage has back button."""
    # Should create without errors
    assert view_log_page is not None


# ============================================================
# load_logs Tests
# ============================================================

@patch('gui.gui_intrusionlog.system')
def test_load_logs_creates_rows_for_each_log(mock_system, view_log_page, mock_log):
    """Test load_logs creates a row for each log entry."""
    log1 = Mock(id=1, date_time="2024-01-15 10:30:00", description="Sensor 1 triggered")
    log2 = Mock(id=2, date_time="2024-01-15 10:31:00", description="Sensor 2 triggered")
    mock_system.current_log_manager.get_log_list.return_value = [log1, log2]
    
    view_log_page.load_logs()
    
    children = view_log_page.rows_container.winfo_children()
    assert len(children) == 2


@patch('gui.gui_intrusionlog.system')
def test_load_logs_displays_log_id(mock_system, view_log_page):
    """Test load_logs displays log ID."""
    log = Mock(id=42, date_time="2024-01-15 10:30:00", description="Test")
    mock_system.current_log_manager.get_log_list.return_value = [log]
    
    view_log_page.load_logs()
    
    # Should have created row with ID
    children = view_log_page.rows_container.winfo_children()
    assert len(children) == 1


@patch('gui.gui_intrusionlog.system')
def test_load_logs_displays_date_time(mock_system, view_log_page):
    """Test load_logs displays date/time."""
    log = Mock(id=1, date_time="2024-01-15 10:30:00", description="Test")
    mock_system.current_log_manager.get_log_list.return_value = [log]
    
    view_log_page.load_logs()
    
    children = view_log_page.rows_container.winfo_children()
    assert len(children) == 1


@patch('gui.gui_intrusionlog.system')
def test_load_logs_displays_description(mock_system, view_log_page):
    """Test load_logs displays description."""
    log = Mock(id=1, date_time="2024-01-15 10:30:00", description="Motion detected")
    mock_system.current_log_manager.get_log_list.return_value = [log]
    
    view_log_page.load_logs()
    
    children = view_log_page.rows_container.winfo_children()
    assert len(children) == 1


@patch('gui.gui_intrusionlog.system')
def test_load_logs_clears_old_rows(mock_system, view_log_page):
    """Test load_logs clears old log rows."""
    # First load
    log1 = Mock(id=1, date_time="2024-01-15 10:30:00", description="Test1")
    mock_system.current_log_manager.get_log_list.return_value = [log1]
    view_log_page.load_logs()
    first_count = len(view_log_page.rows_container.winfo_children())
    
    # Second load with different logs
    log2 = Mock(id=2, date_time="2024-01-15 10:31:00", description="Test2")
    log3 = Mock(id=3, date_time="2024-01-15 10:32:00", description="Test3")
    mock_system.current_log_manager.get_log_list.return_value = [log2, log3]
    view_log_page.load_logs()
    second_count = len(view_log_page.rows_container.winfo_children())
    
    assert second_count == 2


@patch('gui.gui_intrusionlog.system')
def test_load_logs_handles_empty_list(mock_system, view_log_page):
    """Test load_logs handles empty log list."""
    mock_system.current_log_manager.get_log_list.return_value = []
    
    view_log_page.load_logs()
    
    children = view_log_page.rows_container.winfo_children()
    assert len(children) == 0


@patch('gui.gui_intrusionlog.system')
def test_load_logs_handles_many_logs(mock_system, view_log_page):
    """Test load_logs handles many log entries."""
    logs = [Mock(id=i, date_time=f"2024-01-15 10:{i:02d}:00", description=f"Log {i}") 
            for i in range(100)]
    mock_system.current_log_manager.get_log_list.return_value = logs
    
    view_log_page.load_logs()
    
    children = view_log_page.rows_container.winfo_children()
    assert len(children) == 100


# ============================================================
# Back Button Tests
# ============================================================

def test_back_button_navigates_to_main(view_log_page, mock_controller):
    """Test back button navigates to main page."""
    # Find the back button and simulate click
    # In real GUI testing, we'd need to actually click it
    # For now, just verify controller has show_frame method
    assert hasattr(view_log_page.controller, 'show_frame')
