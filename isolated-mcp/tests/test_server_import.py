"""
Tests for server module imports.
"""

import pytest
import sys
import os
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestServerImport:
    """Test server module imports"""

    def test_import_virtual_desktop(self):
        from virtual_desktop import (
            VirtualDesktopManager, VirtualDesktopError
        )
        assert VirtualDesktopManager
        assert VirtualDesktopError

    def test_import_isolated_browser(self):
        from isolated_browser import (
            IsolatedBrowser, BrowserNotFoundError
        )
        assert IsolatedBrowser
        assert BrowserNotFoundError

    def test_import_isolated_operations(self):
        from isolated_operations import (
            IsolatedOperation, isolated_op
        )
        assert IsolatedOperation
        assert isolated_op

    def test_server_file_exists(self):
        """Test server.py file exists"""
        server_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server.py"
        )
        assert os.path.exists(server_path)

    def test_server_importable(self):
        """Test server module can be loaded (not executed)"""
        server_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "server.py"
        )
        spec = importlib.util.spec_from_file_location(
            "server", server_path
        )
        assert spec is not None
        assert spec.loader is not None
