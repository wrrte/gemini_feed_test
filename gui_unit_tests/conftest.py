import pytest
import tkinter as tk
import os
import sys
import time


# Set TCL/TK environment variables before any tests run
@pytest.fixture(scope="session", autouse=True)
def setup_tcl_environment():
    """Set up TCL/TK environment variables for the test session."""
    python_dir = os.path.dirname(os.path.dirname(tk.__file__))
    tcl_dir = os.path.join(python_dir, "tcl")
    
    if os.path.exists(tcl_dir):
        os.environ["TCL_LIBRARY"] = os.path.join(tcl_dir, "tcl8.6")
        os.environ["TK_LIBRARY"] = os.path.join(tcl_dir, "tk8.6")
    
    yield


@pytest.fixture
def tk_root():
    """Create a Tk root for testing that properly cleans up with delays."""
    # Ensure no existing default root
    if tk._default_root:
        try:
            tk._default_root.destroy()
        except:
            pass
        tk._default_root = None
    
    # Wait before creating new root
    time.sleep(0.2)
    
    root = tk.Tk()
    root.withdraw()
    
    yield root
    
    # Proper cleanup with delays
    try:
        # Process all pending events first
        root.update_idletasks()
        
        # Destroy all children
        for child in list(root.winfo_children()):
            try:
                child.destroy()
            except:
                pass
        
        # Wait for children to be destroyed
        root.update_idletasks()
        time.sleep(0.1)
        
        # Now destroy root
        root.quit()
        root.destroy()
        
        # Wait after destruction
        time.sleep(0.2)
    except:
        pass
    
    # Reset default root
    tk._default_root = None


@pytest.fixture(autouse=True)
def cleanup_between_tests(tk_root):
    """Clean up widgets between tests but keep the root."""
    yield
    
    # After each test, destroy all toplevel children
    try:
        for widget in tk_root.winfo_children():
            try:
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            except:
                pass
        tk_root.update_idletasks()
        time.sleep(0.05)  # Small delay between tests
    except:
        pass
