#!/usr/bin/env python3
"""
Comprehensive tests for ScreenshotManager.

Tests cover initialization, filename generation, screenshot saving,
capture and save, cleanup, directory size monitoring, and listing.
"""

import os
import sys
import time
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.screenshot_manager import (
    ScreenshotManager, ScreenshotError
)


class MockMCPClient:
    """Mock MCP client for testing"""

    def __init__(self, success=True, screenshot_path=None, error_msg=None):
        self.success = success
        self.screenshot_path = screenshot_path
        self.error_msg = error_msg

    def inspect_screen(self):
        if self.success:
            return {
                'success': True,
                'screenshot_path': self.screenshot_path,
                'screenshot_width': 1920,
                'screenshot_height': 1080
            }
        else:
            return {
                'success': False,
                'error': self.error_msg or 'Mock error'
            }


class TestScreenshotError(unittest.TestCase):
    """Tests for ScreenshotError exception."""

    def test_screenshot_error_is_exception(self):
        """Test that ScreenshotError is an Exception subclass."""
        self.assertTrue(issubclass(ScreenshotError, Exception))

    def test_screenshot_error_message(self):
        """Test ScreenshotError message."""
        error = ScreenshotError("Test error message")
        self.assertEqual(str(error), "Test error message")

    def test_screenshot_error_can_be_caught(self):
        """Test that ScreenshotError can be caught."""
        try:
            raise ScreenshotError("test error")
        except ScreenshotError as e:
            self.assertEqual(str(e), "test error")


class TestScreenshotManagerInit(unittest.TestCase):
    """Tests for ScreenshotManager initialization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_directory(self):
        """Test that initialization creates the directory if it doesn't exist."""
        new_dir = os.path.join(self.temp_dir, "new_screenshots", "weibo")
        self.assertFalse(os.path.exists(new_dir))

        manager = ScreenshotManager(base_dir=new_dir, max_age_days=7)

        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
        self.assertEqual(manager.base_dir, new_dir)
        self.assertEqual(manager.max_age_days, 7)

    def test_init_with_existing_directory(self):
        """Test initialization with an existing directory."""
        existing_dir = os.path.join(self.temp_dir, "existing")
        os.makedirs(existing_dir)

        # Create a test file to verify directory is preserved
        test_file = os.path.join(existing_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")

        manager = ScreenshotManager(base_dir=existing_dir, max_age_days=3)

        self.assertTrue(os.path.exists(existing_dir))
        self.assertTrue(os.path.exists(test_file))
        self.assertEqual(manager.base_dir, existing_dir)
        self.assertEqual(manager.max_age_days, 3)

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory to avoid creating screenshots in project
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                manager = ScreenshotManager()

                self.assertEqual(manager.base_dir, "screenshots/weibo/")
                self.assertEqual(manager.max_age_days, 7)
                self.assertTrue(os.path.exists("screenshots/weibo/"))
            finally:
                os.chdir(original_cwd)

    def test_init_creates_nested_directories(self):
        """Test that initialization creates nested directories."""
        nested_dir = os.path.join(self.temp_dir, "a", "b", "c", "screenshots")

        manager = ScreenshotManager(base_dir=nested_dir)

        self.assertTrue(os.path.exists(nested_dir))


class TestScreenshotManagerGenerateFilename(unittest.TestCase):
    """Tests for generate_filename method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=7)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_filename_format(self):
        """Test filename format matches expected pattern."""
        filename = self.manager.generate_filename("home")

        # Should match: weibo_{context}_{YYYYMMDD}_{HHMMSS}.png
        self.assertTrue(filename.startswith("weibo_home_"))
        self.assertTrue(filename.endswith(".png"))

        # Extract parts
        parts = filename.replace(".png", "").split("_")
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "weibo")
        self.assertEqual(parts[1], "home")

        # Check date format (YYYYMMDD)
        date_part = parts[2]
        self.assertEqual(len(date_part), 8)
        self.assertTrue(date_part.isdigit())

        # Check time format (HHMMSS)
        time_part = parts[3]
        self.assertEqual(len(time_part), 6)
        self.assertTrue(time_part.isdigit())

    def test_generate_filename_different_contexts(self):
        """Test filename generation with different contexts."""
        contexts = ["home", "error", "login", "post", "profile", "checkout"]

        for context in contexts:
            filename = self.manager.generate_filename(context)
            expected_prefix = f"weibo_{context}_"
            self.assertTrue(
                filename.startswith(expected_prefix),
                f"Filename {filename} should start with {expected_prefix}"
            )

    def test_generate_filename_default_context(self):
        """Test filename generation with default context."""
        filename = self.manager.generate_filename()

        self.assertTrue(filename.startswith("weibo_home_"))

    def test_generate_filename_unique(self):
        """Test that consecutive filenames follow the expected format.
        
        Note: On fast machines, consecutive calls within the same second
        will generate identical filenames. This is acceptable behavior.
        """
        filename1 = self.manager.generate_filename("test")
        time.sleep(1.1)  # Wait for next second to ensure different timestamp
        filename2 = self.manager.generate_filename("test")

        # Both should match the expected format
        self.assertTrue(filename1.startswith("weibo_test_"))
        self.assertTrue(filename2.startswith("weibo_test_"))
        
        # After waiting a second, they should be different
        self.assertNotEqual(filename1, filename2)

    def test_generate_filename_context_with_underscore(self):
        """Test filename generation with context containing underscore."""
        filename = self.manager.generate_filename("login_error")

        self.assertTrue(filename.startswith("weibo_login_error_"))
        self.assertTrue(filename.endswith(".png"))


class TestScreenshotManagerSaveScreenshot(unittest.TestCase):
    """Tests for save_screenshot method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = tempfile.mkdtemp()
        self.manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=7)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.source_dir, ignore_errors=True)

    def test_save_screenshot_success(self):
        """Test successful screenshot saving."""
        # Create a source file
        source_path = os.path.join(self.source_dir, "source.png")
        with open(source_path, 'wb') as f:
            f.write(b"fake image data")

        # Save screenshot
        saved_path = self.manager.save_screenshot(source_path, "test")

        # Verify file was saved
        self.assertTrue(os.path.exists(saved_path))
        self.assertTrue(saved_path.startswith(self.temp_dir))
        self.assertTrue("weibo_test_" in saved_path)

        # Verify content was copied
        with open(saved_path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b"fake image data")

    def test_save_screenshot_source_not_found(self):
        """Test saving with non-existent source file."""
        non_existent_path = os.path.join(self.source_dir, "does_not_exist.png")

        with self.assertRaises(FileNotFoundError) as context:
            self.manager.save_screenshot(non_existent_path)

        self.assertIn("Source screenshot not found", str(context.exception))

    def test_save_screenshot_source_is_directory(self):
        """Test saving when source path is a directory."""
        subdir = os.path.join(self.source_dir, "subdir")
        os.makedirs(subdir)

        with self.assertRaises(FileNotFoundError) as context:
            self.manager.save_screenshot(subdir)

        self.assertIn("Source path is not a file", str(context.exception))

    def test_save_screenshot_preserves_source(self):
        """Test that source file is preserved after saving."""
        source_path = os.path.join(self.source_dir, "source.png")
        with open(source_path, 'wb') as f:
            f.write(b"test data")

        self.manager.save_screenshot(source_path, "test")

        # Source should still exist
        self.assertTrue(os.path.exists(source_path))


class TestScreenshotManagerCaptureAndSave(unittest.TestCase):
    """Tests for capture_and_save method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = tempfile.mkdtemp()
        self.manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=7)

        # Create a mock source file for MCP to "return"
        self.mock_screenshot_path = os.path.join(self.source_dir, "mock_capture.png")
        with open(self.mock_screenshot_path, 'wb') as f:
            f.write(b"mock screenshot data")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.source_dir, ignore_errors=True)

    def test_capture_and_save_success(self):
        """Test successful capture and save."""
        mock_mcp = MockMCPClient(
            success=True,
            screenshot_path=self.mock_screenshot_path
        )

        saved_path = self.manager.capture_and_save(mock_mcp, "capture_test")

        # Verify file was saved
        self.assertTrue(os.path.exists(saved_path))
        self.assertTrue("weibo_capture_test_" in saved_path)

        # Verify content
        with open(saved_path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b"mock screenshot data")

    def test_capture_and_save_mcp_failure(self):
        """Test capture when MCP fails."""
        mock_mcp = MockMCPClient(
            success=False,
            error_msg="Screenshot capture failed"
        )

        with self.assertRaises(ScreenshotError) as context:
            self.manager.capture_and_save(mock_mcp, "test")

        self.assertIn("MCP screenshot capture failed", str(context.exception))
        self.assertIn("Screenshot capture failed", str(context.exception))

    def test_capture_and_save_mcp_no_screenshot_path(self):
        """Test capture when MCP returns success but no path."""
        mock_mcp = MockMCPClient(success=True, screenshot_path=None)

        with self.assertRaises(ScreenshotError) as context:
            self.manager.capture_and_save(mock_mcp, "test")

        self.assertIn("MCP did not return screenshot_path", str(context.exception))

    def test_capture_and_save_missing_inspect_screen(self):
        """Test capture with MCP client missing inspect_screen method."""
        # Use a simple object that truly doesn't have inspect_screen
        # (Mock objects return new Mocks for any attribute access)
        class NoInspectScreen:
            pass
        mock_mcp = NoInspectScreen()

        with self.assertRaises(AttributeError) as context:
            self.manager.capture_and_save(mock_mcp, "test")

        self.assertIn("MCP client must have 'inspect_screen' method", str(context.exception))

    def test_capture_and_save_mcp_exception(self):
        """Test capture when MCP raises exception."""
        mock_mcp = Mock()
        mock_mcp.inspect_screen.side_effect = Exception("Connection failed")

        with self.assertRaises(ScreenshotError) as context:
            self.manager.capture_and_save(mock_mcp, "test")

        self.assertIn("MCP inspect_screen call failed", str(context.exception))

    def test_capture_and_save_invalid_result_type(self):
        """Test capture when MCP returns non-dict result."""
        mock_mcp = Mock()
        mock_mcp.inspect_screen.return_value = "invalid result"

        with self.assertRaises(ScreenshotError) as context:
            self.manager.capture_and_save(mock_mcp, "test")

        self.assertIn("MCP returned invalid result type", str(context.exception))


class TestScreenshotManagerCleanup(unittest.TestCase):
    """Tests for cleanup_old_screenshots method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleanup_old_screenshots(self):
        """Test cleanup removes old files."""
        manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=1)

        # Create an old file (2 days ago)
        old_file = os.path.join(self.temp_dir, "weibo_old_20240101_120000.png")
        with open(old_file, 'w') as f:
            f.write("old")
        old_time = time.time() - (2 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        # Create a new file (now)
        new_file = os.path.join(self.temp_dir, "weibo_new_20241201_120000.png")
        with open(new_file, 'w') as f:
            f.write("new")

        # Run cleanup
        deleted = manager.cleanup_old_screenshots()

        self.assertEqual(deleted, 1)
        self.assertFalse(os.path.exists(old_file))
        self.assertTrue(os.path.exists(new_file))

    def test_cleanup_disabled(self):
        """Test cleanup is disabled when max_age_days <= 0."""
        manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=0)

        # Create an old file
        old_file = os.path.join(self.temp_dir, "weibo_old_20240101_120000.png")
        with open(old_file, 'w') as f:
            f.write("old")
        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        # Run cleanup
        deleted = manager.cleanup_old_screenshots()

        self.assertEqual(deleted, 0)
        self.assertTrue(os.path.exists(old_file))

    def test_cleanup_negative_max_age(self):
        """Test cleanup with negative max_age_days."""
        manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=-1)

        # Create an old file
        old_file = os.path.join(self.temp_dir, "weibo_old_20240101_120000.png")
        with open(old_file, 'w') as f:
            f.write("old")
        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        # Run cleanup
        deleted = manager.cleanup_old_screenshots()

        self.assertEqual(deleted, 0)
        self.assertTrue(os.path.exists(old_file))

    def test_cleanup_ignores_non_png(self):
        """Test cleanup ignores non-png files."""
        manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=1)

        # Create an old txt file
        old_txt = os.path.join(self.temp_dir, "old_file.txt")
        with open(old_txt, 'w') as f:
            f.write("old text")
        old_time = time.time() - (2 * 24 * 60 * 60)
        os.utime(old_txt, (old_time, old_time))

        # Run cleanup
        deleted = manager.cleanup_old_screenshots()

        self.assertEqual(deleted, 0)
        self.assertTrue(os.path.exists(old_txt))

    def test_cleanup_empty_directory(self):
        """Test cleanup with empty directory."""
        manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=7)

        deleted = manager.cleanup_old_screenshots()

        self.assertEqual(deleted, 0)


class TestScreenshotManagerDirectorySize(unittest.TestCase):
    """Tests for get_directory_size method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=7)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_directory_size_empty(self):
        """Test directory size with empty directory."""
        size = self.manager.get_directory_size()

        self.assertEqual(size, 0)

    def test_get_directory_size_with_files(self):
        """Test directory size calculation with files."""
        # Create files with known sizes
        file1 = os.path.join(self.temp_dir, "file1.png")
        with open(file1, 'w') as f:
            f.write("a" * 100)

        file2 = os.path.join(self.temp_dir, "file2.png")
        with open(file2, 'w') as f:
            f.write("b" * 200)

        size = self.manager.get_directory_size()

        self.assertEqual(size, 300)

    def test_get_directory_size_includes_subdirectories(self):
        """Test directory size includes subdirectories."""
        # Create nested directory
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir)

        # Create files in both directories
        file1 = os.path.join(self.temp_dir, "file1.png")
        with open(file1, 'w') as f:
            f.write("a" * 100)

        file2 = os.path.join(subdir, "file2.png")
        with open(file2, 'w') as f:
            f.write("b" * 200)

        size = self.manager.get_directory_size()

        self.assertEqual(size, 300)


class TestScreenshotManagerListScreenshots(unittest.TestCase):
    """Tests for list_screenshots method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=7)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_screenshots_empty(self):
        """Test listing screenshots in empty directory."""
        screenshots = self.manager.list_screenshots()

        self.assertEqual(screenshots, [])

    def test_list_screenshots(self):
        """Test listing screenshots."""
        # Create test files
        file1 = os.path.join(self.temp_dir, "weibo_home_20240101_120000.png")
        with open(file1, 'w') as f:
            f.write("screenshot 1")

        file2 = os.path.join(self.temp_dir, "weibo_error_20240101_130000.png")
        with open(file2, 'w') as f:
            f.write("screenshot 2 content")

        screenshots = self.manager.list_screenshots()

        self.assertEqual(len(screenshots), 2)

        # Check first file
        self.assertEqual(screenshots[0]['filename'], "weibo_error_20240101_130000.png")
        self.assertEqual(screenshots[0]['context'], "error")
        self.assertEqual(screenshots[0]['size'], 20)
        self.assertTrue(os.path.isabs(screenshots[0]['path']))
        self.assertIn('created_at', screenshots[0])
        self.assertIn('modified_at', screenshots[0])

        # Check second file
        self.assertEqual(screenshots[1]['filename'], "weibo_home_20240101_120000.png")
        self.assertEqual(screenshots[1]['context'], "home")
        self.assertEqual(screenshots[1]['size'], 12)

    def test_list_screenshots_ignores_non_png(self):
        """Test that listing ignores non-png files."""
        # Create png and non-png files
        png_file = os.path.join(self.temp_dir, "weibo_test_20240101_120000.png")
        with open(png_file, 'w') as f:
            f.write("png")

        txt_file = os.path.join(self.temp_dir, "readme.txt")
        with open(txt_file, 'w') as f:
            f.write("text")

        screenshots = self.manager.list_screenshots()

        self.assertEqual(len(screenshots), 1)
        self.assertEqual(screenshots[0]['filename'], "weibo_test_20240101_120000.png")

    def test_list_screenshots_parses_context(self):
        """Test that listing correctly parses context from filename."""
        contexts = ["home", "login_error", "post_success", "checkout"]

        for i, context in enumerate(contexts):
            filename = f"weibo_{context}_2024010{i+1}_120000.png"
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"data {i}")

        screenshots = self.manager.list_screenshots()

        self.assertEqual(len(screenshots), 4)

        # Verify contexts are parsed correctly
        contexts_found = [s['context'] for s in screenshots]
        for context in contexts:
            self.assertIn(context, contexts_found)


class TestScreenshotManagerIntegration(unittest.TestCase):
    """Integration tests for ScreenshotManager."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = tempfile.mkdtemp()
        self.manager = ScreenshotManager(base_dir=self.temp_dir, max_age_days=7)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.source_dir, ignore_errors=True)

    def test_full_workflow(self):
        """Test a complete workflow: save, list, cleanup."""
        # Save multiple screenshots
        for i, context in enumerate(["home", "login", "post"]):
            source = os.path.join(self.source_dir, f"source{i}.png")
            with open(source, 'w') as f:
                f.write(f"screenshot {i}")
            self.manager.save_screenshot(source, context)

        # List screenshots
        screenshots = self.manager.list_screenshots()
        self.assertEqual(len(screenshots), 3)

        # Check directory size
        size = self.manager.get_directory_size()
        self.assertEqual(size, len("screenshot 0") + len("screenshot 1") + len("screenshot 2"))

        # Cleanup (nothing should be deleted as files are new)
        deleted = self.manager.cleanup_old_screenshots()
        self.assertEqual(deleted, 0)

        # List again
        screenshots = self.manager.list_screenshots()
        self.assertEqual(len(screenshots), 3)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)