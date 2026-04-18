"""
Comprehensive tests for SubagentCoordinator.

Tests cover initialization, command building, response parsing,
coordinate validation, and retry logic.
"""

import json
import subprocess
import unittest
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.subagent_coordinator import (
    SubagentCoordinator, SubagentError, ValidationError, ParseError
)


class TestSubagentErrorClasses(unittest.TestCase):
    """Tests for exception class hierarchy."""

    def test_validation_error_is_subagent_error(self):
        """Test that ValidationError is a SubagentError subclass."""
        self.assertTrue(issubclass(ValidationError, SubagentError))

    def test_parse_error_is_subagent_error(self):
        """Test that ParseError is a SubagentError subclass."""
        self.assertTrue(issubclass(ParseError, SubagentError))

    def test_validation_error_can_be_caught_as_subagent_error(self):
        """Test that ValidationError can be caught as SubagentError."""
        try:
            raise ValidationError("test error")
        except SubagentError as e:
            self.assertEqual(str(e), "test error")

    def test_parse_error_can_be_caught_as_subagent_error(self):
        """Test that ParseError can be caught as SubagentError."""
        try:
            raise ParseError("test error")
        except SubagentError as e:
            self.assertEqual(str(e), "test error")


class TestSubagentCoordinatorInit(unittest.TestCase):
    """Tests for SubagentCoordinator initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        coordinator = SubagentCoordinator()

        self.assertEqual(coordinator.model, "ollama-cloud/qwen3.5:397b")
        self.assertEqual(coordinator.timeout, 60)
        self.assertEqual(coordinator.prompt, SubagentCoordinator.DEFAULT_PROMPT)

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        custom_prompt = "Custom prompt for testing"
        coordinator = SubagentCoordinator(
            model="custom-model",
            timeout=120,
            prompt=custom_prompt
        )

        self.assertEqual(coordinator.model, "custom-model")
        self.assertEqual(coordinator.timeout, 120)
        self.assertEqual(coordinator.prompt, custom_prompt)


class TestSubagentCoordinatorBuildCommand(unittest.TestCase):
    """Tests for _build_command method."""

    def test_build_command_returns_list(self):
        """Test that command is returned as a list."""
        coordinator = SubagentCoordinator()
        screenshot_path = "/path/to/screenshot.png"

        command = coordinator._build_command(screenshot_path)

        # Check that command is a list
        self.assertIsInstance(command, list)

    def test_build_command_contains_expected_parts(self):
        """Test that command list contains expected parts."""
        coordinator = SubagentCoordinator()
        screenshot_path = "/path/to/screenshot.png"

        command = coordinator._build_command(screenshot_path)

        # Check that command contains expected parts
        self.assertIn("opencode", command)
        self.assertIn("run", command)
        self.assertIn("-m", command)
        self.assertIn("ollama-cloud/qwen3.5:397b", command)
        self.assertIn("-f", command)
        self.assertIn(screenshot_path, command)
        self.assertIn(coordinator.prompt, command)

    def test_build_command_no_shell_escaping_needed(self):
        """Test that quotes in prompt don't need escaping with list format."""
        custom_prompt = 'Say "hello" to test'
        coordinator = SubagentCoordinator(prompt=custom_prompt)

        command = coordinator._build_command("/test.png")

        # With list format, quotes don't need escaping
        self.assertIn(custom_prompt, command)


class TestSubagentCoordinatorParseResponse(unittest.TestCase):
    """Tests for _parse_response method."""

    def setUp(self):
        self.coordinator = SubagentCoordinator()

    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        valid_json = json.dumps({
            "input_box": [0.1, 0.2, 0.3, 0.4],
            "send_button": [0.5, 0.6, 0.7, 0.8],
            "headline_article_button": [0.1, 0.5, 0.2, 0.6]
        })

        result = self.coordinator._parse_response(valid_json)

        self.assertEqual(result["input_box"], [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(result["send_button"], [0.5, 0.6, 0.7, 0.8])
        self.assertEqual(result["headline_article_button"], [0.1, 0.5, 0.2, 0.6])

    def test_parse_response_with_null(self):
        """Test parsing JSON with null values."""
        json_with_null = json.dumps({
            "input_box": [0.1, 0.2, 0.3, 0.4],
            "send_button": [0.5, 0.6, 0.7, 0.8],
            "headline_article_button": None
        })

        result = self.coordinator._parse_response(json_with_null)

        self.assertEqual(result["input_box"], [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(result["send_button"], [0.5, 0.6, 0.7, 0.8])
        self.assertIsNone(result["headline_article_button"])

    def test_parse_response_with_extra_text(self):
        """Test parsing JSON embedded in extra text."""
        response_with_extra = """
        Here is the analysis result:
        {
          "input_box": [0.1, 0.2, 0.3, 0.4],
          "send_button": [0.5, 0.6, 0.7, 0.8],
          "headline_article_button": null
        }
        Hope this helps!
        """

        result = self.coordinator._parse_response(response_with_extra)

        self.assertEqual(result["input_box"], [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(result["send_button"], [0.5, 0.6, 0.7, 0.8])
        self.assertIsNone(result["headline_article_button"])

    def test_parse_response_invalid_json_raises_parse_error(self):
        """Test that invalid JSON raises ParseError."""
        invalid_json = "This is not valid JSON"

        with self.assertRaises(ParseError) as context:
            self.coordinator._parse_response(invalid_json)

        self.assertIn("Failed to parse JSON", str(context.exception))

    def test_parse_error_is_subagent_error(self):
        """Test that ParseError can be caught as SubagentError."""
        invalid_json = "This is not valid JSON"

        with self.assertRaises(SubagentError):
            self.coordinator._parse_response(invalid_json)


class TestSubagentCoordinatorValidateAndNormalize(unittest.TestCase):
    """Tests for _validate_and_normalize method."""

    def setUp(self):
        self.coordinator = SubagentCoordinator()

    def test_validate_and_normalize_valid(self):
        """Test validation with valid coordinates."""
        data = {
            "input_box": [0.1, 0.2, 0.3, 0.4],
            "send_button": [0.5, 0.6, 0.7, 0.8],
            "headline_article_button": [0.1, 0.5, 0.2, 0.6]
        }

        result = self.coordinator._validate_and_normalize(data)

        self.assertEqual(result["input_box"], [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(result["send_button"], [0.5, 0.6, 0.7, 0.8])
        self.assertEqual(result["headline_article_button"], [0.1, 0.5, 0.2, 0.6])

    def test_validate_and_normalize_missing_required_raises_validation_error(self):
        """Test validation with missing required keys raises ValidationError."""
        data = {
            "input_box": [0.1, 0.2, 0.3, 0.4]
            # Missing send_button
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("Missing required key", str(context.exception))

    def test_validate_and_normalize_null_required_raises_validation_error(self):
        """Test validation with null required values raises ValidationError."""
        data = {
            "input_box": None,
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("cannot be null", str(context.exception))

    def test_validation_error_can_be_caught_as_subagent_error(self):
        """Test that ValidationError can be caught as SubagentError."""
        data = {
            "input_box": [0.1, 0.2, 0.3, 0.4]
            # Missing send_button
        }

        with self.assertRaises(SubagentError):
            self.coordinator._validate_and_normalize(data)

    def test_validate_and_normalize_invalid_range(self):
        """Test validation with coordinates outside 0-1 range."""
        data = {
            "input_box": [1.5, 0.2, 0.3, 0.4],  # X1 > 1
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("Invalid coordinate range", str(context.exception))

    def test_validate_and_normalize_negative_range(self):
        """Test validation with negative coordinates."""
        data = {
            "input_box": [-0.1, 0.2, 0.3, 0.4],  # X1 < 0
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("Invalid coordinate range", str(context.exception))

    def test_validate_and_normalize_wrong_order_x(self):
        """Test validation with X1 >= X2."""
        data = {
            "input_box": [0.5, 0.2, 0.3, 0.4],  # X1 > X2
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("X1", str(context.exception))
        self.assertIn("must be less than X2", str(context.exception))

    def test_validate_and_normalize_wrong_order_y(self):
        """Test validation with Y1 >= Y2."""
        data = {
            "input_box": [0.1, 0.5, 0.3, 0.4],  # Y1 > Y2
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("Y1", str(context.exception))
        self.assertIn("must be less than Y2", str(context.exception))

    def test_validate_and_normalize_equal_coordinates(self):
        """Test validation with X1 == X2."""
        data = {
            "input_box": [0.3, 0.2, 0.3, 0.4],  # X1 == X2
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("must be less than", str(context.exception))

    def test_validate_and_normalize_optional_null(self):
        """Test validation with null optional field."""
        data = {
            "input_box": [0.1, 0.2, 0.3, 0.4],
            "send_button": [0.5, 0.6, 0.7, 0.8],
            "headline_article_button": None
        }

        result = self.coordinator._validate_and_normalize(data)

        self.assertIsNone(result["headline_article_button"])

    def test_validate_and_normalize_missing_optional(self):
        """Test validation with missing optional field."""
        data = {
            "input_box": [0.1, 0.2, 0.3, 0.4],
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        result = self.coordinator._validate_and_normalize(data)

        self.assertIsNone(result["headline_article_button"])

    def test_validate_and_normalize_wrong_format(self):
        """Test validation with wrong coordinate format."""
        data = {
            "input_box": [0.1, 0.2],  # Only 2 values
            "send_button": [0.5, 0.6, 0.7, 0.8]
        }

        with self.assertRaises(ValidationError) as context:
            self.coordinator._validate_and_normalize(data)

        self.assertIn("Invalid coordinate format", str(context.exception))


class TestSubagentCoordinatorAnalyzeScreenshot(unittest.TestCase):
    """Tests for analyze_screenshot method with mocked subprocess."""

    def setUp(self):
        self.coordinator = SubagentCoordinator()
        self.valid_response = json.dumps({
            "input_box": [0.1, 0.2, 0.3, 0.4],
            "send_button": [0.5, 0.6, 0.7, 0.8],
            "headline_article_button": None
        })

    @patch('lib.subagent_coordinator.subprocess.run')
    def test_analyze_screenshot_success(self, mock_run):
        """Test successful screenshot analysis."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=self.valid_response,
            stderr=""
        )

        result = self.coordinator.analyze_screenshot("/path/to/screenshot.png")

        self.assertEqual(result["input_box"], [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(result["send_button"], [0.5, 0.6, 0.7, 0.8])
        self.assertIsNone(result["headline_article_button"])

        # Verify subprocess was called with list and shell=False
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        self.assertIsInstance(call_args[0][0], list)  # First positional arg is list
        self.assertEqual(call_args[1].get('shell'), False)  # shell=False

    @patch('lib.subagent_coordinator.subprocess.run')
    def test_analyze_screenshot_retry_on_parse_failure(self, mock_run):
        """Test retry logic on parse failure."""
        # First call fails with invalid JSON, second succeeds
        mock_run.side_effect = [
            Mock(returncode=0, stdout="invalid json", stderr=""),
            Mock(returncode=0, stdout=self.valid_response, stderr="")
        ]

        result = self.coordinator.analyze_screenshot("/path/to/screenshot.png", max_retries=3)

        self.assertEqual(result["input_box"], [0.1, 0.2, 0.3, 0.4])
        # Should have been called twice
        self.assertEqual(mock_run.call_count, 2)

    @patch('lib.subagent_coordinator.subprocess.run')
    @patch('lib.subagent_coordinator.time.sleep')
    def test_analyze_screenshot_exhaust_retries(self, mock_sleep, mock_run):
        """Test that exception is raised when all retries are exhausted."""
        # All calls fail with parse error
        mock_run.return_value = Mock(returncode=0, stdout="invalid json", stderr="")

        with self.assertRaises(SubagentError) as context:
            self.coordinator.analyze_screenshot("/path/to/screenshot.png", max_retries=3)

        self.assertIn("failed after 3 attempts", str(context.exception))
        # Should have been called 3 times
        self.assertEqual(mock_run.call_count, 3)

    @patch('lib.subagent_coordinator.subprocess.run')
    def test_analyze_screenshot_no_retry_on_validation_error(self, mock_run):
        """Test that validation errors don't trigger retry."""
        invalid_response = json.dumps({
            "input_box": [1.5, 0.2, 0.3, 0.4],  # Invalid range
            "send_button": [0.5, 0.6, 0.7, 0.8]
        })
        mock_run.return_value = Mock(returncode=0, stdout=invalid_response, stderr="")

        with self.assertRaises(ValidationError) as context:
            self.coordinator.analyze_screenshot("/path/to/screenshot.png", max_retries=3)

        self.assertIn("Invalid coordinate range", str(context.exception))
        # Should only be called once (no retry on validation error)
        self.assertEqual(mock_run.call_count, 1)

    @patch('lib.subagent_coordinator.subprocess.run')
    def test_analyze_screenshot_no_retry_on_missing_key(self, mock_run):
        """Test that missing key errors don't trigger retry."""
        invalid_response = json.dumps({
            "input_box": [0.1, 0.2, 0.3, 0.4]
            # Missing send_button
        })
        mock_run.return_value = Mock(returncode=0, stdout=invalid_response, stderr="")

        with self.assertRaises(ValidationError) as context:
            self.coordinator.analyze_screenshot("/path/to/screenshot.png", max_retries=3)

        self.assertIn("Missing required key", str(context.exception))
        # Should only be called once
        self.assertEqual(mock_run.call_count, 1)

    @patch('lib.subagent_coordinator.subprocess.run')
    def test_analyze_screenshot_command_failure(self, mock_run):
        """Test handling of command failure."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Command failed")

        with self.assertRaises(SubagentError) as context:
            self.coordinator.analyze_screenshot("/path/to/screenshot.png", max_retries=1)

        self.assertIn("Command failed", str(context.exception))

    @patch('lib.subagent_coordinator.subprocess.run')
    def test_analyze_screenshot_timeout(self, mock_run):
        """Test handling of command timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 60)

        with self.assertRaises(SubagentError) as context:
            self.coordinator.analyze_screenshot("/path/to/screenshot.png", max_retries=1)

        self.assertIn("timed out", str(context.exception))


class TestSubagentError(unittest.TestCase):
    """Tests for SubagentError exception."""

    def test_subagent_error_is_exception(self):
        """Test that SubagentError is an Exception subclass."""
        self.assertTrue(issubclass(SubagentError, Exception))

    def test_subagent_error_message(self):
        """Test SubagentError message."""
        error = SubagentError("Test error message")
        self.assertEqual(str(error), "Test error message")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
