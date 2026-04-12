"""
Tests for IsolatedBrowser.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from isolated_browser import IsolatedBrowser, BrowserNotFoundError


class TestIsolatedBrowser:
    """IsolatedBrowser unit tests"""

    @pytest.fixture
    def mock_desktop_manager(self):
        manager = Mock()
        manager.create_desktop.return_value = "test-desktop-id"
        manager.get_current_desktop.return_value = "user-desktop-id"
        return manager

    @pytest.fixture
    def browser(self, mock_desktop_manager):
        return IsolatedBrowser(mock_desktop_manager)

    def test_init(self, browser):
        """Properties should be None after init"""
        assert browser.desktop_id is None
        assert browser.window_hwnd is None

    @patch('isolated_browser.find_browser_window')
    def test_launch_or_locate_finds_existing(self, mock_find, browser):
        """Should find existing window"""
        mock_find.return_value = {"hwnd": 12345, "title": "Chrome"}

        hwnd = browser.launch_or_locate()

        assert hwnd == 12345
        mock_find.assert_called_once()

    @patch('isolated_browser.find_browser_window')
    @patch('isolated_browser.launch_new_browser')
    def test_launch_or_locate_launches_new(self, mock_launch, mock_find, browser):
        """Should launch new window if none found"""
        mock_find.return_value = None
        mock_launch.return_value = {"hwnd": 67890, "title": "Chrome"}

        hwnd = browser.launch_or_locate()

        assert hwnd == 67890
        mock_find.assert_called_once()
        mock_launch.assert_called_once()

    @patch.object(IsolatedBrowser, 'launch_or_locate', return_value=12345)
    @patch.object(IsolatedBrowser, 'move_to_isolated_desktop')
    def test_setup_sets_desktop_id_and_hwnd(
        self, mock_move, mock_launch, browser, mock_desktop_manager
    ):
        """setup should set desktop_id and window_hwnd"""
        result = browser.setup()

        assert browser.desktop_id == "test-desktop-id"
        assert browser.window_hwnd == 12345
        assert result == 12345
        mock_desktop_manager.create_desktop.assert_called_once()
        mock_launch.assert_called_once()
        mock_move.assert_called_once()

    def test_move_to_isolated_desktop_raises_without_setup(self, browser):
        """Should raise if not set up"""
        with pytest.raises(RuntimeError, match="must be set first"):
            browser.move_to_isolated_desktop()

    @patch('isolated_browser.ctypes')
    def test_ensure_restored(self, mock_ctypes, browser):
        """ensure_restored should call ShowWindow"""
        browser.window_hwnd = 12345
        browser.ensure_restored()
        mock_ctypes.windll.user32.ShowWindow.assert_called_with(12345, 9)

    @patch('isolated_browser.ctypes')
    def test_ensure_minimized(self, mock_ctypes, browser):
        """ensure_minimized should call ShowWindow"""
        browser.window_hwnd = 12345
        browser.ensure_minimized()
        mock_ctypes.windll.user32.ShowWindow.assert_called_with(12345, 6)

    def test_is_alive_without_hwnd(self, browser):
        """is_alive should return False without hwnd"""
        assert browser.is_alive() is False

    @patch('isolated_browser.ctypes')
    def test_is_alive_with_hwnd(self, mock_ctypes, browser):
        """is_alive should call IsWindow"""
        browser.window_hwnd = 12345
        mock_ctypes.windll.user32.IsWindow.return_value = True
        assert browser.is_alive() is True

    @patch('isolated_browser.ctypes')
    def test_cleanup(self, mock_ctypes, browser):
        """cleanup should reset properties"""
        browser.window_hwnd = 12345
        browser.desktop_id = "test-desktop"
        mock_ctypes.windll.user32.IsWindow.return_value = True

        browser.cleanup()

        assert browser.window_hwnd is None
        assert browser.desktop_id is None
