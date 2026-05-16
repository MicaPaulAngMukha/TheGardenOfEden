"""
Helper module to get the correct resource path for PyInstaller executables.
"""
import sys
import os

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    When running as a PyInstaller executable, files are extracted to a temp folder.
    This function returns the correct path whether running from source or as exe.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running from source, use current directory
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
