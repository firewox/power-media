#!/usr/bin/env python3
"""
Computer MCP Client - 封装 computer-mcp 工具调用
"""
import subprocess
import json
import time
import sys
from typing import Optional, Dict, Any, List


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

    def list_windows(self) -> List[Dict[str, Any]]:
        """列出当前可见顶层窗口，使用 ctypes 避免 pywin32 EnumWindows 兼容性问题。"""
        try:
            import ctypes
            import ctypes.wintypes

            user32 = ctypes.windll.user32
            windows: list[Dict[str, Any]] = []

            def enum_handler(hwnd, _):
                try:
                    if not user32.IsWindowVisible(hwnd):
                        return True

                    length = user32.GetWindowTextLengthW(hwnd)
                    if length <= 0:
                        return True

                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value.strip()
                    if not title:
                        return True

                    pid = ctypes.wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    windows.append({
                        "hwnd": int(hwnd),
                        "title": title,
                        "pid": int(pid.value),
                    })
                except Exception:
                    pass
                return True

            enum_proc = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                ctypes.wintypes.HWND,
                ctypes.wintypes.LPARAM,
            )(enum_handler)
            user32.EnumWindows(enum_proc, 0)
            return windows
        except Exception:
            return []

    def focus_window(self, title: str) -> Dict[str, Any]:
        """聚焦窗口 - 先列出可见窗口，再使用 ctypes 前置。"""
        try:
            import ctypes

            windows = [
                window for window in self.list_windows()
                if title.lower() in window["title"].lower()
            ]
            if not windows:
                return {"success": False, "error": f"Window '{title}' not found"}
            
            hwnd = windows[0]["hwnd"]
            window_title = windows[0]["title"]
            
            # 恢复窗口（如果最小化）
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            
            # 设置前台窗口
            ctypes.windll.user32.SetForegroundWindow(hwnd)
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
            import os
            import time
            from PIL import ImageGrab

            # 确保截图目录存在
            screenshot_dir = os.path.join(os.path.dirname(__file__), "../../computer-mcp/screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            # 截图
            prefix = getattr(self, "PLATFORM", "unknown")
            filename = os.path.join(screenshot_dir, f"{prefix}_shot_{int(time.time()*1000)}.png")
            screenshot = ImageGrab.grab()
            screenshot.save(filename)

            return {
                "success": True,
                "screenshot_path": os.path.abspath(filename),
                "screenshot_width": screenshot.size[0],
                "screenshot_height": screenshot.size[1],
                "screen_resolution": {"width": screenshot.size[0], "height": screenshot.size[1]},
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
            import psutil
            import pyautogui
            windows = []
            browser_names = ["chrome", "msedge", "firefox", "brave", "opera"]
            for window in self.mcp.list_windows():
                title = window["title"]
                if not any(keyword in title.lower() for keyword in ["微博", "weibo", "Weibo", "新浪微博"]):
                    continue

                try:
                    process_name = psutil.Process(window["pid"]).name().lower()
                except Exception:
                    continue

                if any(browser in process_name for browser in browser_names):
                    windows.append({
                        "hwnd": window["hwnd"],
                        "title": title,
                        "process": process_name,
                    })
            
            if not windows:
                print("  [debug] 未找到微博窗口")
                return None

            hwnd = windows[0]['hwnd']
            
            # 获取客户区（内容区域，扣除标题栏和边框）
            import ctypes
            import ctypes.wintypes

            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
            point = ctypes.wintypes.POINT(0, 0)
            ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(point))
            
            return {
                "left": point.x,
                "top": point.y,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top,
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

    def bbox_to_center(self, bbox: list) -> tuple:
        """
        将边界框 [X1,Y1,X2,Y2] 转换为中心点 (center_x, center_y)
        
        Args:
            bbox: [X1, Y1, X2, Y2] 百分比坐标 (0-1)
        
        Returns:
            (center_x, center_y) 百分比坐标
            
        Raises:
            ValueError: bbox 格式错误或值无效
            
        Example:
            >>> bbox_to_center([0.47, 0.25, 0.61, 0.30])
            (0.54, 0.275)
        """
        # 验证 bbox 是长度为4的列表
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise ValueError(f"bbox must be a list with 4 elements, got {type(bbox).__name__} with {len(bbox) if isinstance(bbox, list) else 'N/A'} elements")
        
        # 验证所有值都是数字
        for i, val in enumerate(bbox):
            if not isinstance(val, (int, float)):
                raise ValueError(f"bbox[{i}] must be a number, got {type(val).__name__}")
        
        x1, y1, x2, y2 = bbox
        
        # 验证值在 0-1 范围内
        for i, val in enumerate(bbox):
            if not (0.0 <= float(val) <= 1.0):
                raise ValueError(f"bbox[{i}] must be between 0.0 and 1.0, got {val}")
        
        # 验证 x1 < x2, y1 < y2
        if x1 >= x2:
            raise ValueError(f"bbox[0] (X1) must be less than bbox[2] (X2), got {x1} >= {x2}")
        if y1 >= y2:
            raise ValueError(f"bbox[1] (Y1) must be less than bbox[3] (Y2), got {y1} >= {y2}")
        
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        return (center_x, center_y)

    def bbox_to_screen_coords(
        self,
        bbox: list,
        window_rect: dict,
        screenshot_width: int = None,
        screenshot_height: int = None
    ) -> tuple:
        """
        将边界框直接转换为屏幕坐标
        
        组合: bbox -> center -> screen
        
        Args:
            bbox: [X1, Y1, X2, Y2] 百分比坐标（相对于截图）
            window_rect: {"left": int, "top": int, "width": int, "height": int}
            screenshot_width: 截图真实宽度（像素），默认使用 window_rect["width"]
            screenshot_height: 截图真实高度（像素），默认使用 window_rect["height"]
        
        Returns:
            (screen_x, screen_y) 像素坐标
        """
        # 获取中心点（会验证 bbox）
        center_x, center_y = self.bbox_to_center(bbox)
        
        # 验证 window_rect
        required_keys = ["left", "top", "width", "height"]
        for key in required_keys:
            if key not in window_rect:
                raise ValueError(f"window_rect must contain '{key}' key")
            if not isinstance(window_rect[key], int):
                raise ValueError(f"window_rect['{key}'] must be an integer")
        
        # 使用截图真实尺寸，如果没有提供则使用窗口尺寸
        img_width = screenshot_width if screenshot_width else window_rect["width"]
        img_height = screenshot_height if screenshot_height else window_rect["height"]
        
        # 计算截图中的像素坐标
        img_pixel_x = int(img_width * center_x)
        img_pixel_y = int(img_height * center_y)
        
        # 转换为屏幕坐标（加上窗口偏移）
        screen_x = window_rect["left"] + img_pixel_x
        screen_y = window_rect["top"] + img_pixel_y
        
        return (screen_x, screen_y)

    def _open_browser_with_cdp(self, url: str) -> Dict[str, Any]:
        """
        用 --remote-debugging-port=9222 参数启动浏览器。

        优先使用系统默认浏览器，按 Edge → Chrome → 系统默认顺序尝试。
        如果已有 CDP 端口可用，直接通过 webbrowser 打开即可（复用已有实例）。
        """
        import os

        # 如果已有 CDP 端口，用 webbrowser 打开（复用到已有调试实例）
        if self._find_cdp_port():
            return self.mcp.open_browser(url)

        # 没有 CDP 端口，需要新启动
        browser_candidates = [
            # Edge 常见路径
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            # Chrome 常见路径
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        # 找到了就用 subprocess 带 CDP 启动
        # 不传 URL（用 about:blank），避免与崩溃恢复的旧标签重复
        # 微博 URL 后续通过 CDP Page.navigate 打开，确保只有一个微博标签页
        for exe in browser_candidates:
            if os.path.exists(exe):
                print(f"  启动: {exe}")
                subprocess.Popen(
                    [exe, f"--remote-debugging-port=9222", "--remote-allow-origins=*"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(3)
                # 浏览器已带 CDP 运行，用 webbrowser 在当前实例中打开微博
                # （这样只产生一个标签页，不重复）
                import webbrowser
                webbrowser.open(url)
                return {"success": True, "message": f"已启动 {exe}"}

        # 找不到已知浏览器，降级为 webbrowser.open（不带 CDP 参数）
        print("  未找到 Edge/Chrome 路径，使用默认浏览器（无 CDP）")
        return self.mcp.open_browser(url)

    def find_or_open_weibo(self) -> bool:
        """
        查找或打开微博窗口
        优先查找已打开的浏览器窗口（标题包含"微博"），未找到则打开默认浏览器
        返回：是否成功找到/打开窗口
        """
        print("正在查找浏览器窗口...")
        
        # 浏览器进程名称列表
        browser_names = ["chrome", "msedge", "firefox", "brave", "opera"]
        
        try:
            import psutil
            windows = []
            for window in self.mcp.list_windows():
                title = window["title"]

                # 检查标题是否包含微博相关关键词
                weibo_keywords = ["微博", "weibo", "Weibo", "新浪微博"]
                has_weibo = any(keyword.lower() in title.lower() for keyword in weibo_keywords)
                if not has_weibo:
                    continue

                # 获取窗口所属进程
                try:
                    process = psutil.Process(window["pid"])
                    process_name = process.name().lower()

                    # 检查是否是浏览器进程
                    is_browser = any(browser in process_name for browser in browser_names)

                    if is_browser:
                        windows.append({
                            "hwnd": window["hwnd"],
                            "title": title,
                            "process": process_name,
                            "pid": window["pid"],
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
                    pass
            
            if windows:
                # 找到浏览器窗口，聚焦它
                hwnd = windows[0]['hwnd']
                title = windows[0]['title']
                process = windows[0]['process']
                
                print(f"✓ 找到浏览器窗口: {title} ({process})")
                
                # 恢复窗口（如果最小化）
                import ctypes
                ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                
                # 设置前台窗口
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                
                self.window_found = True
                return True
                
        except ImportError as e:
            print(f"  警告: 缺少必要的库 ({e})，回退到简单标题匹配")
        except Exception as e:
            print(f"  查找窗口时出错: {e}")
        
        # 未找到浏览器窗口，启动浏览器并打开微博（带 CDP 调试端口）
        print("未找到浏览器窗口，正在启动浏览器（带 CDP 调试端口）...")
        result = self._open_browser_with_cdp("https://weibo.com")
        
        if not result.get("success"):
            print(f"✗ 打开浏览器失败: {result.get('error')}")
            return False
        
        # 等待页面加载（给足够时间）
        print("等待浏览器和页面加载...")
        self.mcp.wait(5)
        
        # 多次尝试聚焦（页面加载需要时间）
        for attempt in range(5):
            print(f"尝试聚焦浏览器窗口 (第 {attempt + 1} 次)...")
            
            try:
                import psutil
                browser_windows = []
                for window in self.mcp.list_windows():
                    title = window["title"]
                    weibo_keywords = ["微博", "weibo", "Weibo", "新浪微博"]
                    if not any(keyword.lower() in title.lower() for keyword in weibo_keywords):
                        continue

                    try:
                        process_name = psutil.Process(window["pid"]).name().lower()
                    except Exception:
                        continue

                    browser_names = ["chrome", "msedge", "firefox", "brave", "opera"]
                    if any(browser in process_name for browser in browser_names):
                        browser_windows.append({
                            "hwnd": window["hwnd"],
                            "title": title,
                        })
                
                if browser_windows:
                    hwnd = browser_windows[0]['hwnd']
                    title = browser_windows[0]['title']
                    
                    # 恢复并聚焦
                    import ctypes
                    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    time.sleep(0.5)
                    
                    print(f"✓ 成功聚焦浏览器窗口: {title}")
                    self.window_found = True
                    return True
                    
            except Exception as e:
                print(f"  查找浏览器窗口时出错: {e}")
            
            self.mcp.wait(2)
        
        print("⚠ 无法再次聚焦浏览器窗口，但微博页面已打开，继续执行")
        self.window_found = True
        return True
    
    # ===== CDP 登录检测 =====

    def _find_cdp_port(self) -> Optional[int]:
        """
        扫描本地 CDP 调试端口，找到可用端口。

        默认扫描 9222~9225，检测 http://127.0.0.1:{port}/json/version
        是否可访问。

        Returns:
            可用端口号，未找到则返回 None
        """
        import urllib.request
        import urllib.error

        for port in range(9222, 9226):
            try:
                url = f"http://127.0.0.1:{port}/json/version"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=1) as resp:
                    if resp.status == 200:
                        return port
            except (urllib.error.URLError, OSError, TimeoutError):
                continue
        return None

    def _cdp_login_check(self, port: int) -> dict:
        """
        通过 CDP 协议检测微博登录状态。

        使用 Network.getCookies 检查 weibo.com 的 SUB Cookie
        （HttpOnly Cookie，无需 JS/DOM 判断）。

        Returns:
            {"loggedIn": True/False, "userName": str/None, "method": "cdp"}
            失败返回 {"method": "cdp", "error": str}
        """
        import json as _json
        import urllib.request
        import urllib.error

        try:
            # 1. 获取页面 target 列表
            targets_url = f"http://127.0.0.1:{port}/json"
            req = urllib.request.Request(targets_url)
            with urllib.request.urlopen(req, timeout=2) as resp:
                targets = _json.loads(resp.read().decode())

            # 找 weibo.com 的 target
            ws_url = None
            for t in targets:
                page_url = t.get("url", "")
                if "weibo.com" in page_url:
                    ws_url = t.get("webSocketDebuggerUrl")
                    break

            if not ws_url:
                return {"method": "cdp", "error": "未找到 weibo.com 页面标签"}

            # 2. WebSocket 连接，调用 Network.getCookies
            try:
                from websocket import create_connection
            except ImportError:
                return {"method": "cdp", "error": "websocket-client 未安装，请运行: pip install websocket-client"}

            ws = create_connection(
                ws_url,
                timeout=3,
                header={"Origin": f"http://127.0.0.1:{port}"},
            )

            # 发送 Network.getCookies 命令
            msg_id = 1
            ws.send(_json.dumps({
                "id": msg_id,
                "method": "Network.getCookies",
                "params": {"urls": ["https://weibo.com"]}
            }))

            # 收响应（5 秒超时）
            ws.settimeout(5)
            raw = ws.recv()
            response = _json.loads(raw)
            ws.close()

            cookies = response.get("result", {}).get("cookies", [])

            # 3. 检查 SUB Cookie
            sub_cookie = None
            for c in cookies:
                if c.get("name") == "SUB":
                    sub_cookie = c
                    break

            if sub_cookie:
                # SUB Cookie 存在 → 已登录
                # 尝试从 Cookie 值中提取用户名（SUB 是加密 token，无法直接解析用户名）
                return {
                    "loggedIn": True,
                    "userName": None,
                    "method": "cdp",
                    "cookie_domain": sub_cookie.get("domain"),
                }
            else:
                # SUB Cookie 不存在 → 未登录
                return {
                    "loggedIn": False,
                    "userName": None,
                    "method": "cdp",
                    "cookie_count": len(cookies),
                }

        except Exception as e:
            return {"method": "cdp", "error": str(e)}

    def _ollama_login_check(self, screenshot_path: str) -> dict:
        """
        使用 Ollama Vision 分析截图判断登录状态（CDP 不可用时的兜底方案）。

        Returns:
            {"loggedIn": True/False/None, "method": "ollama_vision", ...}
        """
        try:
            from ollama_vision import call_ollama

            prompt = """这张微博首页截图中，用户是否已登录？请以纯 JSON 格式回答，不要其他文字。

判断标准：
- 已登录：顶部导航栏显示用户昵称/头像，没有「登录」和「注册」按钮
- 未登录：顶部有明显的「登录」和「注册」按钮/链接

返回格式：
{"loggedIn": true/false, "reason": "简短说明"}

注意：只返回 JSON，不要任何其他内容。"""

            response = call_ollama(
                model="qwen3.5:397b-cloud",
                prompt=prompt,
                image_path=screenshot_path,
                host="http://localhost:11434",
                stream=False,
            )

            content = response.get("message", {}).get("content", "")
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                import json as _json
                result = _json.loads(json_match.group(0))
                return {
                    "loggedIn": result.get("loggedIn"),
                    "method": "ollama_vision",
                    "reason": result.get("reason", ""),
                }
            else:
                return {"method": "ollama_vision", "error": f"响应解析失败: {content[:200]}"}

        except ImportError:
            return {"method": "ollama_vision", "error": "ollama_vision 模块不可用"}
        except Exception as e:
            return {"method": "ollama_vision", "error": str(e)}

    def check_login_status(self) -> Dict[str, Any]:
        """
        检查微博登录状态。

        检测链路（按优先级降级）：
        1. CDP Network.getCookies → 精确检测 SUB Cookie
        2. Ollama Vision → 本地视觉模型分析截图
        3. 兜底 → 返回截图路径，由外部 AI 判断
        """
        # 确保窗口存在
        if not self.window_found:
            if not self.find_or_open_weibo():
                return {
                    "loggedIn": None,
                    "userName": None,
                    "screenshot_path": None,
                    "error": "无法打开微博窗口",
                }

        # 截图（CDP 失败时 Ollama / 外部 AI 都需要）
        result = self.mcp.inspect_screen()
        if not result.get("success"):
            return {
                "loggedIn": None,
                "userName": None,
                "screenshot_path": None,
                "error": "截图失败",
            }

        screenshot_path = result.get("screenshot_path")

        # 第 1 层：CDP 检测
        cdp_port = self._find_cdp_port()
        if cdp_port is not None:
            cdp_result = self._cdp_login_check(cdp_port)
            if cdp_result.get("loggedIn") is not None:
                return {
                    "loggedIn": cdp_result["loggedIn"],
                    "userName": cdp_result.get("userName"),
                    "screenshot_path": screenshot_path,
                    "method": "cdp",
                }

        # 第 2 层：Ollama Vision 兜底
        ollama_result = self._ollama_login_check(screenshot_path)
        if ollama_result.get("loggedIn") is not None:
            return {
                "loggedIn": ollama_result["loggedIn"],
                "userName": None,
                "screenshot_path": screenshot_path,
                "method": "ollama_vision",
            }

        # 第 3 层：返回截图由外部 AI 判断
        cdp_err = "CDP 端口不可用"
        ollama_err = ollama_result.get("error")
        if cdp_port is not None:
            cdp_err = cdp_result.get("error", cdp_err)

        return {
            "loggedIn": None,
            "userName": None,
            "screenshot_path": screenshot_path,
            "method": "fallback",
            "cdp_error": cdp_err,
            "ollama_error": ollama_err,
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
