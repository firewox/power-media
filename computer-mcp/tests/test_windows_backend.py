import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from windows_backend import list_windows, focus_window

def test_list_windows_returns_list():
    windows = list_windows()
    assert isinstance(windows, list)
    assert len(windows) > 0
    w = windows[0]
    assert "title" in w
    assert "handle" in w

def test_focus_window_unknown_title_raises():
    import pytest
    with pytest.raises(ValueError, match="not found"):
        focus_window("__nonexistent_window_xyzxyz__")
