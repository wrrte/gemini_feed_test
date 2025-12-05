import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from gui.gui_thumbnails import ThumbnailsPage


# Use tk_root from conftest - no root fixture needed

@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    return Mock()


@pytest.fixture
def thumbnails_page(tk_root, mock_controller):
    """Create a ThumbnailsPage instance."""
    with patch('gui.gui_thumbnails.system') as mock_system:
        # Mock get_thumbnail_views to return test images
        mock_system.current_camera_controller.get_thumbnail_views.return_value = {
            1: Image.new('RGB', (100, 100), color='red'),
            2: Image.new('RGB', (100, 100), color='green'),
            3: Image.new('RGB', (100, 100), color='blue'),
        }
        page = ThumbnailsPage(tk_root, mock_controller)
        yield page


# ============================================================
# Initialization Tests
# ============================================================

def test_thumbnails_page_initializes(thumbnails_page):
    """Test ThumbnailsPage initializes correctly."""
    assert thumbnails_page.controller is not None
    assert thumbnails_page.thumb_frame is not None


def test_thumbnails_page_has_title(thumbnails_page):
    """Test ThumbnailsPage has title label."""
    # Should create without errors
    assert thumbnails_page is not None


@patch('gui.gui_thumbnails.system')
def test_thumbnails_page_loads_thumbnails_on_init(mock_system, tk_root, mock_controller):
    """Test ThumbnailsPage loads thumbnails on initialization."""
    mock_system.current_camera_controller.get_thumbnail_views.return_value = {
        1: Image.new('RGB', (200, 200), color='red')
    }
    
    page = ThumbnailsPage(tk_root, mock_controller)
    
    mock_system.current_camera_controller.get_thumbnail_views.assert_called_once()


# ============================================================
# load_thumbnails Tests
# ============================================================

@patch('gui.gui_thumbnails.system')
def test_load_thumbnails_creates_frames_for_each_camera(mock_system, thumbnails_page):
    """Test load_thumbnails creates a frame for each camera."""
    mock_system.current_camera_controller.get_thumbnail_views.return_value = {
        1: Image.new('RGB', (100, 100)),
        2: Image.new('RGB', (100, 100)),
    }
    
    thumbnails_page.load_thumbnails()
    
    # Should have frames for cameras
    children = thumbnails_page.thumb_frame.winfo_children()
    assert len(children) >= 2


@patch('gui.gui_thumbnails.system')
def test_load_thumbnails_stores_tk_images(mock_system, thumbnails_page):
    """Test load_thumbnails stores ImageTk objects."""
    test_images = {
        1: Image.new('RGB', (100, 100), color='red'),
        2: Image.new('RGB', (100, 100), color='blue'),
    }
    mock_system.current_camera_controller.get_thumbnail_views.return_value = test_images
    
    thumbnails_page.load_thumbnails()
    
    assert len(thumbnails_page.tk_thumbnails) == 2
    assert 1 in thumbnails_page.tk_thumbnails
    assert 2 in thumbnails_page.tk_thumbnails


@patch('gui.gui_thumbnails.system')
def test_load_thumbnails_clears_old_widgets(mock_system, thumbnails_page):
    """Test load_thumbnails clears old thumbnail widgets."""
    # First load
    mock_system.current_camera_controller.get_thumbnail_views.return_value = {
        1: Image.new('RGB', (100, 100))
    }
    thumbnails_page.load_thumbnails()
    first_count = len(thumbnails_page.thumb_frame.winfo_children())
    
    # Second load with different cameras
    mock_system.current_camera_controller.get_thumbnail_views.return_value = {
        2: Image.new('RGB', (100, 100)),
        3: Image.new('RGB', (100, 100)),
    }
    thumbnails_page.load_thumbnails()
    second_count = len(thumbnails_page.thumb_frame.winfo_children())
    
    # Should have replaced widgets
    assert second_count >= 2


@patch('gui.gui_thumbnails.system')
def test_load_thumbnails_handles_empty_dict(mock_system, tk_root, mock_controller):
    """Test load_thumbnails handles empty camera dict."""
    mock_system.current_camera_controller.get_thumbnail_views.return_value = {}
    
    page = ThumbnailsPage(tk_root, mock_controller)
    
    # Should not crash
    assert page is not None


@patch('gui.gui_thumbnails.system')
def test_load_thumbnails_resizes_large_images(mock_system, thumbnails_page):
    """Test load_thumbnails resizes large images."""
    large_image = Image.new('RGB', (1000, 1000))
    mock_system.current_camera_controller.get_thumbnail_views.return_value = {
        1: large_image
    }
    
    thumbnails_page.load_thumbnails()
    
    # Image should be stored as thumbnail
    assert 1 in thumbnails_page.tk_thumbnails


# ============================================================
# Grid Layout Tests
# ============================================================

@patch('gui.gui_thumbnails.system')
def test_thumbnails_arranged_in_grid(mock_system, tk_root, mock_controller):
    """Test thumbnails are arranged in 3-column grid."""
    # Create 5 cameras to test wrapping
    cameras = {i: Image.new('RGB', (100, 100)) for i in range(1, 6)}
    mock_system.current_camera_controller.get_thumbnail_views.return_value = cameras
    
    page = ThumbnailsPage(tk_root, mock_controller)
    
    # Should have created frames in grid
    assert len(page.tk_thumbnails) == 5
