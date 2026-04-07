"""
computer-mcp: Desktop control MCP server for power-media.
Run: python computer-mcp/server.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from windows_backend import (
    list_windows, focus_window, get_cursor,
    click, double_click, drag,
    type_text, press_key, hotkey,
    scroll, wait,
)
from screen_inspector import take_screenshot, inspect_screen
from confirm_guard import request_confirm
from logger import ActionLogger

log = ActionLogger()
mcp = FastMCP("computer-mcp")


@mcp.tool()
def tool_screenshot(region_top: int = 0, region_left: int = 0,
                    region_width: int = 0, region_height: int = 0) -> dict:
    """Take a screenshot. Pass all zeros for full screen."""
    region = None
    if region_width > 0 and region_height > 0:
        region = {"top": region_top, "left": region_left,
                  "width": region_width, "height": region_height}
    result = take_screenshot(region)
    log.record("screenshot", {"region": region})
    return result


@mcp.tool()
def tool_inspect_screen(region_top: int = 0, region_left: int = 0,
                        region_width: int = 0, region_height: int = 0) -> dict:
    """Screenshot + OCR. Returns text blocks with bounding boxes and confidence."""
    region = None
    if region_width > 0 and region_height > 0:
        region = {"top": region_top, "left": region_left,
                  "width": region_width, "height": region_height}
    result = inspect_screen(region)
    log.record("inspect_screen", {"region": region})
    return result


@mcp.tool()
def tool_list_windows() -> dict:
    """List visible top-level windows."""
    result = list_windows()
    log.record("list_windows", {})
    return {"windows": result}


@mcp.tool()
def tool_focus_window(title: str) -> dict:
    """Bring window matching title substring to foreground."""
    result = focus_window(title)
    log.record("focus_window", {"title": title})
    return result


@mcp.tool()
def tool_get_cursor() -> dict:
    """Return current mouse cursor position."""
    result = get_cursor()
    log.record("get_cursor", {})
    return result


@mcp.tool()
def tool_click(x: int, y: int, button: str = "left") -> dict:
    """Click at screen coordinates."""
    result = click(x, y, button)
    log.record("click", {"x": x, "y": y, "button": button})
    return result


@mcp.tool()
def tool_double_click(x: int, y: int) -> dict:
    """Double-click at screen coordinates."""
    result = double_click(x, y)
    log.record("double_click", {"x": x, "y": y})
    return result


@mcp.tool()
def tool_drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.3) -> dict:
    """Drag from (x1,y1) to (x2,y2)."""
    result = drag(x1, y1, x2, y2, duration)
    log.record("drag", {"from": [x1, y1], "to": [x2, y2]})
    return result


@mcp.tool()
def tool_type_text(text: str, secret: bool = False) -> dict:
    """Type text. Set secret=True to suppress logging."""
    result = type_text(text)
    log.record("type_text", {"text": text, "secret": secret})
    return result


@mcp.tool()
def tool_press_key(key: str) -> dict:
    """Press a single key, e.g. 'enter', 'tab', 'escape'."""
    result = press_key(key)
    log.record("press_key", {"key": key})
    return result


@mcp.tool()
def tool_hotkey(keys: str) -> dict:
    """Press a hotkey combo, space-separated e.g. 'ctrl c' or 'ctrl shift t'."""
    key_list = keys.split()
    result = hotkey(*key_list)
    log.record("hotkey", {"keys": keys})
    return result


@mcp.tool()
def tool_scroll(x: int, y: int, clicks: int) -> dict:
    """Scroll at (x,y). Positive=up, negative=down."""
    result = scroll(x, y, clicks)
    log.record("scroll", {"x": x, "y": y, "clicks": clicks})
    return result


@mcp.tool()
def tool_wait(seconds: float) -> dict:
    """Wait for given seconds."""
    result = wait(seconds)
    log.record("wait", {"seconds": seconds})
    return result


@mcp.tool()
def tool_confirm_action(action_description: str) -> dict:
    """
    Request human confirmation before executing high-risk actions
    such as publish, delete, or submit.
    """
    result = request_confirm(action_description)
    log.record("confirm_action", {"action": action_description})
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
