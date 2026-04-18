"""
SubagentCoordinator - Manages opencode subagent execution with retry logic.

This module provides a coordinator class to execute subagents for screenshot analysis,
with proper error handling, retry logic, and coordinate validation.
"""

import json
import re
import subprocess
import time
from typing import Optional


class SubagentError(Exception):
    """Custom exception for subagent execution failures."""
    pass


class ValidationError(SubagentError):
    """Raised when validation fails - don't retry."""
    pass


class ParseError(SubagentError):
    """Raised when parsing fails - retry allowed."""
    pass


class SubagentCoordinator:
    """
    Coordinator for managing opencode subagent execution.

    Handles building commands, executing subagents, parsing responses,
    and implementing retry logic with exponential backoff.
    """

    DEFAULT_PROMPT = """请识别这张微博主页截图中的微博发文文本输入框、发送按钮、头条文章按钮，以纯JSON格式返回结果，无多余描述。

坐标使用归一化小数格式 [X1,Y1,X2,Y2]，数值范围 0~1，代表元素相对于整张图片的左上角与右下角位置。

返回格式：
{
  "input_box": [X1,Y1,X2,Y2],
  "send_button": [X1,Y1,X2,Y2],
  "headline_article_button": [X1,Y1,X2,Y2]
}

注意：
1. 只返回JSON，不要任何其他文字
2. 坐标必须是0-1之间的浮点数
3. [X1,Y1]是左上角，[X2,Y2]是右下角
4. 如果某个元素找不到，返回null
"""

    def __init__(
        self,
        model: str = "ollama-cloud/qwen3.5:397b",
        timeout: int = 120,  # 增加到120秒
        prompt: Optional[str] = None
    ):
        """
        Initialize the SubagentCoordinator.

        Args:
            model: The model to use for the subagent (default: ollama-cloud/qwen3.5:397b)
            timeout: Command timeout in seconds (default: 60)
            prompt: Custom prompt template (default: DEFAULT_PROMPT)
        """
        self.model = model
        self.timeout = timeout
        self.prompt = prompt or self.DEFAULT_PROMPT

    def _build_command(self, screenshot_path: str) -> list:
        """
        Build the opencode command as a list for safe execution.

        Args:
            screenshot_path: Path to the screenshot file

        Returns:
            Command list ready for subprocess.run with shell=False
        """
        # 使用系统全局的 opencode（PowerShell 脚本）
        # opencode 安装在 D:\00_software\nodejs\opencode.ps1
        return [
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-File', r'D:\00_software\nodejs\opencode.ps1',
            'run',
            '-m', self.model,
            self.prompt,
            '-f', screenshot_path
        ]

    def _execute_command(self, command: list) -> str:
        """
        Execute the command and capture output.

        Args:
            command: The command list to execute

        Returns:
            The stdout from the command execution

        Raises:
            SubagentError: If the command times out or returns non-zero exit code
        """
        try:
            result = subprocess.run(
                command,
                shell=False,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise SubagentError(f"Subagent command failed with exit code {result.returncode}: {error_msg}")

            return result.stdout

        except subprocess.TimeoutExpired:
            raise SubagentError(f"Subagent command timed out after {self.timeout} seconds")
        except Exception as e:
            raise SubagentError(f"Failed to execute subagent command: {str(e)}")

    def _parse_response(self, output: str) -> dict:
        """
        Parse JSON response from subagent output.

        Handles cases where the output contains extra text before/after the JSON.

        Args:
            output: The raw output from the subagent

        Returns:
            Parsed JSON as a dictionary

        Raises:
            ParseError: If JSON parsing fails
        """
        # Try to find JSON in the output using regex
        # Look for content between { and }
        json_match = re.search(r'\{[\s\S]*\}', output)

        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = output

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ParseError(f"Failed to parse JSON response: {str(e)}. Output: {output[:200]}")

    def _validate_and_normalize(self, data: dict) -> dict:
        """
        Validate and normalize the parsed response data.

        Validates:
        - Required keys exist (input_box, send_button)
        - Coordinate ranges (0-1)
        - Coordinate order (X1 < X2, Y1 < Y2)

        Args:
            data: Parsed JSON data from subagent

        Returns:
            Validated and normalized data dictionary

        Raises:
            ValidationError: If validation fails
        """
        required_keys = ["input_box", "send_button"]
        optional_keys = ["headline_article_button"]

        result = {}

        # Check required keys
        for key in required_keys:
            if key not in data:
                raise ValidationError(f"Missing required key in response: {key}")

            value = data[key]

            # Handle null values for required keys (should not happen, but handle gracefully)
            if value is None:
                raise ValidationError(f"Required key '{key}' cannot be null")

            # Validate coordinates
            result[key] = self._validate_coordinates(value, key)

        # Check optional keys
        for key in optional_keys:
            if key in data:
                value = data[key]
                if value is None:
                    result[key] = None
                else:
                    result[key] = self._validate_coordinates(value, key)
            else:
                result[key] = None

        return result

    def _validate_coordinates(self, coords: list, key_name: str) -> list:
        """
        Validate coordinate array.

        Args:
            coords: List of 4 floats [X1, Y1, X2, Y2]
            key_name: Name of the key being validated (for error messages)

        Returns:
            Validated coordinate list

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(coords, list) or len(coords) != 4:
            raise ValidationError(
                f"Invalid coordinate format for '{key_name}': expected list of 4 floats, got {type(coords)}"
            )

        try:
            x1, y1, x2, y2 = float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3])
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid coordinate values for '{key_name}': {str(e)}"
            )

        # Validate ranges (0-1)
        for i, val in enumerate([x1, y1, x2, y2]):
            coord_name = ['X1', 'Y1', 'X2', 'Y2'][i]
            if not 0 <= val <= 1:
                raise ValidationError(
                    f"Invalid coordinate range for '{key_name}.{coord_name}': {val}. Must be between 0 and 1."
                )

        # Validate order (X1 < X2, Y1 < Y2)
        if x1 >= x2:
            raise ValidationError(
                f"Invalid coordinate order for '{key_name}': X1 ({x1}) must be less than X2 ({x2})"
            )

        if y1 >= y2:
            raise ValidationError(
                f"Invalid coordinate order for '{key_name}': Y1 ({y1}) must be less than Y2 ({y2})"
            )

        return [x1, y1, x2, y2]

    def analyze_screenshot(self, screenshot_path: str, max_retries: int = 3) -> dict:
        """
        Analyze a screenshot using the subagent with retry logic.

        Args:
            screenshot_path: Path to the screenshot file
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Dictionary containing detected elements with their coordinates:
            {
                "input_box": [X1, Y1, X2, Y2],
                "send_button": [X1, Y1, X2, Y2],
                "headline_article_button": [X1, Y1, X2, Y2] or None
            }

        Raises:
            SubagentError: If all retry attempts are exhausted or validation fails
        """
        command = self._build_command(screenshot_path)

        last_error = None
        # Note: No overall timeout protection implemented yet.
        # Max total time = sum(2^attempt) + max_retries * timeout
        # For max_retries=3, timeout=60: max ~7 + 180 = ~187 seconds

        for attempt in range(max_retries):
            try:
                # Execute command
                output = self._execute_command(command)

                # Parse response
                data = self._parse_response(output)

                # Validate and normalize
                result = self._validate_and_normalize(data)

                return result

            except ValidationError:
                # Don't retry on validation errors (invalid coordinates, missing keys)
                raise
            except SubagentError as e:
                last_error = e

                # Calculate backoff delay (exponential: 1s, 2s, 4s)
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    time.sleep(delay)

        # All retries exhausted
        raise SubagentError(
            f"Subagent failed after {max_retries} attempts. Last error: {last_error}"
        )
