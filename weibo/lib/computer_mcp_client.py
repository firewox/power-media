#!/usr/bin/env python3
"""
Computer MCP Client - 封装 computer-mcp 工具调用
"""
import subprocess
import json
import time
import sys
from typing import Optional, Dict, Any


class ComputerMCPClient:
    """Computer MCP 客户端，用于调用 MCP 工具"""

    # 平台标识，截图文件名将使用此前缀
    PLATFORM = "weibo"

    def __init__(self):
        self.server_path = self._find_mcp_server()
    
    def _find_mcp_server(self) -> str:
        """查找 MCP 服务器脚本路径"""
        import os
        
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 尝试常见路径（相对于项目根目录）
        possible_paths = [
            os.path.join(current_dir, "../../computer-mcp/server.py"),
            os.path.join(current_dir, "../../../computer-mcp/server.py"),
            "computer-mcp/server.py",
            "../computer-mcp/server.py",
            "../../computer-mcp/server.py",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        # 如果找不到，返回默认路径
        return "computer-mcp/server.py"
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用 MCP 工具"""
        try:
            # 构建请求
            request = {
                "tool": tool_name,
                "params": params
            }
            
            # 调用 MCP 服务器
            result = subprocess.run(
                ["python", self.server_path],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"MCP server error: {result.stderr}"
                }
            
            return json.loads(result.stdout)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===== 常用工具封装 =====
    
    def focus_window(self, title: str) -> Dict[str, Any]:
        """聚焦窗口 - 直接使用 pywin32"""
        try:
            import win32gui
            import win32con
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if title.lower() in window_title.lower():
                        windows.append((hwnd, window_title))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if not windows:
                return {"success": False, "error": f"Window '{title}' not found"}
            
            hwnd, window_title = windows[0]
            
            # 恢复窗口（如果最小化）
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 设置前台窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            return {"success": True, "title": window_title}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_browser(self, url: Optional[str] = None) -> Dict[str, Any]:
        """打开默认浏览器"""
        import webbrowser
        import os
        
        try:
            # 使用 Windows 默认浏览器打开
            target_url = url if url else "about:blank"
            webbrowser.open(target_url)
            
            # 等待浏览器打开
            time.sleep(3)
            
            return {"success": True, "message": f"Browser opened with {target_url}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to open browser: {str(e)}"}
    
    def inspect_screen(self) -> Dict[str, Any]:
        """截图，返回截图路径供多模态 AI 分析"""
        try:
            import pyautogui
            import os
            import time

            # 确保截图目录存在
            screenshot_dir = os.path.join(os.path.dirname(__file__), "../../computer-mcp/screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            # 截图
            prefix = getattr(self, "PLATFORM", "unknown")
            filename = os.path.join(screenshot_dir, f"{prefix}_shot_{int(time.time()*1000)}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)

            # 获取屏幕分辨率
            screen_w, screen_h = pyautogui.size()

            return {
                "success": True,
                "screenshot_path": os.path.abspath(filename),
                "screenshot_width": screenshot.width,
                "screenshot_height": screenshot.height,
                "screen_resolution": {"width": screen_w, "height": screen_h},
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click(self, x: int, y: int) -> Dict[str, Any]:
        """点击指定坐标"""
        try:
            import pyautogui
            pyautogui.click(x, y)
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def type_text(self, text: str) -> Dict[str, Any]:
        """输入文本（支持中文，通过剪贴板粘贴）"""
        try:
            import pyperclip
            import pyautogui
            # 复制到剪贴板
            pyperclip.copy(text)
            # 粘贴 (Ctrl+V)
            pyautogui.hotkey('ctrl', 'v')
            return {"success": True, "length": len(text)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """按键"""
        try:
            import pyautogui
            pyautogui.press(key)
            return {"success": True, "key": key}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def hotkey(self, keys: list) -> Dict[str, Any]:
        """组合键"""
        return self.call_tool("computer-mcp/hotkey", {"keys": keys})
    
    def wait(self, seconds: int) -> Dict[str, Any]:
        """等待"""
        time.sleep(seconds)
        return {"success": True}
    
    def confirm_action(self, description: str) -> Dict[str, Any]:
        """确认操作"""
        return self.call_tool("computer-mcp/confirm_action", {
            "action_description": description
        })


class WeiboAutomation:
    """微博自动化操作封装"""

    def __init__(self):
        self.mcp = ComputerMCPClient()
        self.window_found = False
        self.window_rect = None  # (left, top, width, height) 浏览器内容区域

    def get_browser_window_rect(self) -> dict:
        """
        获取浏览器窗口的内容区域（扣除标题栏、边框）
        返回: {"left": x, "top": y, "width": w, "height": h}
        """
        try:
            import win32gui
            import win32con
            import pyautogui
            
            def callback(hwnd, result):
                title = win32gui.GetWindowText(hwnd)
                if win32gui.IsWindowVisible(hwnd) and ('微博' in title or 'weibo' in title.lower()):
                    rect = win32gui.GetWindowRect(hwnd)
                    result.append({'hwnd': hwnd, 'rect': rect})
                return True

            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if not windows:
                print("  [debug] 未找到微博窗口")
                return None

            hwnd = windows[0]['hwnd']
            
            # 获取客户区（内容区域，扣除标题栏和边框）
            client_rect = win32gui.GetClientRect(hwnd)
            pt = win32gui.ClientToScreen(hwnd, (0, 0))
            
            return {
                "left": pt[0],
                "top": pt[1],
                "width": client_rect[2],
                "height": client_rect[3],
                "screen_resolution": pyautogui.size(),
            }
        except Exception as e:
            import traceback
            print(f"  [debug] 获取窗口区域失败: {e}")
            traceback.print_exc()
            return None

    def pct_to_screen_coords(self, pct_x: float, pct_y: float) -> tuple:
        """
        百分比坐标转屏幕绝对坐标
        基于浏览器窗口内容区域计算，适配不同分辨率和窗口大小
        """
        # 如果获取到了窗口区域，在窗口内计算
        if self.window_rect:
            wr = self.window_rect
            x = wr["left"] + int(wr["width"] * pct_x)
            y = wr["top"] + int(wr["height"] * pct_y)
            return (x, y)
        
        # 降级方案：基于全屏计算
        screen_w, screen_h = pyautogui.size()
        return (int(screen_w * pct_x), int(screen_h * pct_y))

    def find_or_open_weibo(self) -> bool:
        """
        查找或打开微博窗口
        返回：是否成功找到/打开窗口
        """
        print("正在查找微博窗口...")
        
        # 尝试聚焦现有窗口
        result = self.mcp.focus_window("微博")
        if result.get("success"):
            print("✓ 找到微博窗口")
            self.window_found = True
            return True
        
        # 尝试其他可能的标题
        for title in ["Weibo", "微博 - ", "weibo.com", "新浪微博"]:
            result = self.mcp.focus_window(title)
            if result.get("success"):
                print(f"✓ 找到微博窗口 (标题: {title})")
                self.window_found = True
                return True
        
        # 未找到，打开浏览器
        print("未找到微博窗口，正在打开默认浏览器...")
        result = self.mcp.open_browser("https://weibo.com")
        
        if not result.get("success"):
            print(f"✗ 打开浏览器失败: {result.get('error')}")
            return False
        
        # 等待页面加载（给足够时间）
        print("等待浏览器和页面加载...")
        self.mcp.wait(5)
        
        # 多次尝试聚焦（页面加载需要时间）
        for attempt in range(5):
            print(f"尝试聚焦微博窗口 (第 {attempt + 1} 次)...")
            
            for title in ["微博", "Weibo", "微博 -", "weibo.com", "新浪微博"]:
                result = self.mcp.focus_window(title)
                if result.get("success"):
                    print(f"✓ 成功聚焦微博窗口 (标题: {title})")
                    self.window_found = True
                    return True
            
            self.mcp.wait(2)
        
        print("✗ 无法聚焦微博窗口")
        self.window_found = False
        return False
    
    def check_login_status(self) -> Dict[str, Any]:
        """
        检查微博登录状态
        返回截图供多模态 AI 分析登录状态
        """
        # 确保窗口存在
        if not self.window_found:
            if not self.find_or_open_weibo():
                return {
                    "loggedIn": None,  # None 表示无法判断，需要 AI 分析截图
                    "userName": None,
                    "screenshot_path": None,
                    "error": "无法打开微博窗口"
                }

        # 截图，由多模态 AI 分析登录状态
        result = self.mcp.inspect_screen()

        if not result.get("success"):
            return {
                "loggedIn": None,
                "userName": None,
                "screenshot_path": None,
                "error": "截图失败"
            }

        return {
            "loggedIn": None,  # 由 AI 分析截图判断
            "userName": None,
            "screenshot_path": result.get("screenshot_path"),
            "width": result.get("width"),
            "height": result.get("height"),
        }

    def post_text_weibo(self, content: str, input_box_pct: tuple, send_btn_pct: tuple) -> Dict[str, Any]:
        """
        发布纯文本微博
        参数:
            content: 微博内容
            input_box_pct: (x_pct, y_pct) 输入框相对窗口内容区域的百分比 (0~1)
            send_btn_pct: (x_pct, y_pct) 发送按钮相对窗口内容区域的百分比 (0~1)
        """
        import pyautogui
        screen_w, screen_h = pyautogui.size()

        # 获取窗口区域并转换为屏幕坐标
        self.window_rect = self.get_browser_window_rect()
        if self.window_rect:
            wr = self.window_rect
            print(f"  浏览器窗口: ({wr['left']}, {wr['top']}) 内容区: {wr['width']}x{wr['height']}")
        else:
            print(f"  警告: 无法获取窗口区域，使用全屏百分比")

        ix, iy = self.pct_to_screen_coords(input_box_pct[0], input_box_pct[1])
        sx, sy = self.pct_to_screen_coords(send_btn_pct[0], send_btn_pct[1])

        print(f"  屏幕分辨率: {screen_w}x{screen_h}")
        print(f"  输入框坐标: ({ix}, {iy}) [窗口百分比: {input_box_pct}]")
        print(f"  发送按钮坐标: ({sx}, {sy}) [窗口百分比: {send_btn_pct}]")

        # 聚焦窗口
        self.mcp.focus_window("微博")

        # 回到页面顶部
        self.mcp.hotkey(["ctrl", "home"])
        self.mcp.wait(2)

        # 点击输入框
        self.mcp.click(ix, iy)
        self.mcp.wait(1)

        # 全选并替换内容
        self.mcp.hotkey(["ctrl", "a"])
        self.mcp.wait(0.5)
        self.mcp.type_text(content)
        self.mcp.wait(1)

        # 点击发送按钮
        self.mcp.click(sx, sy)

        # 等待发布
        self.mcp.wait(3)

        # 截图验证
        result = self.mcp.inspect_screen()

        if result.get("success"):
            return {
                "success": True,
                "message": "已发送，请检查截图确认发布结果",
                "screenshot_path": result.get("screenshot_path"),
            }
        else:
            return {
                "success": True,
                "message": "已发送，请检查发布结果",
            }


if __name__ == "__main__":
    # 测试代码
    weibo = WeiboAutomation()
    print("正在检查登录状态...")
    status = weibo.check_login_status()
    print(f"登录状态: {status}")
