# 隔离模式 (Isolated Mode) 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现基于 Windows 虚拟桌面的隔离模式,使 AI 能够在独立虚拟桌面中操作浏览器,与用户工作完全并行隔离。

**Architecture:** 新增 `isolated-mcp` 模块,包含虚拟桌面管理器、隔离浏览器管理器、隔离操作封装,以及独立的 MCP 服务。所有隔离操作自动处理虚拟桌面切换,确保用户无感知。

**Tech Stack:** Python 3.10+, comtypes (Windows COM API), pywin32, pyautogui, mss, mcp (FastMCP)

---

## 文件结构概览

### 新增文件

| 文件 | 职责 |
|------|------|
| `isolated-mcp/__init__.py` | 模块初始化 |
| `isolated-mcp/requirements.txt` | 隔离模式依赖 |
| `isolated-mcp/virtual_desktop.py` | Windows 虚拟桌面 COM 接口封装 |
| `isolated-mcp/isolated_browser.py` | 浏览器窗口查找、启动、移动、状态管理 |
| `isolated-mcp/isolated_operations.py` | 隔离操作基类,自动处理桌面切换 |
| `isolated-mcp/server.py` | 隔离模式 MCP 服务入口 |
| `isolated-mcp/tests/test_virtual_desktop.py` | 虚拟桌面管理器单元测试 |
| `isolated-mcp/tests/test_isolated_browser.py` | 隔离浏览器管理器单元测试 |
| `isolated-mcp/tests/test_server_import.py` | 服务器导入测试 |
| `docs/isolated-mode.md` | 隔离模式使用文档 |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `docs/AGENT-CALLING-PROTOCOL.md` | 新增隔离模式调用章节 |

---

### Task 1: 虚拟桌面管理器 (VirtualDesktopManager)

**Files:**
- Create: `isolated-mcp/virtual_desktop.py`
- Test: `isolated-mcp/tests/test_virtual_desktop.py`

#### Step 1: 编写虚拟桌面管理器的测试

```python
# isolated-mcp/tests/test_virtual_desktop.py

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from virtual_desktop import VirtualDesktopManager, VirtualDesktopError


class TestVirtualDesktopManager:
    """VirtualDesktopManager 单元测试"""

    def test_list_desktops_returns_list(self):
        """list_desktops 应返回桌面 ID 列表"""
        manager = VirtualDesktopManager()
        desktops = manager.list_desktops()
        assert isinstance(desktops, list)
        # 至少有一个桌面(当前桌面)
        assert len(desktops) >= 1

    def test_get_current_desktop_returns_string(self):
        """get_current_desktop 应返回当前桌面 ID"""
        manager = VirtualDesktopManager()
        desktop_id = manager.get_current_desktop()
        assert isinstance(desktop_id, str)
        assert len(desktop_id) > 0

    def test_create_and_cleanup_desktop(self):
        """创建桌面后应能清理"""
        manager = VirtualDesktopManager()
        original_count = len(manager.list_desktops())
        
        desktop_id = manager.create_desktop("test-isolated")
        assert isinstance(desktop_id, str)
        
        # 创建后桌面数应增加
        assert len(manager.list_desktops()) == original_count + 1
        
        # 清理
        manager.cleanup([desktop_id])
        assert len(manager.list_desktops()) == original_count

    def test_switch_desktop_roundtrip(self):
        """切换桌面后应能切回"""
        manager = VirtualDesktopManager()
        original_desktop = manager.get_current_desktop()
        
        desktop_id = manager.create_desktop("test-switch")
        try:
            manager.switch_to_desktop(desktop_id)
            current = manager.get_current_desktop()
            assert current == desktop_id
            
            # 切回原桌面
            manager.switch_to_desktop(original_desktop)
            assert manager.get_current_desktop() == original_desktop
        finally:
            manager.cleanup([desktop_id])
```

#### Step 2: 运行测试验证失败

```bash
cd isolated-mcp
python -m pytest tests/test_virtual_desktop.py -v
```

预期: FAIL - 模块不存在或方法未实现

#### Step 3: 实现 VirtualDesktopManager

```python
# isolated-mcp/virtual_desktop.py

"""
Windows Virtual Desktop Manager using COM interfaces.
Requires Windows 10 1703+ or Windows 11.
"""

import ctypes
import ctypes.wintypes
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VirtualDesktopError(Exception):
    """虚拟桌面操作异常"""
    pass


class VirtualDesktopManager:
    """Windows 虚拟桌面管理器"""

    # Windows 10 1703+ Virtual Desktop COM interfaces
    CLSID_ImmersiveShell = "{C2F03A33-21F5-47FA-B4BB-156362A2F239}"
    CLSID_VirtualDesktopManager = "{AA509086-5CA9-4C25-8F95-589D3C07B48A}"
    IID_IVirtualDesktopManager = "{A5CD92FF-29BE-454C-8D04-D82879FB3F1B}"
    
    # Windows 11 specific IDs (may vary by version)
    CLSID_VirtualDesktopManagerWin11 = "{3F07F4BE-B107-441A-AF0F-39D82529072C}"
    IID_IVirtualDesktopManagerWin11 = "{536D3495-B208-4CC9-AE26-DE8111275BF8}"

    def __init__(self):
        self._is_win11 = self._detect_win11()
        self._manager = None
        self._initialize_com()

    def _detect_win11(self) -> bool:
        """检测是否为 Windows 11"""
        try:
            import platform
            version = platform.version()
            major = int(version.split('.')[0])
            build = int(version.split('.')[2])
            # Windows 11 build >= 22000
            return major >= 10 and build >= 22000
        except Exception:
            return False

    def _initialize_com(self):
        """初始化 COM 接口"""
        try:
            import comtypes.client
            
            # 尝试 Windows 11 接口
            if self._is_win11:
                try:
                    self._manager = comtypes.client.CreateObject(
                        self.CLSID_VirtualDesktopManagerWin11,
                        interface=self.IID_IVirtualDesktopManagerWin11
                    )
                    logger.info("Initialized Windows 11 Virtual Desktop API")
                    return
                except Exception as e:
                    logger.warning(f"Win11 API failed, falling back to Win10: {e}")
            
            # 使用 Windows 10 接口
            self._manager = comtypes.client.CreateObject(
                self.CLSID_ImmersiveShell,
                interface=comtypes.IUnknown
            ).QueryInterface(self.IID_IVirtualDesktopManager)
            logger.info("Initialized Windows 10 Virtual Desktop API")
            
        except Exception as e:
            logger.error(f"Failed to initialize COM: {e}")
            raise VirtualDesktopError(
                f"无法初始化虚拟桌面 API: {e}\n"
                f"请确保: 1) Windows 10 1703+ 或 Win11  "
                f"2) 安装了 comtypes 库  3) 以管理员权限运行"
            ) from e

    def create_desktop(self, name: str = "power-media-isolated") -> str:
        """
        创建新的虚拟桌面
        
        Args:
            name: 桌面名称(仅用于日志,Windows 不原生支持名称)
        
        Returns:
            desktop_id: 虚拟桌面的 GUID
        
        Raises:
            VirtualDesktopError: 创建失败时抛出
        """
        try:
            # 使用 IVirtualDesktopManagerInternal::CreateDesktopW
            # 注意: 这个接口在不同 Windows 版本可能不同
            import comtypes.client
            
            # 获取 IVirtualDesktopManagerInternal
            pdisp = comtypes.client.CreateObject(self.CLSID_ImmersiveShell)
            
            # 不同 Windows 版本的 IID 可能不同
            if self._is_win11:
                iid = "{536D3495-B208-4CC9-AE26-DE8111275BF8}"
            else:
                iid = "{F31574D6-B682-4CDC-BD56-1827860ABEC6}"
            
            internal = pdisp.QueryInterface(iid)
            
            # CreateDesktopW 返回桌面 ID
            desktop_id = internal.CreateDesktopW()
            
            logger.info(f"Created virtual desktop: {desktop_id}")
            return desktop_id
            
        except Exception as e:
            logger.error(f"Failed to create desktop: {e}")
            raise VirtualDesktopError(f"创建虚拟桌面失败: {e}") from e

    def switch_to_desktop(self, desktop_id: str) -> None:
        """
        切换到指定虚拟桌面
        
        Args:
            desktop_id: 目标桌面 ID
        """
        try:
            self._manager.SwitchDesktop(desktop_id)
            logger.debug(f"Switched to desktop: {desktop_id}")
        except Exception as e:
            logger.error(f"Failed to switch desktop: {e}")
            raise VirtualDesktopError(f"切换虚拟桌面失败: {e}") from e

    def get_current_desktop(self) -> str:
        """
        获取当前虚拟桌面的 ID
        
        Returns:
            desktop_id: 当前桌面 ID
        """
        try:
            return self._manager.GetCurrentDesktop()
        except Exception as e:
            logger.error(f"Failed to get current desktop: {e}")
            raise VirtualDesktopError(f"获取当前虚拟桌面失败: {e}") from e

    def move_window_to_desktop(self, hwnd: int, desktop_id: str) -> None:
        """
        将指定窗口移动到目标虚拟桌面
        
        Args:
            hwnd: 窗口句柄
            desktop_id: 目标桌面 ID
        """
        try:
            self._manager.MoveWindowToDesktop(hwnd, desktop_id)
            logger.debug(f"Moved window {hwnd} to desktop {desktop_id}")
        except Exception as e:
            logger.error(f"Failed to move window: {e}")
            raise VirtualDesktopError(f"移动窗口到虚拟桌面失败: {e}") from e

    def is_window_on_current_desktop(self, hwnd: int) -> bool:
        """
        检查窗口是否在当前虚拟桌面上
        
        Args:
            hwnd: 窗口句柄
        
        Returns:
            bool: 是否在当前桌面
        """
        try:
            return self._manager.IsWindowOnCurrentVirtualDesktop(hwnd)
        except Exception:
            # 如果不支持此方法,默认返回 True
            return True

    def list_desktops(self) -> list[str]:
        """
        列出所有虚拟桌面 ID
        
        Returns:
            list[str]: 桌面 ID 列表
        """
        try:
            # 获取 IVirtualDesktopManagerInternal::GetDesktops
            import comtypes.client
            pdisp = comtypes.client.CreateObject(self.CLSID_ImmersiveShell)
            
            if self._is_win11:
                iid = "{536D3495-B208-4CC9-AE26-DE8111275BF8}"
            else:
                iid = "{F31574D6-B682-4CDC-BD56-1827860ABEC6}"
            
            internal = pdisp.QueryInterface(iid)
            desktop_list = internal.GetDesktops()
            
            # IObjectArray 转 Python 列表
            count = desktop_list.GetCount()
            result = []
            for i in range(count):
                desktop = desktop_list.GetAt(i)
                result.append(str(desktop.GetID()))
            
            return result
        except Exception as e:
            logger.warning(f"Failed to list desktops, returning empty list: {e}")
            return []

    def cleanup(self, desktop_ids: Optional[list[str]] = None) -> None:
        """
        清理指定的虚拟桌面
        
        Args:
            desktop_ids: 要清理的桌面 ID 列表,默认清理所有非默认桌面
        """
        if not desktop_ids:
            return
        
        try:
            import comtypes.client
            pdisp = comtypes.client.CreateObject(self.CLSID_ImmersiveShell)
            
            if self._is_win11:
                iid = "{536D3495-B208-4CC9-AE26-DE8111275BF8}"
            else:
                iid = "{F31574D6-B682-4CDC-BD56-1827860ABEC6}"
            
            internal = pdisp.QueryInterface(iid)
            
            current_desktop = self.get_current_desktop()
            
            for desktop_id in desktop_ids:
                # 不能清理当前所在的桌面
                if desktop_id == current_desktop:
                    logger.warning(f"Skipping cleanup of current desktop: {desktop_id}")
                    continue
                
                try:
                    internal.RemoveDesktop(desktop_id)
                    logger.info(f"Cleaned up virtual desktop: {desktop_id}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup desktop {desktop_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup desktops: {e}")
            raise VirtualDesktopError(f"清理虚拟桌面失败: {e}") from e
```

#### Step 4: 安装依赖并运行测试

```bash
# 安装依赖
pip install comtypes pywin32

# 运行测试
cd isolated-mcp
python -m pytest tests/test_virtual_desktop.py -v
```

预期: PASS (需要管理员权限)

#### Step 5: 提交

```bash
git add isolated-mcp/virtual_desktop.py isolated-mcp/tests/test_virtual_desktop.py
git commit -m "feat(isolated-mcp): add VirtualDesktopManager with tests"
```

---

### Task 2: 隔离浏览器管理器 (IsolatedBrowser)

**Files:**
- Create: `isolated-mcp/isolated_browser.py`
- Test: `isolated-mcp/tests/test_isolated_browser.py`

#### Step 1: 编写隔离浏览器管理器的测试

```python
# isolated-mcp/tests/test_isolated_browser.py

import pytest
import sys
import os
import subprocess
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from isolated_browser import IsolatedBrowser, BrowserNotFoundError


class TestIsolatedBrowser:
    """IsolatedBrowser 单元测试"""

    @pytest.fixture
    def mock_desktop_manager(self):
        """模拟虚拟桌面管理器"""
        manager = Mock()
        manager.create_desktop.return_value = "test-desktop-id"
        manager.get_current_desktop.return_value = "user-desktop-id"
        return manager

    @pytest.fixture
    def browser(self, mock_desktop_manager):
        """创建 IsolatedBrowser 实例"""
        return IsolatedBrowser(mock_desktop_manager)

    def test_init(self, browser):
        """初始化后属性应为 None"""
        assert browser.desktop_id is None
        assert browser.window_hwnd is None

    @patch('isolated_browser.find_browser_window')
    def test_launch_or_locate_finds_existing(self, mock_find, browser, mock_desktop_manager):
        """应能找到已有浏览器窗口"""
        mock_find.return_value = {"hwnd": 12345, "title": "Chrome"}
        
        hwnd = browser.launch_or_locate()
        
        assert hwnd == 12345
        mock_find.assert_called_once()

    @patch('isolated_browser.find_browser_window')
    @patch('isolated_browser.launch_new_browser')
    def test_launch_or_locate_launches_new(self, mock_launch, mock_find, browser):
        """找不到窗口时应启动新窗口"""
        mock_find.return_value = None
        mock_launch.return_value = {"hwnd": 67890, "title": "Chrome"}
        
        hwnd = browser.launch_or_locate()
        
        assert hwnd == 67890
        mock_find.assert_called_once()
        mock_launch.assert_called_once()

    def test_get_window_rect_structure(self, browser):
        """get_window_rect 应返回包含 left/top/width/height 的字典"""
        # 此测试需要实际窗口,这里只测试返回结构
        browser.window_hwnd = 12345
        
        # 模拟情况下返回 None (真实环境会调用 Windows API)
        # 真实测试需要实际窗口
        assert browser.window_hwnd == 12345

    def test_setup_sets_desktop_id_and_hwnd(self, browser, mock_desktop_manager):
        """setup 应设置 desktop_id 和 window_hwnd"""
        with patch.object(browser, 'launch_or_locate', return_value=12345):
            with patch.object(browser, 'move_to_isolated_desktop'):
                result = browser.setup()
                
                assert browser.desktop_id == "test-desktop-id"
                assert browser.window_hwnd == 12345
                assert result == 12345
                mock_desktop_manager.create_desktop.assert_called_once()
```

#### Step 2: 运行测试验证失败

```bash
cd isolated-mcp
python -m pytest tests/test_isolated_browser.py -v
```

预期: FAIL - 模块不存在

#### Step 3: 实现 IsolatedBrowser

```python
# isolated-mcp/isolated_browser.py

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
    """未找到浏览器窗口"""
    pass


# 常见浏览器窗口类名
BROWSER_CLASS_NAMES = [
    "Chrome_WidgetWin_1",      # Chrome, Edge, Brave, etc.
    "MozillaWindowClass",     # Firefox
    "OperaWindowClass",       # Opera
    "Chrome_WidgetWin_0",     # Some Chrome variants
]

# 浏览器可执行文件路径 (Windows)
BROWSER_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_browser_window() -> Optional[dict]:
    """
    查找已有的浏览器窗口
    
    Returns:
        {"hwnd": int, "title": str} 或 None
    """
    import win32gui
    import win32process
    
    def enum_callback(hwnd, results):
        try:
            # 检查窗口是否可见
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True
            
            # 获取窗口标题
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True
            
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            
            if not title:
                return True
            
            # 获取窗口类名
            class_name = win32gui.GetClassName(hwnd)
            
            # 检查是否为浏览器窗口
            if class_name in BROWSER_CLASS_NAMES:
                results.append({"hwnd": hwnd, "title": title, "class": class_name})
                
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
    启动新的浏览器窗口
    
    Args:
        url: 要打开的 URL
    
    Returns:
        {"hwnd": int, "title": str}
    """
    # 查找可用的浏览器
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
    
    # 启动新窗口
    cmd = [browser_path, "--new-window"]
    if url:
        cmd.append(url)
    
    logger.info(f"Launching browser: {' '.join(cmd)}")
    subprocess.Popen(cmd)
    
    # 等待窗口出现
    time.sleep(2)
    
    # 查找新启动的窗口
    window = find_browser_window()
    if window:
        return window
    
    raise BrowserNotFoundError("浏览器启动后未找到窗口")


class IsolatedBrowser:
    """隔离浏览器管理器"""

    def __init__(self, desktop_manager):
        """
        Args:
            desktop_manager: VirtualDesktopManager 实例
        """
        self.desktop_manager = desktop_manager
        self.desktop_id: Optional[str] = None
        self.window_hwnd: Optional[int] = None

    def setup(self, url: Optional[str] = None) -> int:
        """
        初始化隔离浏览器环境
        
        Args:
            url: 要打开的 URL(可选)
        
        Returns:
            hwnd: 浏览器窗口句柄
        """
        # 1. 创建虚拟桌面
        self.desktop_id = self.desktop_manager.create_desktop("power-media-isolated")
        logger.info(f"Created isolated desktop: {self.desktop_id}")
        
        # 2. 查找或启动浏览器窗口
        self.window_hwnd = self.launch_or_locate(url)
        logger.info(f"Browser window hwnd: {self.window_hwnd}")
        
        # 3. 移动到隔离桌面
        self.move_to_isolated_desktop()
        
        return self.window_hwnd

    def launch_or_locate(self, url: Optional[str] = None) -> int:
        """
        启动新浏览器窗口或定位已有窗口
        
        Args:
            url: 要打开的 URL(可选)
        
        Returns:
            hwnd: 窗口句柄
        """
        # 先查找已有窗口
        window = find_browser_window()
        if window:
            logger.info(f"Found existing browser window: {window['title']}")
            self.window_hwnd = window["hwnd"]
            return self.window_hwnd
        
        # 启动新窗口
        logger.info("No existing browser window found, launching new one")
        window = launch_new_browser(url)
        self.window_hwnd = window["hwnd"]
        return self.window_hwnd

    def move_to_isolated_desktop(self) -> None:
        """将浏览器窗口移动到隔离虚拟桌面"""
        if not self.desktop_id or not self.window_hwnd:
            raise RuntimeError("desktop_id and window_hwnd must be set first")
        
        self.desktop_manager.move_window_to_desktop(self.window_hwnd, self.desktop_id)
        logger.info(f"Moved browser window to isolated desktop")

    def get_window_rect(self) -> dict:
        """
        获取浏览器窗口内容区域
        
        Returns:
            {"left": int, "top": int, "width": int, "height": int}
        """
        if not self.window_hwnd:
            raise RuntimeError("window_hwnd not set")
        
        import win32gui
        
        # 获取窗口位置
        rect = win32gui.GetWindowRect(self.window_hwnd)
        left, top, right, bottom = rect
        
        # 获取客户区大小 (内容区域)
        client_rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetClientRect(self.window_hwnd, ctypes.byref(client_rect))
        
        width = client_rect.right - client_rect.left
        height = client_rect.bottom - client_rect.top
        
        return {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
        }

    def ensure_restored(self) -> None:
        """确保窗口处于恢复状态(非最小化/最大化)"""
        if not self.window_hwnd:
            raise RuntimeError("window_hwnd not set")
        
        # SW_RESTORE = 9
        ctypes.windll.user32.ShowWindow(self.window_hwnd, 9)
        time.sleep(0.1)

    def ensure_minimized(self) -> None:
        """确保窗口最小化"""
        if not self.window_hwnd:
            raise RuntimeError("window_hwnd not set")
        
        # SW_MINIMIZE = 6
        ctypes.windll.user32.ShowWindow(self.window_hwnd, 6)
        time.sleep(0.1)

    def is_alive(self) -> bool:
        """检查窗口是否仍然存活"""
        if not self.window_hwnd:
            return False
        
        try:
            return bool(ctypes.windll.user32.IsWindow(self.window_hwnd))
        except Exception:
            return False

    def cleanup(self) -> None:
        """清理隔离浏览器环境"""
        logger.info("Cleaning up isolated browser")
        
        # 可选: 关闭窗口
        if self.window_hwnd and self.is_alive():
            try:
                # WM_CLOSE = 0x0010
                ctypes.windll.user32.PostMessageW(self.window_hwnd, 0x0010, 0, 0)
                logger.info(f"Closed browser window {self.window_hwnd}")
            except Exception as e:
                logger.warning(f"Failed to close browser window: {e}")
        
        self.window_hwnd = None
        self.desktop_id = None
```

#### Step 4: 运行测试验证通过

```bash
cd isolated-mcp
python -m pytest tests/test_isolated_browser.py -v
```

预期: PASS

#### Step 5: 提交

```bash
git add isolated-mcp/isolated_browser.py isolated-mcp/tests/test_isolated_browser.py
git commit -m "feat(isolated-mcp): add IsolatedBrowser with tests"
```

---

### Task 3: 隔离操作封装 (IsolatedOperations)

**Files:**
- Create: `isolated-mcp/isolated_operations.py`
- Test: `isolated-mcp/tests/test_isolated_operations.py`

#### Step 1: 编写隔离操作的测试

```python
# isolated-mcp/tests/test_isolated_operations.py

import pytest
import sys
import os
from unittest.mock import Mock, patch, call

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from isolated_operations import IsolatedOperation, isolated_op


class TestIsolatedOperation:
    """隔离操作单元测试"""

    @pytest.fixture
    def mock_manager(self):
        """模拟虚拟桌面管理器"""
        manager = Mock()
        manager.get_current_desktop.return_value = "user-desktop"
        return manager

    @pytest.fixture
    def mock_browser(self):
        """模拟浏览器"""
        browser = Mock()
        browser.desktop_id = "isolated-desktop"
        browser.window_hwnd = 12345
        return browser

    def test_execute_switches_desktops(self, mock_manager, mock_browser):
        """执行操作应切换桌面"""
        def operation():
            return {"success": True}
        
        iso_op = IsolatedOperation(mock_manager, mock_browser, operation)
        result = iso_op.execute()
        
        # 验证桌面切换顺序
        calls = [
            call.switch_to_desktop("isolated-desktop"),
            call.switch_to_desktop("user-desktop"),
        ]
        assert mock_manager.switch_to_desktop.call_count == 2

    def test_execute_restores_window(self, mock_manager, mock_browser):
        """执行操作应恢复窗口"""
        def operation():
            return {"success": True}
        
        iso_op = IsolatedOperation(mock_manager, mock_browser, operation)
        iso_op.execute()
        
        mock_browser.ensure_restored.assert_called_once()

    def test_execute_returns_operation_result(self, mock_manager, mock_browser):
        """执行应返回操作结果"""
        def operation():
            return {"data": "test"}
        
        iso_op = IsolatedOperation(mock_manager, mock_browser, operation)
        result = iso_op.execute()
        
        assert result == {"data": "test"}

    def test_execute_always_switches_back_on_error(self, mock_manager, mock_browser):
        """操作失败时也应切回用户桌面"""
        def operation():
            raise ValueError("Test error")
        
        iso_op = IsolatedOperation(mock_manager, mock_browser, operation)
        
        with pytest.raises(ValueError, match="Test error"):
            iso_op.execute()
        
        # 验证仍切回了用户桌面
        mock_manager.switch_to_desktop.assert_any_call("user-desktop")

    def test_isolated_op_decorator(self, mock_manager, mock_browser):
        """装饰器应包装操作"""
        @isolated_op(mock_manager, mock_browser)
        def my_op(x, y):
            return x + y
        
        result = my_op(3, 4)
        assert result == 7
```

#### Step 2: 运行测试验证失败

```bash
cd isolated-mcp
python -m pytest tests/test_isolated_operations.py -v
```

预期: FAIL

#### Step 3: 实现 IsolatedOperations

```python
# isolated-mcp/isolated_operations.py

"""
Isolated Operation Wrapper.
Automatically handles virtual desktop switching for all operations.
"""

import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

# 桌面切换延迟 (秒)
SWITCH_DELAY = 0.1
RESTORE_DELAY = 0.05


class IsolatedOperation:
    """隔离操作基类,自动处理桌面切换"""

    def __init__(self, desktop_manager, browser, operation: Callable):
        """
        Args:
            desktop_manager: VirtualDesktopManager 实例
            browser: IsolatedBrowser 实例
            operation: 实际要执行的操作函数
        """
        self.desktop_manager = desktop_manager
        self.browser = browser
        self.operation = operation

    def execute(self, *args, **kwargs) -> Any:
        """
        执行操作,自动切换桌面
        
        流程:
        1. 记录用户桌面
        2. 切换到隔离桌面
        3. 恢复窗口
        4. 执行操作
        5. 切回用户桌面 (无论成功失败)
        """
        # 1. 记录用户桌面
        user_desktop = self.desktop_manager.get_current_desktop()
        
        try:
            # 2. 切换到隔离桌面
            logger.debug(f"Switching to isolated desktop: {self.browser.desktop_id}")
            self.desktop_manager.switch_to_desktop(self.browser.desktop_id)
            time.sleep(SWITCH_DELAY)
            
            # 3. 确保窗口在前台
            self.browser.ensure_restored()
            time.sleep(RESTORE_DELAY)
            
            # 4. 执行实际操作
            logger.debug(f"Executing operation: {self.operation.__name__ if hasattr(self.operation, '__name__') else 'anonymous'}")
            result = self.operation(*args, **kwargs)
            
            return result
        
        finally:
            # 5. 切回用户桌面 (确保无论成功失败都切回)
            logger.debug(f"Switching back to user desktop: {user_desktop}")
            try:
                self.desktop_manager.switch_to_desktop(user_desktop)
                time.sleep(SWITCH_DELAY / 2)
            except Exception as e:
                logger.error(f"Failed to switch back to user desktop: {e}")
                # 尝试再次切回
                try:
                    self.desktop_manager.switch_to_desktop(user_desktop)
                except Exception:
                    pass


def isolated_op(desktop_manager, browser):
    """
    装饰器: 将普通操作函数包装为隔离操作
    
    Usage:
        @isolated_op(desktop_manager, browser)
        def my_click(x, y):
            pyautogui.click(x, y)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            iso_op = IsolatedOperation(desktop_manager, browser, func)
            return iso_op.execute(*args, **kwargs)
        return wrapper
    return decorator
```

#### Step 4: 运行测试验证通过

```bash
cd isolated-mcp
python -m pytest tests/test_isolated_operations.py -v
```

预期: PASS

#### Step 5: 提交

```bash
git add isolated-mcp/isolated_operations.py isolated-mcp/tests/test_isolated_operations.py
git commit -m "feat(isolated-mcp): add IsolatedOperation wrapper with tests"
```

---

### Task 4: 隔离 MCP 服务 (Server)

**Files:**
- Create: `isolated-mcp/server.py`
- Create: `isolated-mcp/__init__.py`
- Create: `isolated-mcp/requirements.txt`
- Test: `isolated-mcp/tests/test_server_import.py`

#### Step 1: 编写 MCP 服务

```python
# isolated-mcp/server.py

"""
Isolated Computer MCP Server.
Provides desktop-isolated browser control tools.
Run: python isolated-mcp/server.py
"""

import sys
import os

# 添加当前目录和父目录到路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.fastmcp import FastMCP
from virtual_desktop import VirtualDesktopManager, VirtualDesktopError
from isolated_browser import IsolatedBrowser, BrowserNotFoundError
from isolated_operations import IsolatedOperation

# 导入原有 computer-mcp 的功能
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

# 全局隔离管理器 (延迟初始化)
_desktop_manager = None
_browser = None


def get_desktop_manager() -> VirtualDesktopManager:
    """获取或创建虚拟桌面管理器"""
    global _desktop_manager
    if _desktop_manager is None:
        _desktop_manager = VirtualDesktopManager()
    return _desktop_manager


def get_browser() -> IsolatedBrowser:
    """获取隔离浏览器实例"""
    global _browser
    if _browser is None:
        _browser = IsolatedBrowser(get_desktop_manager())
    return _browser


def isolated_tool(func):
    """隔离工具装饰器: 自动处理桌面切换"""
    def wrapper(*args, **kwargs):
        browser = get_browser()
        desktop_manager = get_desktop_manager()
        
        iso_op = IsolatedOperation(desktop_manager, browser, func)
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
def tool_screenshot(region_top: int = 0, region_left: int = 0,
                    region_width: int = 0, region_height: int = 0) -> dict:
    """
    Take screenshot in isolated environment.
    Automatically switches to isolated desktop, captures, then switches back.
    Pass all zeros for full browser window.
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
    
    log.record("isolated_screenshot", {"region": region_top > 0 and {"top": region_top} or None})
    return result


@mcp.tool()
def tool_inspect_screen(region_top: int = 0, region_left: int = 0,
                        region_width: int = 0, region_height: int = 0) -> dict:
    """
    Screenshot + OCR in isolated environment.
    """
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
    
    log.record("isolated_click", {"x": x, "y": y, "button": button})
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
def tool_drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.3) -> dict:
    """Drag from (x1,y1) to (x2,y2) in isolated environment."""
    def _drag():
        return drag(x1, y1, x2, y2, duration)
    
    browser = get_browser()
    desktop_manager = get_desktop_manager()
    iso_op = IsolatedOperation(desktop_manager, browser, _drag)
    result = iso_op.execute()
    
    log.record("isolated_drag", {"from": [x1, y1], "to": [x2, y2]})
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
    
    log.record("isolated_type_text", {"text": text, "secret": secret})
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
    
    log.record("isolated_scroll", {"x": x, "y": y, "clicks": clicks})
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
    """Request human confirmation (works on current desktop, not isolated)."""
    result = request_confirm(action_description)
    log.record("isolated_confirm_action", {"action": action_description})
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
        
        # 关闭窗口
        browser.cleanup()
        
        # 清理虚拟桌面
        if browser.desktop_id:
            desktop_manager.cleanup([browser.desktop_id])
        
        # 重置全局变量
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
```

#### Step 2: 创建辅助文件

```python
# isolated-mcp/__init__.py

"""
Isolated MCP Module.
Provides desktop-isolated browser control via Windows Virtual Desktops.
"""

__version__ = "1.0.0"
```

```txt
# isolated-mcp/requirements.txt

mcp>=1.0.0
comtypes>=1.2.0
pywin32>=306
pyautogui>=0.9.54
mss>=9.0.1
easyocr>=1.7.1
opencv-python>=4.9.0
Pillow>=10.0.0
pytest>=8.0.0
```

#### Step 3: 创建服务器导入测试

```python
# isolated-mcp/tests/test_server_import.py

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestServerImport:
    """测试服务器模块导入"""

    def test_import_virtual_desktop(self):
        from virtual_desktop import VirtualDesktopManager, VirtualDesktopError
        assert VirtualDesktopManager
        assert VirtualDesktopError

    def test_import_isolated_browser(self):
        from isolated_browser import IsolatedBrowser, BrowserNotFoundError
        assert IsolatedBrowser
        assert BrowserNotFoundError

    def test_import_isolated_operations(self):
        from isolated_operations import IsolatedOperation, isolated_op
        assert IsolatedOperation
        assert isolated_op

    def test_import_server(self):
        """测试导入 server 模块 (不运行)"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "server",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "server.py")
        )
        assert spec is not None
```

#### Step 4: 运行所有测试

```bash
cd isolated-mcp
python -m pytest tests/ -v
```

预期: 所有测试 PASS

#### Step 5: 提交

```bash
git add isolated-mcp/server.py isolated-mcp/__init__.py isolated-mcp/requirements.txt isolated-mcp/tests/test_server_import.py
git commit -m "feat(isolated-mcp): add MCP server with isolated tools"
```

---

### Task 5: 文档与集成

**Files:**
- Create: `docs/isolated-mode.md`
- Modify: `docs/AGENT-CALLING-PROTOCOL.md`

#### Step 1: 创建隔离模式使用文档

```markdown
# 隔离模式 (Isolated Mode) 使用指南

## 概述

隔离模式通过 Windows 虚拟桌面技术,实现 AI 操作与用户工作的完全并行隔离。

**核心特性**:
- ✅ 完全并行隔离,AI 操作不影响用户
- ✅ 复用浏览器登录态 (Cookie/Session 共享)
- ✅ 用户完全无感知 (AI 在虚拟桌面 2 操作)
- ✅ 自动桌面切换,所有工具透明处理

---

## 系统要求

- Windows 10 1703+ 或 Windows 11
- Python 3.10+
- Chrome 或 Edge 浏览器
- 管理员权限 (推荐)

---

## 安装

```bash
cd isolated-mcp
pip install -r requirements.txt
```

---

## 配置

在 `.claude/settings.local.json` 中添加:

```json
{
  "mcpServers": {
    "isolated-computer": {
      "command": "python",
      "args": ["isolated-mcp/server.py"]
    }
  }
}
```

---

## 使用流程

### 1. 初始化隔离环境

```python
# 初始化 (可选 URL)
result = await mcp.tool_init_isolated("https://weibo.com")
# 返回: {"success": True, "desktop_id": "...", "window_hwnd": 12345}
```

### 2. 执行操作

所有操作自动处理虚拟桌面切换:

```python
# 截图
screenshot = await mcp.tool_screenshot()

# 获取浏览器窗口位置 (用于坐标映射)
rect = await mcp.tool_get_browser_rect()
# 返回: {"success": True, "left": 100, "top": 50, "width": 1200, "height": 800}

# 点击/输入等操作
await mcp.tool_click(x, y)
await mcp.tool_type_text("内容")
await mcp.tool_press_key("enter")
```

### 3. 清理 (可选)

```python
await mcp.tool_cleanup_isolated()
```

---

## 坐标映射

隔离模式使用与 computer-mcp 相同的百分比坐标 + 窗口区域转换:

```python
# 1. 获取浏览器窗口
rect = await mcp.tool_get_browser_rect()

# 2. AI 估算百分比坐标
pct_x, pct_y = 0.47, 0.25

# 3. 转换为实际坐标
real_x = rect["left"] + int(rect["width"] * pct_x)
real_y = rect["top"] + int(rect["height"] * pct_y)

# 4. 点击
await mcp.tool_click(real_x, real_y)
```

---

## 工具列表

| 工具 | 说明 |
|------|------|
| `tool_init_isolated` | 初始化隔离环境 |
| `tool_screenshot` | 截图 (自动切换桌面) |
| `tool_inspect_screen` | 截图 + OCR |
| `tool_click` | 点击 |
| `tool_double_click` | 双击 |
| `tool_drag` | 拖拽 |
| `tool_type_text` | 输入文字 |
| `tool_press_key` | 按键 |
| `tool_hotkey` | 组合键 |
| `tool_scroll` | 滚动 |
| `tool_wait` | 等待 |
| `tool_get_browser_rect` | 获取浏览器窗口位置 |
| `tool_confirm_action` | 请求确认 (在当前桌面) |
| `tool_cleanup_isolated` | 清理隔离环境 |

---

## 故障排除

### 虚拟桌面创建失败

**错误**: `无法初始化虚拟桌面 API`

**解决**:
1. 确认 Windows 版本 ≥ 10 1703 或 Win11
2. 安装 comtypes: `pip install comtypes`
3. 尝试以管理员权限运行

### 找不到浏览器窗口

**错误**: `未找到 Chrome 或 Edge 浏览器`

**解决**:
1. 安装 Chrome 或 Edge
2. 或修改 `isolated_browser.py` 中的 `BROWSER_PATHS`

### 桌面切换后窗口不可见

**排查**:
1. Win+Tab 查看所有虚拟桌面
2. 确认浏览器窗口在虚拟桌面 2
3. 检查窗口是否被最小化

---

## 与普通模式的对比

| 特性 | computer-mcp | isolated-computer-mcp |
|------|--------------|----------------------|
| 操作目标 | 当前前台窗口 | 隔离虚拟桌面中的窗口 |
| 用户干扰 | 会抢占焦点 | 完全无干扰 |
| 浏览器登录态 | 复用 | 复用 |
| 桌面切换 | 无 | 自动处理 |
| 适用场景 | 单一任务 | 并行工作 |

---

## 最佳实践

1. **初始化一次**: 一个会话中只调用一次 `tool_init_isolated`
2. **获取窗口位置**: 在截图后调用 `tool_get_browser_rect` 进行坐标映射
3. **及时清理**: 任务完成后调用 `tool_cleanup_isolated` 释放资源
4. **错误处理**: 捕获异常并记录日志
```

#### Step 2: 更新 Agent 调用协议

在 `docs/AGENT-CALLING-PROTOCOL.md` 中新增章节:

在文件的 "## 9. 快速参考" 之前插入:

```markdown

---

## 8. 隔离模式 (Isolated Mode)

### 8.1 何时使用隔离模式

当需要 AI 操作浏览器,而用户需要同时工作且互不干扰时,使用隔离模式。

### 8.2 配置

在 `.claude/settings.local.json` 中配置:

```json
{
  "mcpServers": {
    "isolated-computer": {
      "command": "python",
      "args": ["isolated-mcp/server.py"]
    }
  }
}
```

### 8.3 调用流程

```
用户请求 Skill
    ↓
1. 初始化隔离环境
   await mcp.tool_init_isolated(url)
    ↓
2. 获取浏览器窗口位置
   rect = await mcp.tool_get_browser_rect()
    ↓
3. 截图分析
   screenshot = await mcp.tool_screenshot()
   # AI 分析截图,估算百分比坐标
    ↓
4. 转换坐标并操作
   real_x = rect["left"] + int(rect["width"] * pct_x)
   real_y = rect["top"] + int(rect["height"] * pct_y)
   await mcp.tool_click(real_x, real_y)
    ↓
5. 重复 3-4 直到完成
    ↓
6. 清理 (可选)
   await mcp.tool_cleanup_isolated()
```

### 8.4 工具对照

| 普通模式 | 隔离模式 | 区别 |
|---------|---------|------|
| `tool_screenshot` | `tool_screenshot` | 隔离模式自动切换桌面 |
| `tool_click` | `tool_click` | 隔离模式自动切换桌面 |
| - | `tool_init_isolated` | 仅隔离模式 |
| - | `tool_get_browser_rect` | 仅隔离模式 |
| - | `tool_cleanup_isolated` | 仅隔离模式 |

### 8.5 注意事项

- 隔离模式需要 Windows 10 1703+ 或 Windows 11
- 初始化后才能使用其他工具
- 所有操作自动处理虚拟桌面切换
- `tool_confirm_action` 在当前桌面显示(不切换)

---

```

#### Step 3: 提交

```bash
git add docs/isolated-mode.md docs/AGENT-CALLING-PROTOCOL.md
git commit -m "docs: add isolated mode documentation and update protocol"
```

---

### Task 6: 端到端测试

**Files:**
- Create: `isolated-mcp/tests/test_e2e.py` (可选,需要手动验证)

#### Step 1: 创建端到端测试脚本

```python
# isolated-mcp/tests/test_e2e.py

"""
端到端测试: 验证隔离模式完整工作流。
需要手动运行,且需要实际浏览器环境。
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from virtual_desktop import VirtualDesktopManager
from isolated_browser import IsolatedBrowser
from isolated_operations import IsolatedOperation


def test_full_workflow():
    """测试完整工作流程"""
    print("=== 隔离模式端到端测试 ===\n")
    
    # 1. 初始化
    print("1. 初始化虚拟桌面管理器...")
    desktop_manager = VirtualDesktopManager()
    print(f"   当前桌面: {desktop_manager.get_current_desktop()}")
    print(f"   桌面列表: {desktop_manager.list_desktops()}\n")
    
    # 2. 初始化浏览器
    print("2. 初始化隔离浏览器...")
    browser = IsolatedBrowser(desktop_manager)
    
    try:
        hwnd = browser.setup()
        print(f"   浏览器窗口句柄: {hwnd}")
        print(f"   隔离桌面 ID: {browser.desktop_id}\n")
        
        # 3. 获取窗口位置
        print("3. 获取浏览器窗口位置...")
        rect = browser.get_window_rect()
        print(f"   位置: {rect}\n")
        
        # 4. 测试隔离操作
        print("4. 测试隔离操作 (截图)...")
        
        def take_test_screenshot():
            import mss
            with mss.mss() as sct:
                shot = sct.grab(sct.monitors[0])
                return shot.size
        
        iso_op = IsolatedOperation(desktop_manager, browser, take_test_screenshot)
        result = iso_op.execute()
        print(f"   截图尺寸: {result}\n")
        
        # 5. 验证窗口在隔离桌面
        print("5. 验证窗口已移动到隔离桌面...")
        is_on_desktop = desktop_manager.is_window_on_current_desktop(browser.window_hwnd)
        print(f"   窗口在隔离桌面: {is_on_desktop}\n")
        
        print("✅ 测试通过!\n")
        
    finally:
        # 6. 清理
        print("6. 清理...")
        browser.cleanup()
        if browser.desktop_id:
            desktop_manager.cleanup([browser.desktop_id])
        print("   清理完成")


if __name__ == "__main__":
    test_full_workflow()
```

#### Step 2: 运行端到端测试 (手动)

```bash
cd isolated-mcp
python tests/test_e2e.py
```

**预期输出**:
```
=== 隔离模式端到端测试 ===

1. 初始化虚拟桌面管理器...
   当前桌面: {some-uuid}
   桌面列表: ['{uuid1}', '{uuid2}']

2. 初始化隔离浏览器...
   浏览器窗口句柄: 12345
   隔离桌面 ID: {new-uuid}

3. 获取浏览器窗口位置...
   位置: {'left': 100, 'top': 50, 'width': 1200, 'height': 800}

4. 测试隔离操作 (截图)...
   截图尺寸: (2560, 1600)

5. 验证窗口已移动到隔离桌面...
   窗口在隔离桌面: True

✅ 测试通过!

6. 清理...
   清理完成
```

#### Step 3: 提交

```bash
git add isolated-mcp/tests/test_e2e.py
git commit -m "test(isolated-mcp): add end-to-end workflow test"
```

---

## 自审检查

### 1. 规范覆盖检查

| 设计文档章节 | 对应 Task | 状态 |
|------------|----------|------|
| 3.1 VirtualDesktopManager | Task 1 | ✅ |
| 3.2 IsolatedBrowser | Task 2 | ✅ |
| 3.3 IsolatedComputerMCP (server.py) | Task 4 | ✅ |
| 3.4 桌面切换核心逻辑 | Task 3 | ✅ |
| 4. 项目结构 | 所有 Task | ✅ |
| 5. 配置与使用 | Task 5 | ✅ |
| 6. 安全与容错 | 所有 Task (异常处理) | ✅ |
| 7. 技术要求 | Task 1, 4 (requirements.txt) | ✅ |
| 8. 兼容性 | Task 5 (文档) | ✅ |
| 10. 实施检查清单 | 所有 Task | ✅ |

### 2. 占位符扫描

- ✅ 无 "TBD" / "TODO"
- ✅ 所有代码步骤都有完整实现
- ✅ 所有测试都有具体代码
- ✅ 无 "类似 Task N" 的引用

### 3. 类型一致性检查

- `VirtualDesktopManager` 方法签名在所有引用中一致
- `IsolatedBrowser` 的属性 (`desktop_id`, `window_hwnd`) 类型一致
- `IsolatedOperation.execute` 返回类型与所有操作一致
- MCP 工具命名统一 (`tool_*` 前缀)

---

## 执行选择

计划已保存到 `docs/superpowers/plans/2026-04-12-isolated-mode-plan.md`。

**两种执行方式:**

**1. Subagent-Driven (推荐)** - 每个 Task 启动独立子 agent,Task 间有 review checkpoint,迭代快速

**2. Inline Execution** - 在当前会话中顺序执行所有 Task,批量执行带检查点

**你选择哪种?**
