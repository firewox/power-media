#!/usr/bin/env python3
"""
Tests for post_text_enhanced module
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../post-text/scripts"))

from post_text_enhanced import (
    parse_args,
    read_content_file,
    validate_content,
    initialize_components,
    main
)


class TestParseArgs(unittest.TestCase):
    """Tests for parse_args function"""

    @patch('post_text_enhanced.argparse.ArgumentParser.parse_args')
    def test_parse_args_with_all_options(self, mock_parse_args):
        """Test parsing all command line arguments"""
        mock_args = Mock()
        mock_args.content_file = "content.txt"
        mock_args.max_retries = 5
        mock_args.screenshot_dir = "custom/screenshots/"
        mock_args.no_cleanup = True
        mock_parse_args.return_value = mock_args

        args = parse_args()

        self.assertEqual(args.content_file, "content.txt")
        self.assertEqual(args.max_retries, 5)
        self.assertEqual(args.screenshot_dir, "custom/screenshots/")
        self.assertTrue(args.no_cleanup)

    @patch('post_text_enhanced.argparse.ArgumentParser.parse_args')
    def test_parse_args_with_defaults(self, mock_parse_args):
        """Test parsing with default values"""
        mock_args = Mock()
        mock_args.content_file = "test.txt"
        mock_args.max_retries = 3
        mock_args.screenshot_dir = "screenshots/weibo/"
        mock_args.no_cleanup = False
        mock_parse_args.return_value = mock_args

        args = parse_args()

        self.assertEqual(args.content_file, "test.txt")
        self.assertEqual(args.max_retries, 3)
        self.assertEqual(args.screenshot_dir, "screenshots/weibo/")
        self.assertFalse(args.no_cleanup)


class TestReadContentFile(unittest.TestCase):
    """Tests for read_content_file function"""

    @patch('builtins.open', mock_open(read_data="Hello World"))
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_read_content_file_success(self, mock_isfile, mock_exists):
        """Test successfully reading content file"""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        content = read_content_file("test.txt")

        self.assertEqual(content, "Hello World")

    @patch('builtins.open', mock_open(read_data="  Content with spaces  "))
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_read_content_file_strips_whitespace(self, mock_isfile, mock_exists):
        """Test that content is stripped of whitespace"""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        content = read_content_file("test.txt")

        self.assertEqual(content, "Content with spaces")

    @patch('os.path.exists')
    def test_read_content_file_not_found(self, mock_exists):
        """Test FileNotFoundError when file doesn't exist"""
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError) as context:
            read_content_file("nonexistent.txt")

        self.assertIn("nonexistent.txt", str(context.exception))

    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_read_content_file_not_a_file(self, mock_isfile, mock_exists):
        """Test FileNotFoundError when path is not a file"""
        mock_exists.return_value = True
        mock_isfile.return_value = False

        with self.assertRaises(FileNotFoundError) as context:
            read_content_file("/path/to/directory")

        self.assertIn("路径不是文件", str(context.exception))

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_read_content_file_io_error(self, mock_isfile, mock_exists, mock_open):
        """Test IOError when reading fails"""
        mock_exists.return_value = True
        mock_isfile.return_value = True

        with self.assertRaises(IOError) as context:
            read_content_file("test.txt")

        self.assertIn("Permission denied", str(context.exception))


class TestValidateContent(unittest.TestCase):
    """Tests for validate_content function"""

    def test_validate_content_valid(self):
        """Test valid content"""
        is_valid, error = validate_content("Hello World")

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_content_empty(self):
        """Test empty content"""
        is_valid, error = validate_content("")

        self.assertFalse(is_valid)
        self.assertEqual(error, "内容不能为空")

    def test_validate_content_whitespace_only(self):
        """Test whitespace-only content (should pass after strip)"""
        # Note: validate_content doesn't strip, that's done in read_content_file
        is_valid, error = validate_content("   ")

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_content_too_long(self):
        """Test content exceeding 140 characters"""
        long_content = "A" * 141

        is_valid, error = validate_content(long_content)

        self.assertFalse(is_valid)
        self.assertIn("141", error)
        self.assertIn("140", error)

    def test_validate_content_exactly_140(self):
        """Test content exactly 140 characters"""
        content = "A" * 140

        is_valid, error = validate_content(content)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_content_one_under_limit(self):
        """Test content one character under limit"""
        content = "A" * 139

        is_valid, error = validate_content(content)

        self.assertTrue(is_valid)
        self.assertIsNone(error)


class TestInitializeComponents(unittest.TestCase):
    """Tests for initialize_components function"""

    @patch('post_text_enhanced.WeiboAutomation')
    @patch('post_text_enhanced.SubagentCoordinator')
    @patch('post_text_enhanced.ScreenshotManager')
    def test_initialize_components(self, mock_screenshot_mgr, mock_coordinator, mock_weibo):
        """Test component initialization"""
        mock_weibo_instance = Mock()
        mock_coordinator_instance = Mock()
        mock_screenshot_mgr_instance = Mock()

        mock_weibo.return_value = mock_weibo_instance
        mock_coordinator.return_value = mock_coordinator_instance
        mock_screenshot_mgr.return_value = mock_screenshot_mgr_instance

        weibo, coordinator, screenshot_mgr = initialize_components(
            "screenshots/test/",
            no_cleanup=False
        )

        self.assertEqual(weibo, mock_weibo_instance)
        self.assertEqual(coordinator, mock_coordinator_instance)
        self.assertEqual(screenshot_mgr, mock_screenshot_mgr_instance)

        # Verify ScreenshotManager was called with correct max_age_days
        mock_screenshot_mgr.assert_called_once_with(
            base_dir="screenshots/test/",
            max_age_days=7
        )

    @patch('post_text_enhanced.WeiboAutomation')
    @patch('post_text_enhanced.SubagentCoordinator')
    @patch('post_text_enhanced.ScreenshotManager')
    def test_initialize_components_no_cleanup(self, mock_screenshot_mgr, mock_coordinator, mock_weibo):
        """Test component initialization with no_cleanup=True"""
        mock_weibo_instance = Mock()
        mock_coordinator_instance = Mock()
        mock_screenshot_mgr_instance = Mock()

        mock_weibo.return_value = mock_weibo_instance
        mock_coordinator.return_value = mock_coordinator_instance
        mock_screenshot_mgr.return_value = mock_screenshot_mgr_instance

        weibo, coordinator, screenshot_mgr = initialize_components(
            "screenshots/test/",
            no_cleanup=True
        )

        # Verify ScreenshotManager was called with max_age_days=0
        mock_screenshot_mgr.assert_called_once_with(
            base_dir="screenshots/test/",
            max_age_days=0
        )


class TestMainSuccessFlow(unittest.TestCase):
    """Tests for main function success flow with mocks"""

    @patch('post_text_enhanced.parse_args')
    @patch('post_text_enhanced.read_content_file')
    @patch('post_text_enhanced.validate_content')
    @patch('post_text_enhanced.initialize_components')
    @patch('post_text_enhanced.json.dumps')
    def test_main_success_flow(
        self, mock_json_dumps, mock_init, mock_validate, mock_read, mock_parse_args
    ):
        """Test successful execution flow with mocks"""
        # Setup mock args
        mock_args = Mock()
        mock_args.content_file = "test.txt"
        mock_args.max_retries = 3
        mock_args.screenshot_dir = "screenshots/"
        mock_args.no_cleanup = False
        mock_parse_args.return_value = mock_args

        # Setup mock content
        mock_read.return_value = "Test content"
        mock_validate.return_value = (True, None)

        # Setup mock components
        mock_weibo = Mock()
        mock_weibo.find_or_open_weibo.return_value = True
        mock_weibo.get_browser_window_rect.return_value = {
            "left": 100,
            "top": 50,
            "width": 1200,
            "height": 800
        }
        mock_weibo.bbox_to_center.return_value = (0.5, 0.5)
        mock_weibo.bbox_to_screen_coords.return_value = (500, 300)
        mock_weibo.mcp = Mock()

        mock_coordinator = Mock()
        mock_coordinator.analyze_screenshot.return_value = {
            "input_box": [0.47, 0.25, 0.61, 0.30],
            "send_button": [0.72, 0.25, 0.78, 0.30],
            "headline_article_button": None
        }

        mock_screenshot_mgr = Mock()
        mock_screenshot_mgr.capture_and_save.return_value = "screenshots/weibo_home_20250419_143052.png"
        mock_screenshot_mgr.cleanup_old_screenshots.return_value = 2

        mock_init.return_value = (mock_weibo, mock_coordinator, mock_screenshot_mgr)

        # Mock json.dumps to avoid actual JSON output during test
        mock_json_dumps.return_value = "{}"

        # Run main
        result = main()

        # Verify success
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "微博发送完成")
        self.assertEqual(result["content_file"], "test.txt")
        self.assertEqual(result["content_length"], 12)  # len("Test content")
        self.assertEqual(result["screenshot_path"], "screenshots/weibo_home_20250419_143052.png")
        self.assertEqual(result["cleanup_deleted"], 2)

        # Verify all components were called
        mock_read.assert_called_once_with("test.txt")
        mock_validate.assert_called_once_with("Test content")
        mock_weibo.find_or_open_weibo.assert_called_once()
        mock_screenshot_mgr.capture_and_save.assert_called_once()
        mock_coordinator.analyze_screenshot.assert_called_once_with(
            "screenshots/weibo_home_20250419_143052.png",
            max_retries=3
        )


class TestMainWindowNotFound(unittest.TestCase):
    """Tests for main function when window is not found"""

    @patch('post_text_enhanced.parse_args')
    @patch('post_text_enhanced.read_content_file')
    @patch('post_text_enhanced.validate_content')
    @patch('post_text_enhanced.initialize_components')
    @patch('post_text_enhanced.json.dumps')
    def test_main_window_not_found(
        self, mock_json_dumps, mock_init, mock_validate, mock_read, mock_parse_args
    ):
        """Test when weibo window cannot be found"""
        # Setup mock args
        mock_args = Mock()
        mock_args.content_file = "test.txt"
        mock_args.max_retries = 3
        mock_args.screenshot_dir = "screenshots/"
        mock_args.no_cleanup = False
        mock_parse_args.return_value = mock_args

        # Setup mock content
        mock_read.return_value = "Test content"
        mock_validate.return_value = (True, None)

        # Setup mock components with window not found
        mock_weibo = Mock()
        mock_weibo.find_or_open_weibo.return_value = False

        mock_coordinator = Mock()
        mock_screenshot_mgr = Mock()

        mock_init.return_value = (mock_weibo, mock_coordinator, mock_screenshot_mgr)

        # Mock json.dumps
        mock_json_dumps.return_value = "{}"

        # Run main
        result = main()

        # Verify failure
        self.assertFalse(result["success"])
        self.assertIn("无法打开或找到微博窗口", result["error"])
        self.assertEqual(result["content_file"], "test.txt")
        self.assertEqual(result["content_length"], 12)

        # Verify screenshot and analysis were not called
        mock_screenshot_mgr.capture_and_save.assert_not_called()
        mock_coordinator.analyze_screenshot.assert_not_called()


class TestMainSubagentFailure(unittest.TestCase):
    """Tests for main function when subagent analysis fails"""

    @patch('post_text_enhanced.parse_args')
    @patch('post_text_enhanced.read_content_file')
    @patch('post_text_enhanced.validate_content')
    @patch('post_text_enhanced.initialize_components')

    @patch('post_text_enhanced.json.dumps')
    def test_main_subagent_failure(
        self, mock_json_dumps, mock_init, mock_validate, mock_read, mock_parse_args
    ):
        """Test when subagent analysis fails"""
        # Setup mock args
        mock_args = Mock()
        mock_args.content_file = "test.txt"
        mock_args.max_retries = 3
        mock_args.screenshot_dir = "screenshots/"
        mock_args.no_cleanup = False
        mock_parse_args.return_value = mock_args

        # Setup mock content
        mock_read.return_value = "Test content"
        mock_validate.return_value = (True, None)

        # Setup mock components
        mock_weibo = Mock()
        mock_weibo.find_or_open_weibo.return_value = True

        mock_coordinator = Mock()
        from subagent_coordinator import SubagentError
        mock_coordinator.analyze_screenshot.side_effect = SubagentError("Subagent failed")

        mock_screenshot_mgr = Mock()
        mock_screenshot_mgr.capture_and_save.return_value = "screenshots/test.png"

        mock_init.return_value = (mock_weibo, mock_coordinator, mock_screenshot_mgr)

        # Mock json.dumps
        mock_json_dumps.return_value = "{}"

        # Run main
        result = main()

        # Verify failure
        self.assertFalse(result["success"])
        self.assertIn("界面分析失败", result["error"])
        self.assertEqual(result["screenshot_path"], "screenshots/test.png")


class TestMainContentValidationFailure(unittest.TestCase):
    """Tests for main function when content validation fails"""

    @patch('post_text_enhanced.parse_args')
    @patch('post_text_enhanced.read_content_file')
    @patch('post_text_enhanced.validate_content')
    @patch('post_text_enhanced.json.dumps')
    def test_main_content_too_long(
        self, mock_json_dumps, mock_validate, mock_read, mock_parse_args
    ):
        """Test when content is too long"""
        # Setup mock args
        mock_args = Mock()
        mock_args.content_file = "test.txt"
        mock_args.max_retries = 3
        mock_args.screenshot_dir = "screenshots/"
        mock_args.no_cleanup = False
        mock_parse_args.return_value = mock_args

        # Setup mock content that is too long
        mock_read.return_value = "A" * 141
        mock_validate.return_value = (False, "内容超长: 141 字符 (最多 140 字符)")

        # Mock json.dumps
        mock_json_dumps.return_value = "{}"

        # Run main
        result = main()

        # Verify failure
        self.assertFalse(result["success"])
        self.assertIn("内容超长", result["error"])
        self.assertEqual(result["content_file"], "test.txt")


class TestMainFileNotFound(unittest.TestCase):
    """Tests for main function when content file is not found"""

    @patch('post_text_enhanced.parse_args')
    @patch('post_text_enhanced.read_content_file')
    @patch('post_text_enhanced.json.dumps')
    def test_main_file_not_found(
        self, mock_json_dumps, mock_read, mock_parse_args
    ):
        """Test when content file does not exist"""
        # Setup mock args
        mock_args = Mock()
        mock_args.content_file = "nonexistent.txt"
        mock_args.max_retries = 3
        mock_args.screenshot_dir = "screenshots/"
        mock_args.no_cleanup = False
        mock_parse_args.return_value = mock_args

        # Setup mock to raise FileNotFoundError
        mock_read.side_effect = FileNotFoundError("内容文件不存在: nonexistent.txt")

        # Mock json.dumps
        mock_json_dumps.return_value = "{}"

        # Run main
        result = main()

        # Verify failure
        self.assertFalse(result["success"])
        self.assertIn("内容文件不存在", result["error"])
        self.assertEqual(result["content_file"], "nonexistent.txt")


if __name__ == "__main__":
    unittest.main()
