"""
Isolated Computer MCP Server.
Provides desktop-isolated browser control tools.
Run: python isolated-mcp/server.py
"""

import sys
import os
import functools

# Add paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.fastmcp import FastMCP
from virtual_desktop import VirtualDesktopManager, VirtualDesktopError
from isolated_browser import IsolatedBrowser, BrowserNotFoundError
from isolated_operations import IsolatedOperation

# Import from existing computer-mcp
from computer_mcp.screen_inspector import take_screenshot, inspect_screen
from computer_mcp.windows_backend import (
    click, double_click, drag, type_text,
    press_key, hotkey, scroll, wait, get_cursor
)
from computer_mcp.confirm_guard import request_confirm
from computer_mcp.logger import ActionLogger

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

log = ActionLogger()
mcp = FastMCP("isolated-computer-mcp")

# Global isolated manager (lazy init)
_desktop_manager = None
_browser = None


def get_desktop_manager() -> VirtualDesktopManager:
    """Get or create virtual desktop manager"""
    global _desktop_manager
    if _desktop_manager is None:
        _desktop_manager = VirtualDesktopManager()
    return _desktop_manager


def get_browser() -> IsolatedBrowser:
    """Get isolated browser instance"""
    global _browser
    if _browser is None:
        _browser = IsolatedBrowser(get_desktop_manager())
    return _browser


def isolated_tool(func):
    """Isolated tool decorator: auto-handles desktop switching"""
    def wrapper(*args, **kwargs):
        browser = get_browser()
        desktop_manager = get_desktop_manager()

        iso_op = IsolatedOperation(
            desktop_manager, browser, func
        )
        return iso_op.execute(*args, **kwargs)

    return functools.wraps(func)(wrapper)


@mcp.tool()
def tool_init_isolated(browser_url: str = None) -> dict:
    """
    Initialize isolated environment.
    Creates virtual desktop and positions browser window.

    Args:
        browser_url: URL to open in browser (optional)

    Returns:
        {"success": bool, "desktop_id": str, "window_hwnd": int}
    """
    try:
        browser = get_browser()
        hwnd = browser.setup(browser_url)

        result = {
            "success": True,
            "desktop_id": browser.desktop_id,
            "window_hwnd": hwnd,
            "message": "Isolated environment initialized"
        }
        log.record("init_isolated", result)
        return result

    except (VirtualDesktopError, BrowserNotFoundError) as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to initialize isolated environment"
        }


@mcp.tool()
def tool_screenshot(
    region_top: int = 0, region_left: int = 0,
    region_width: int = 0, region_height: int = 0
) -> dict:
    """
    Take screenshot in isolated environment.
    Automatically switches to isolated desktop, captures, then switches back.
    Pass all zeros for full screen.
    """
    def _screenshot():
        region = None
        if region_width > 0 and region_height > 0:
            region = {
                "top": region_top,
                "left": region_left,
                "width": region_width,
                "height": region_height
            }
        return take_screenshot(region)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _screenshot)
    result = iso_op.execute()

    log.record("isolated_screenshot", {
        "region": region_top > 0 and {
            "top": region_top,
            "left": region_left,
            "width": region_width,
            "height": region_height
        } or None
    })
    return result


@mcp.tool()
def tool_inspect_screen(
    region_top: int = 0, region_left: int = 0,
    region_width: int = 0, region_height: int = 0
) -> dict:
    """Screenshot + OCR in isolated environment."""
    def _inspect():
        region = None
        if region_width > 0 and region_height > 0:
            region = {
                "top": region_top,
                "left": region_left,
                "width": region_width,
                "height": region_height
            }
        return inspect_screen(region)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _inspect)
    result = iso_op.execute()

    log.record("isolated_inspect_screen", {})
    return result


@mcp.tool()
def tool_click(x: int, y: int, button: str = "left") -> dict:
    """Click at screen coordinates in isolated environment."""
    def _click():
        return click(x, y, button)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _click)
    result = iso_op.execute()

    log.record("isolated_click", {
        "x": x, "y": y, "button": button
    })
    return result


@mcp.tool()
def tool_double_click(x: int, y: int) -> dict:
    """Double-click at screen coordinates in isolated environment."""
    def _double_click():
        return double_click(x, y)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _double_click)
    result = iso_op.execute()

    log.record("isolated_double_click", {"x": x, "y": y})
    return result


@mcp.tool()
def tool_drag(
    x1: int, y1: int, x2: int, y2: int, duration: float = 0.3
) -> dict:
    """Drag from (x1,y1) to (x2,y2) in isolated environment."""
    def _drag():
        return drag(x1, y1, x2, y2, duration)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _drag)
    result = iso_op.execute()

    log.record("isolated_drag", {
        "from": [x1, y1], "to": [x2, y2]
    })
    return result


@mcp.tool()
def tool_type_text(text: str, secret: bool = False) -> dict:
    """Type text in isolated environment."""
    def _type():
        return type_text(text)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _type)
    result = iso_op.execute()

    log.record("isolated_type_text", {
        "text": text, "secret": secret
    })
    return result


@mcp.tool()
def tool_press_key(key: str) -> dict:
    """Press a single key in isolated environment."""
    def _press():
        return press_key(key)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _press)
    result = iso_op.execute()

    log.record("isolated_press_key", {"key": key})
    return result


@mcp.tool()
def tool_hotkey(keys: str) -> dict:
    """Press hotkey combo in isolated environment, e.g. 'ctrl c'."""
    def _hotkey():
        return hotkey(*keys.split())

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _hotkey)
    result = iso_op.execute()

    log.record("isolated_hotkey", {"keys": keys})
    return result


@mcp.tool()
def tool_scroll(x: int, y: int, clicks: int) -> dict:
    """Scroll at (x,y) in isolated environment."""
    def _scroll():
        return scroll(x, y, clicks)

    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _scroll)
    result = iso_op.execute()

    log.record("isolated_scroll", {
        "x": x, "y": y, "clicks": clicks
    })
    return result


@mcp.tool()
def tool_wait(seconds: float) -> dict:
    """Wait for given seconds."""
    result = wait(seconds)
    log.record("isolated_wait", {"seconds": seconds})
    return result


@mcp.tool()
def tool_get_browser_rect() -> dict:
    """Get isolated browser window rectangle for coordinate mapping."""
    browser = get_browser()
    if not browser.window_hwnd:
        return {
            "success": False,
            "error": "Browser not initialized"
        }

    rect = browser.get_window_rect()
    return {
        "success": True,
        "window_hwnd": browser.window_hwnd,
        **rect
    }


@mcp.tool()
def tool_confirm_action(action_description: str) -> dict:
    """
    Request human confirmation.
    Works on current desktop (not isolated).
    """
    result = request_confirm(action_description)
    log.record("isolated_confirm_action", {
        "action": action_description
    })
    return result


@mcp.tool()
def tool_cleanup_isolated() -> dict:
    """
    Cleanup isolated environment.
    Closes browser window and removes virtual desktop.
    """
    global _browser, _desktop_manager

    try:
        browser = get_browser()
        desktop_manager = get_desktop_manager()

        # Close window
        browser.cleanup()

        # Cleanup virtual desktop
        if browser.desktop_id:
            desktop_manager.cleanup([browser.desktop_id])

        # Reset globals
        _browser = None
        _desktop_manager = None

        result = {
            "success": True,
            "message": "Isolated environment cleaned up"
        }
        log.record("cleanup_isolated", result)
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to cleanup isolated environment"
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
