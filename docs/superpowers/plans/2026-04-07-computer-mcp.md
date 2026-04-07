# Computer MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Python MCP server (`computer-mcp`) that lets AI control Windows browser windows via screenshot, OCR, mouse, keyboard, and window management tools.

**Architecture:** Python MCP server exposes 14 tools. Each tool delegates to one of three backend modules: `windows_backend` (input injection + window control), `screen_inspector` (screenshot + OCR + element detection), and `confirm_guard` (high-risk action gating). AI never calls OS APIs directly.

**Tech Stack:** Python 3.11+, `mcp` SDK (stdio transport), `mss` (screenshot), `pyautogui` (mouse/keyboard), `pywinauto` (window control), `easyocr` (OCR), `opencv-python` (image matching), `pytest` (tests)

---

## File Map

```
computer-mcp/
├── server.py                  # MCP server entry, tool registration
├── windows_backend.py         # mouse, keyboard, window focus
├── screen_inspector.py        # screenshot, OCR, element detection
├── confirm_guard.py           # confirm_action gating
├── logger.py                  # action logger (no sensitive data)
├── requirements.txt           # pinned deps
├── tests/
│   ├── test_windows_backend.py
│   ├── test_screen_inspector.py
│   └── test_confirm_guard.py
└── README.md
```

---

## Task 1: Project scaffold + requirements

**Files:**
- Create: `computer-mcp/requirements.txt`
- Create: `computer-mcp/README.md`

- [ ] **Step 1: Create requirements.txt**

```
mcp>=1.0.0
mss>=9.0.1
pyautogui>=0.9.54
pywinauto>=0.6.8
easyocr>=1.7.1
opencv-python>=4.9.0
Pillow>=10.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create README.md**

```markdown
# computer-mcp

Local MCP server that gives AI desktop control over Windows browser windows.

## Setup

```bash
cd computer-mcp
pip install -r requirements.txt
python server.py
```

## Tools

screenshot, list_windows, focus_window, click, double_click, drag,
type_text, press_key, hotkey, scroll, wait, inspect_screen,
get_cursor, confirm_action

## Usage with OpenCode / Claude

Add to your MCP config:
{
  "computer": {
    "command": "python",
    "args": ["computer-mcp/server.py"]
  }
}
```

- [ ] **Step 3: Install dependencies**

Run: `pip install -r computer-mcp/requirements.txt`
Expected: All packages install without error.

- [ ] **Step 4: Commit**

```bash
git add computer-mcp/requirements.txt computer-mcp/README.md
git commit -m "Add: computer-mcp scaffold and requirements"
```

---

## Task 2: Logger

**Files:**
- Create: `computer-mcp/logger.py`
- Create: `computer-mcp/tests/test_logger.py` (smoke only)

- [ ] **Step 1: Write failing test**

Create `computer-mcp/tests/test_logger.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from logger import ActionLogger

def test_log_action_returns_entry():
    log = ActionLogger(log_file=None)  # no file, in-memory only
    entry = log.record("click", {"x": 100, "y": 200})
    assert entry["tool"] == "click"
    assert entry["params"] == {"x": 100, "y": 200}
    assert "timestamp" in entry

def test_log_never_stores_password():
    log = ActionLogger(log_file=None)
    entry = log.record("type_text", {"text": "mypassword", "secret": True})
    assert entry["params"].get("text") == "[REDACTED]"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest computer-mcp/tests/test_logger.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'logger'`

- [ ] **Step 3: Implement logger.py**

Create `computer-mcp/logger.py`:

```python
import time
from typing import Any

class ActionLogger:
    def __init__(self, log_file: str | None = "computer-mcp.log"):
        self.log_file = log_file
        self.entries: list[dict] = []

    def record(self, tool: str, params: dict[str, Any]) -> dict:
        safe_params = self._redact(params)
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tool": tool,
            "params": safe_params,
        }
        self.entries.append(entry)
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(str(entry) + "\n")
        return entry

    def _redact(self, params: dict[str, Any]) -> dict[str, Any]:
        if params.get("secret"):
            return {**params, "text": "[REDACTED]"}
        return params
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest computer-mcp/tests/test_logger.py -v`
Expected: PASS — 2 tests passed.

- [ ] **Step 5: Commit**

```bash
git add computer-mcp/logger.py computer-mcp/tests/test_logger.py
git commit -m "Add: ActionLogger with secret redaction"
```

---

## Task 3: windows_backend — window list + focus

**Files:**
- Create: `computer-mcp/windows_backend.py`
- Create: `computer-mcp/tests/test_windows_backend.py`

- [ ] **Step 1: Write failing tests**

Create `computer-mcp/tests/test_windows_backend.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from windows_backend import list_windows, focus_window

def test_list_windows_returns_list():
    windows = list_windows()
    assert isinstance(windows, list)
    assert len(windows) > 0
    w = windows[0]
    assert "title" in w
    assert "handle" in w

def test_focus_window_unknown_title_raises():
    import pytest
    with pytest.raises(ValueError, match="not found"):
        focus_window("__nonexistent_window_xyzxyz__")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest computer-mcp/tests/test_windows_backend.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'windows_backend'`

- [ ] **Step 3: Implement list_windows and focus_window**

Create `computer-mcp/windows_backend.py`:

```python
import pyautogui
import pywinauto
from pywinauto import Desktop
from typing import Any

def list_windows() -> list[dict[str, Any]]:
    """Return visible top-level windows with title and handle."""
    desktop = Desktop(backend="uia")
    result = []
    for win in desktop.windows():
        try:
            title = win.window_text()
            handle = win.handle
            if title:
                result.append({"title": title, "handle": handle})
        except Exception:
            continue
    return result


def focus_window(title: str) -> dict[str, Any]:
    """Bring window matching title substring to foreground."""
    desktop = Desktop(backend="uia")
    for win in desktop.windows():
        try:
            if title.lower() in win.window_text().lower():
                win.set_focus()
                return {"success": True, "title": win.window_text()}
        except Exception:
            continue
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
    import time
    time.sleep(seconds)
    return {"success": True, "waited": seconds}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest computer-mcp/tests/test_windows_backend.py -v`
Expected: PASS — 2 tests passed.

- [ ] **Step 5: Commit**

```bash
git add computer-mcp/windows_backend.py computer-mcp/tests/test_windows_backend.py
git commit -m "Add: windows_backend with window list, focus, mouse and keyboard"
```

---

## Task 4: screen_inspector — screenshot + OCR

**Files:**
- Create: `computer-mcp/screen_inspector.py`
- Create: `computer-mcp/tests/test_screen_inspector.py`

- [ ] **Step 1: Write failing tests**

Create `computer-mcp/tests/test_screen_inspector.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from screen_inspector import take_screenshot, inspect_screen

def test_take_screenshot_returns_path():
    result = take_screenshot()
    assert result["success"] is True
    assert os.path.exists(result["path"])
    assert result["path"].endswith(".png")

def test_inspect_screen_returns_structure():
    result = inspect_screen()
    assert "screenshot_path" in result
    assert "ocr_blocks" in result
    assert isinstance(result["ocr_blocks"], list)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest computer-mcp/tests/test_screen_inspector.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'screen_inspector'`

- [ ] **Step 3: Implement screen_inspector.py**

Create `computer-mcp/screen_inspector.py`:

```python
import os
import time
import mss
import mss.tools
import easyocr
from typing import Any

_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
    return _reader


def take_screenshot(region: dict | None = None) -> dict[str, Any]:
    """
    Capture screen. region: {top, left, width, height} or None for fullscreen.
    Returns {"success": True, "path": "...", "width": N, "height": N}
    """
    os.makedirs("computer-mcp/screenshots", exist_ok=True)
    filename = f"computer-mcp/screenshots/shot_{int(time.time()*1000)}.png"
    with mss.mss() as sct:
        monitor = region if region else sct.monitors[0]
        shot = sct.grab(monitor)
        mss.tools.to_png(shot.rgb, shot.size, output=filename)
    return {
        "success": True,
        "path": filename,
        "width": shot.size[0],
        "height": shot.size[1],
    }


def inspect_screen(region: dict | None = None) -> dict[str, Any]:
    """
    Screenshot + OCR. Returns screenshot path and list of OCR text blocks.
    Each block: {"text": str, "bbox": [[x,y], ...], "confidence": float}
    """
    shot = take_screenshot(region)
    reader = _get_reader()
    raw = reader.readtext(shot["path"])
    blocks = [
        {
            "text": text,
            "bbox": bbox,
            "confidence": round(float(conf), 3),
        }
        for bbox, text, conf in raw
    ]
    return {
        "screenshot_path": shot["path"],
        "width": shot["width"],
        "height": shot["height"],
        "ocr_blocks": blocks,
    }
```

- [ ] **Step 4: Run tests**

Run: `pytest computer-mcp/tests/test_screen_inspector.py -v`
Expected: PASS — 2 tests passed. (First run will download EasyOCR model, may take a minute.)

- [ ] **Step 5: Commit**

```bash
git add computer-mcp/screen_inspector.py computer-mcp/tests/test_screen_inspector.py
git commit -m "Add: screen_inspector with screenshot and OCR"
```

---

## Task 5: confirm_guard — high-risk action gating

**Files:**
- Create: `computer-mcp/confirm_guard.py`
- Create: `computer-mcp/tests/test_confirm_guard.py`

- [ ] **Step 1: Write failing tests**

Create `computer-mcp/tests/test_confirm_guard.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from confirm_guard import request_confirm, ConfirmationDenied

def test_confirm_auto_approve(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    result = request_confirm("publish post to weibo")
    assert result["confirmed"] is True

def test_confirm_auto_deny(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    import pytest
    with pytest.raises(ConfirmationDenied):
        request_confirm("delete all drafts")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest computer-mcp/tests/test_confirm_guard.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'confirm_guard'`

- [ ] **Step 3: Implement confirm_guard.py**

Create `computer-mcp/confirm_guard.py`:

```python
class ConfirmationDenied(Exception):
    pass


def request_confirm(action_description: str) -> dict:
    """
    Print the action to console and wait for user input.
    Raises ConfirmationDenied if user types anything other than 'y' / 'yes'.
    """
    print(f"\n[computer-mcp] HIGH-RISK ACTION: {action_description}")
    answer = input("Confirm? (y/n): ").strip().lower()
    if answer in ("y", "yes"):
        return {"confirmed": True, "action": action_description}
    raise ConfirmationDenied(f"User denied: {action_description}")
```

- [ ] **Step 4: Run tests**

Run: `pytest computer-mcp/tests/test_confirm_guard.py -v`
Expected: PASS — 2 tests passed.

- [ ] **Step 5: Commit**

```bash
git add computer-mcp/confirm_guard.py computer-mcp/tests/test_confirm_guard.py
git commit -m "Add: confirm_guard for high-risk action gating"
```

---

## Task 6: MCP server — tool registration and entry point

**Files:**
- Create: `computer-mcp/server.py`

- [ ] **Step 1: Write smoke test**

Add `computer-mcp/tests/test_server_import.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_server_imports_without_error():
    import importlib
    mod = importlib.import_module("server")
    assert hasattr(mod, "mcp")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest computer-mcp/tests/test_server_import.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'server'`

- [ ] **Step 3: Implement server.py**

Create `computer-mcp/server.py`:

```python
"""
computer-mcp: Desktop control MCP server for power-media.
Run: python computer-mcp/server.py
"""

import sys, os
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
```

- [ ] **Step 4: Run smoke test**

Run: `pytest computer-mcp/tests/test_server_import.py -v`
Expected: PASS — 1 test passed.

- [ ] **Step 5: Commit**

```bash
git add computer-mcp/server.py computer-mcp/tests/test_server_import.py
git commit -m "Add: MCP server with 14 desktop control tools"
```

---

## Task 7: End-to-end smoke test (manual)

This task runs the server and confirms all tools are registered.

- [ ] **Step 1: Start the server in stdio mode and list tools**

Run: `python computer-mcp/server.py`
In another terminal or via MCP client, list available tools.
Expected: 14 tools registered — screenshot, inspect_screen, list_windows, focus_window, get_cursor, click, double_click, drag, type_text, press_key, hotkey, scroll, wait, confirm_action.

- [ ] **Step 2: Test screenshot via MCP**

Call `tool_screenshot` with no arguments.
Expected: Returns JSON with `"success": true` and a valid `.png` path that exists on disk.

- [ ] **Step 3: Test list_windows via MCP**

Call `tool_list_windows`.
Expected: Returns JSON with `"windows": [...]` containing at least one entry with `"title"` and `"handle"`.

- [ ] **Step 4: Test inspect_screen via MCP**

Call `tool_inspect_screen` with no arguments.
Expected: Returns JSON with `"ocr_blocks"` list (may be empty if screen has no text, but key must exist).

- [ ] **Step 5: Commit final state**

```bash
git add .
git commit -m "Add: computer-mcp complete — 14 tools, tests, README"
```

---

## Task 8: Add MCP config entry for power-media

**Files:**
- Modify: `.claude/settings.local.json`

- [ ] **Step 1: Read current settings**

Read `.claude/settings.local.json` to see existing structure.

- [ ] **Step 2: Add computer-mcp to mcpServers**

Add an entry to the `mcpServers` block:

```json
"computer": {
  "command": "python",
  "args": ["computer-mcp/server.py"]
}
```

- [ ] **Step 3: Verify OpenCode picks it up**

Restart OpenCode session. Run `/mcp` to confirm `computer` server is listed.
Expected: `computer` appears with status `connected`.

- [ ] **Step 4: Commit**

```bash
git add .claude/settings.local.json
git commit -m "Add: register computer-mcp in OpenCode settings"
```
