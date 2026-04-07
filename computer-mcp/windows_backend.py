import time
import pyautogui
from typing import Any


def list_windows() -> list[dict[str, Any]]:
    """Return visible top-level windows with title and handle."""
    import ctypes
    import ctypes.wintypes

    result = []

    def enum_handler(hwnd, _):
        try:
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value
                    if title:
                        result.append({"title": title, "handle": hwnd})
        except Exception:
            pass
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_handler), 0)
    return result


def focus_window(title: str) -> dict[str, Any]:
    """Bring window matching title substring to foreground."""
    windows = list_windows()
    for w in windows:
        if title.lower() in w["title"].lower():
            import ctypes
            hwnd = w["handle"]
            ctypes.windll.user32.ShowWindow(hwnd, 9)   # SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            return {"success": True, "title": w["title"]}
    raise ValueError(f"Window '{title}' not found")


def get_cursor() -> dict[str, int]:
    """Return current mouse cursor position."""
    x, y = pyautogui.position()
    return {"x": x, "y": y}


def click(x: int, y: int, button: str = "left") -> dict[str, Any]:
    pyautogui.click(x, y, button=button)
    return {"success": True, "x": x, "y": y, "button": button}


def double_click(x: int, y: int) -> dict[str, Any]:
    pyautogui.doubleClick(x, y)
    return {"success": True, "x": x, "y": y}


def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.3) -> dict[str, Any]:
    pyautogui.moveTo(x1, y1)
    pyautogui.dragTo(x2, y2, duration=duration, button="left")
    return {"success": True, "from": [x1, y1], "to": [x2, y2]}


def type_text(text: str, interval: float = 0.03) -> dict[str, Any]:
    pyautogui.typewrite(text, interval=interval)
    return {"success": True, "length": len(text)}


def press_key(key: str) -> dict[str, Any]:
    pyautogui.press(key)
    return {"success": True, "key": key}


def hotkey(*keys: str) -> dict[str, Any]:
    pyautogui.hotkey(*keys)
    return {"success": True, "keys": list(keys)}


def scroll(x: int, y: int, clicks: int) -> dict[str, Any]:
    """Scroll at (x, y). Positive clicks = up, negative = down."""
    pyautogui.moveTo(x, y)
    pyautogui.scroll(clicks)
    return {"success": True, "x": x, "y": y, "clicks": clicks}


def wait(seconds: float) -> dict[str, Any]:
    time.sleep(seconds)
    return {"success": True, "waited": seconds}
