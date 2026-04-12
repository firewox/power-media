"""
Tests for IsolatedOperations.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, call

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from isolated_operations import IsolatedOperation, isolated_op


class TestIsolatedOperation:
    """IsolatedOperation unit tests"""

    @pytest.fixture
    def mock_manager(self):
        manager = Mock()
        manager.get_current_desktop.return_value = "user-desktop"
        return manager

    @pytest.fixture
    def mock_browser(self):
        browser = Mock()
        browser.desktop_id = "isolated-desktop"
        browser.window_hwnd = 12345
        return browser

    def test_execute_switches_desktops(self, mock_manager, mock_browser):
        """Should switch desktops during execution"""
        def operation():
            return {"success": True}

        iso_op = IsolatedOperation(
            mock_manager, mock_browser, operation
        )
        result = iso_op.execute()

        assert mock_manager.switch_to_desktop.call_count == 2

    def test_execute_restores_window(self, mock_manager, mock_browser):
        """Should restore window before operation"""
        def operation():
            return {"success": True}

        iso_op = IsolatedOperation(
            mock_manager, mock_browser, operation
        )
        iso_op.execute()

        mock_browser.ensure_restored.assert_called_once()

    def test_execute_returns_operation_result(self, mock_manager, mock_browser):
        """Should return operation result"""
        def operation():
            return {"data": "test"}

        iso_op = IsolatedOperation(
            mock_manager, mock_browser, operation
        )
        result = iso_op.execute()

        assert result == {"data": "test"}

    def test_execute_always_switches_back_on_error(
        self, mock_manager, mock_browser
    ):
        """Should switch back even on error"""
        def operation():
            raise ValueError("Test error")

        iso_op = IsolatedOperation(
            mock_manager, mock_browser, operation
        )

        with pytest.raises(ValueError, match="Test error"):
            iso_op.execute()

        mock_manager.switch_to_desktop.assert_any_call("user-desktop")

    def test_isolated_op_decorator(self, mock_manager, mock_browser):
        """Decorator should wrap function"""
        @isolated_op(mock_manager, mock_browser)
        def my_op(x, y):
            return x + y

        result = my_op(3, 4)
        assert result == 7
