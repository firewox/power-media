"""
Isolated Browser Manager.
Finds/launches browser windows and moves them to isolated virtual desktops.
"""

import ctypes
import ctypes.wintypes
import subprocess
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserNotFoundError(Exception):
    """Browser not found"""
    pass


# Common browser window class names
BROWSER_CLASS_NAMES = [
    "Chrome_WidgetWin_1",      # Chrome, Edge, Brave, etc.
    "MozillaWindowClass",     # Firefox
    "OperaWindowClass",       # Opera
    "Chrome_WidgetWin_0",     # Some Chrome variants
]

# Browser executable paths (Windows)
BROWSER_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_browser_window() -> Optional[dict]:
    """
    Find existing browser window.

    Returns:
        {"hwnd": int, "title": str, "class": str} or None
    """
    try:
        import win32gui
    except ImportError:
        logger.warning("pywin32 not installed, cannot find browser window")
        return None

    def enum_callback(hwnd, results):
        try:
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True

            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True

            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value

            if not title:
                return True

            class_name = win32gui.GetClassName(hwnd)

            if class_name in BROWSER_CLASS_NAMES:
                results.append({
                    "hwnd": hwnd,
                    "title": title,
                    "class": class_name
                })

        except Exception as e:
            logger.debug(f"Error enumerating window {hwnd}: {e}")

        return True

    results = []
    win32gui.EnumWindows(enum_callback, results)

    if results:
        logger.info(f"Found browser window: {results[0]}")
        return results[0]

    return None


def launch_new_browser(url: Optional[str] = None) -> dict:
    """
    Launch a new browser window.

    Args:
        url: URL to open

    Returns:
        {"hwnd": int, "title": str}
    """
    browser_path = None
    for path in BROWSER_PATHS:
        if ctypes.windll.kernel32.GetFileAttributesW(path) != 0xFFFFFFFF:
            browser_path = path
            break

    if not browser_path:
        raise BrowserNotFoundError(
            "未找到 Chrome 或 Edge 浏览器。\n"
            "请安装 Chrome 或 Edge,或在 isolated_browser.py 中配置浏览器路径。"
        )

    cmd = [browser_path, "--new-window"]
    if url:
        cmd.append(url)

    logger.info(f"Launching browser: {' '.join(cmd)}")
    subprocess.Popen(cmd)

    # Wait for window to appear
    time.sleep(2)

    window = find_browser_window()
    if window:
        return window

    raise BrowserNotFoundError("浏览器启动后未找到窗口")


class IsolatedBrowser:
    """Isolated browser manager"""

    def __init__(self, desktop_manager):
        """
        Args:
            desktop_manager: VirtualDesktopManager instance
        """
        self.desktop_manager = desktop_manager
        self.desktop_id: Optional[str] = None
        self.window_hwnd: Optional[int] = None

    def setup(self, url: Optional[str] = None) -> int:
        """
        Initialize isolated browser environment.

        Args:
            url: URL to open (optional)

        Returns:
            hwnd: Browser window handle
        """
        # 1. Create virtual desktop
        self.desktop_id = self.desktop_manager.create_desktop(
            "power-media-isolated"
        )
        logger.info(f"Created isolated desktop: {self.desktop_id}")

        # 2. Find or launch browser
        self.window_hwnd = self.launch_or_locate(url)
        logger.info(f"Browser window hwnd: {self.window_hwnd}")

        # 3. Move to isolated desktop
        self.move_to_isolated_desktop()

        return self.window_hwnd

    def launch_or_locate(self, url: Optional[str] = None) -> int:
        """
        Launch new browser window or find existing one.

        Args:
            url: URL to open (optional)

        Returns:
            hwnd: Window handle
        """
        # Try to find existing window first
        window = find_browser_window()
        if window:
            logger.info(
                f"Found existing browser window: {window['title']}"
            )
            self.window_hwnd = window["hwnd"]
            return self.window_hwnd

        # Launch new window
        logger.info("No existing browser window found, launching new one")
        window = launch_new_browser(url)
        self.window_hwnd = window["hwnd"]
        return self.window_hwnd

    def move_to_isolated_desktop(self) -> None:
        """Move browser window to isolated virtual desktop"""
        if not self.desktop_id or not self.window_hwnd:
            raise RuntimeError(
                "desktop_id and window_hwnd must be set first"
            )

        self.desktop_manager.move_window_to_desktop(
            self.window_hwnd, self.desktop_id
        )
        logger.info("Moved browser window to isolated desktop")

    def get_window_rect(self) -> dict:
        """
        Get browser window client area.

        Returns:
            {"left": int, "top": int, "width": int, "height": int}
        """
        if not self.window_hwnd:
            raise RuntimeError("window_hwnd not set")

        try:
            import win32gui

            rect = win32gui.GetWindowRect(self.window_hwnd)
            left, top, right, bottom = rect

            client_rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetClientRect(
                self.window_hwnd, ctypes.byref(client_rect)
            )

            width = client_rect.right - client_rect.left
            height = client_rect.bottom - client_rect.top

            return {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            }

        except Exception as e:
            logger.error(f"Failed to get window rect: {e}")
            return {
                "left": 0,
                "top": 0,
                "width": 1920,
                "height": 1080,
            }

    def ensure_restored(self) -> None:
        """Ensure window is restored (not minimized/maximized)"""
        if not self.window_hwnd:
            raise RuntimeError("window_hwnd not set")

        # SW_RESTORE = 9
        ctypes.windll.user32.ShowWindow(self.window_hwnd, 9)
        time.sleep(0.1)

    def ensure_minimized(self) -> None:
        """Ensure window is minimized"""
        if not self.window_hwnd:
            raise RuntimeError("window_hwnd not set")

        # SW_MINIMIZE = 6
        ctypes.windll.user32.ShowWindow(self.window_hwnd, 6)
        time.sleep(0.1)

    def is_alive(self) -> bool:
        """Check if window is still alive"""
        if not self.window_hwnd:
            return False

        try:
            return bool(
                ctypes.windll.user32.IsWindow(self.window_hwnd)
            )
        except Exception:
            return False

    def cleanup(self) -> None:
        """Cleanup isolated browser environment"""
        logger.info("Cleaning up isolated browser")

        # Optionally close window
        if self.window_hwnd and self.is_alive():
            try:
                # WM_CLOSE = 0x0010
                ctypes.windll.user32.PostMessageW(
                    self.window_hwnd, 0x0010, 0, 0
                )
                logger.info(f"Closed browser window {self.window_hwnd}")
            except Exception as e:
                logger.warning(f"Failed to close browser window: {e}")

        self.window_hwnd = None
        self.desktop_id = None
