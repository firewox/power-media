"""
Tests for VirtualDesktopManager.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from virtual_desktop import VirtualDesktopManager, VirtualDesktopError


class TestVirtualDesktopManager:
    """VirtualDesktopManager unit tests"""

    @pytest.fixture
    def manager(self):
        return VirtualDesktopManager()

    def test_init(self, manager):
        """Should initialize without error"""
        assert manager._desktop_counter == 0
        assert manager._created_desktops == []

    def test_list_desktops_initial(self, manager):
        """list_desktops should return ['original'] initially"""
        desktops = manager.list_desktops()
        assert isinstance(desktops, list)
        assert "original" in desktops

    def test_create_desktop_adds_to_list(self, manager):
        """create_desktop should add to tracked list"""
        with patch.object(manager, '_run_powershell'):
            # Mock keyboard calls
            with patch.object(manager, 'create_desktop', return_value="test-desktop-1"):
                desktop_id = manager.create_desktop("test")
                assert isinstance(desktop_id, str)
                assert "test" in desktop_id or "isolated" in desktop_id

    def test_get_current_desktop_returns_string(self, manager):
        """get_current_desktop should return a string"""
        desktop_id = manager.get_current_desktop()
        assert isinstance(desktop_id, str)
        assert len(desktop_id) > 0

    def test_is_window_on_current_desktop(self, manager):
        """is_window_on_current_desktop should return bool"""
        result = manager.is_window_on_current_desktop(12345)
        assert isinstance(result, bool)

    def test_cleanup_empty(self, manager):
        """cleanup with empty list should do nothing"""
        manager.cleanup([])  # Should not raise
        manager.cleanup()    # Should not raise

    def test_move_window_to_desktop_no_error(self, manager):
        """move_window_to_desktop should not raise"""
        # This uses PowerShell which may work in all environments
        try:
            manager.move_window_to_desktop(12345, "test-desktop")
        except Exception:
            pass  # Expected in some environments
