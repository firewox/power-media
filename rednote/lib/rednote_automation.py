#!/usr/bin/env python3
"""
RedNote Automation - 小红书创作者平台自动化封装
基于 computer-mcp 实现
"""
import sys
import os
import time

# 添加 computer_mcp_client 到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from computer_mcp_client import ComputerMCPClient
except ImportError:
    # 如果 rednote/lib 下没有，尝试从 weibo/lib 导入
    weibo_lib = os.path.join(current_dir, '../../weibo/lib')
    sys.path.insert(0, weibo_lib)
    from computer_mcp_client import ComputerMCPClient


class RedNoteAutomation:
    """小红书创作者平台自动化操作"""

    CREATOR_URL = "https://creator.xiaohongshu.com/"
    PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish"
    
    WINDOW_TITLES = [
        "小红书创作者中心",
        "creator.xiaohongshu.com",
        "小红书 - ",
        "创作者中心",
        "小红书",
    ]

    def __init__(self):
        self.mcp = ComputerMCPClient()
        self.window_found = False
        self.window_rect = None

    def find_or_open_creator(self) -> bool:
        """查找或打开小红书创作者平台窗口"""
        print("正在查找小红书创作者平台窗口...")

        for title in self.WINDOW_TITLES:
            result = self.mcp.focus_window(title)
            if result.get("success"):
                print(f"✓ 找到小红书窗口 (标题: {title})")
                self.window_found = True
                self._try_get_window_rect()
                return True

        # 未找到，打开浏览器
        print("未找到小红书窗口，正在打开浏览器...")
        result = self.mcp.open_browser(self.CREATOR_URL)

        if not result.get("success"):
            print(f"✗ 打开浏览器失败: {result.get('error')}")
            return False

        # 等待页面加载
        print("等待页面加载...")
        self.mcp.wait(5)

        # 再次尝试聚焦
        for attempt in range(3):
            print(f"尝试聚焦 (第 {attempt + 1} 次)...")
            for title in self.WINDOW_TITLES:
                result = self.mcp.focus_window(title)
                if result.get("success"):
                    print(f"✓ 成功聚焦 (标题: {title})")
                    self.window_found = True
                    self._try_get_window_rect()
                    return True
            self.mcp.wait(2)

        print("✗ 无法聚焦小红书窗口")
        self.window_found = False
        return False

    def _try_get_window_rect(self):
        """尝试获取窗口区域"""
        try:
            import win32gui
            
            def callback(hwnd, result):
                title = win32gui.GetWindowText(hwnd)
                if win32gui.IsWindowVisible(hwnd):
                    if any(kw in title for kw in ["小红书", "creator.xiaohongshu"]):
                        try:
                            client_rect = win32gui.GetClientRect(hwnd)
                            pt = win32gui.ClientToScreen(hwnd, (0, 0))
                            result.append({
                                "left": pt[0],
                                "top": pt[1],
                                "width": client_rect[2],
                                "height": client_rect[3],
                            })
                        except:
                            pass
                return True

            windows = []
            win32gui.EnumWindows(callback, windows)

            if windows:
                self.window_rect = windows[0]
                print(f"  窗口区域: ({self.window_rect['left']}, {self.window_rect['top']}) "
                      f"{self.window_rect['width']}x{self.window_rect['height']}")
        except Exception as e:
            print(f"  [debug] 获取窗口区域失败: {e}")

    def get_browser_window_rect(self) -> dict:
        """获取浏览器窗口的内容区域"""
        if not self.window_rect:
            self._try_get_window_rect()
        return self.window_rect

    def pct_to_screen_coords(self, pct_x: float, pct_y: float) -> tuple:
        """百分比坐标转屏幕绝对坐标"""
        if self.window_rect:
            wr = self.window_rect
            x = wr["left"] + int(wr["width"] * pct_x)
            y = wr["top"] + int(wr["height"] * pct_y)
            return (x, y)

        # 降级方案：基于全屏计算
        import pyautogui
        screen_w, screen_h = pyautogui.size()
        return (int(screen_w * pct_x), int(screen_h * pct_y))

    def check_login_status(self) -> dict:
        """检查登录状态，返回截图供多模态 AI 分析"""
        if not self.window_found:
            if not self.find_or_open_creator():
                return {
                    "success": False,
                    "loggedIn": None,
                    "error": "无法打开创作者平台窗口"
                }

        result = self.mcp.inspect_screen()

        if not result.get("success"):
            return {
                "success": False,
                "loggedIn": None,
                "error": "截图失败",
                "screenshot_path": None
            }

        return {
            "success": True,
            "loggedIn": None,  # 由多模态 AI 分析截图判断
            "screenshot_path": result.get("screenshot_path"),
        }

    def navigate_to(self, url: str) -> bool:
        """导航到指定 URL"""
        print(f"  导航到: {url}")
        
        # Ctrl+L 聚焦地址栏
        self.mcp.hotkey(["ctrl", "l"])
        self.mcp.wait(0.5)

        # 全选旧 URL
        self.mcp.hotkey(["ctrl", "a"])
        self.mcp.wait(0.3)

        # 输入新 URL
        self.mcp.type_text(url)
        self.mcp.wait(0.3)

        # 回车
        self.mcp.press_key("enter")
        self.mcp.wait(3)

        return True

    def find_element_by_ocr(self, keywords: list, screenshot_result: dict = None) -> dict:
        """
        通过 OCR 结果查找元素坐标
        
        参数:
            keywords: 关键词列表
            screenshot_result: 已有的截图结果（可选）
            
        返回:
            {"success": True, "x": x, "y": y, "text": "匹配的文字"}
            或 {"success": False, "error": "未找到匹配的元素"}
        """
        # 如果没有截图结果，先截图
        if not screenshot_result:
            screenshot_result = self.mcp.inspect_screen()
            if not screenshot_result.get("success"):
                return {"success": False, "error": "截图失败"}

        # 这里需要 AI 分析 OCR 结果，返回匹配元素的坐标
        # 实际使用时，由 AI 分析 inspect_screen 的返回结果
        return {
            "success": False,
            "error": "需要 AI 分析截图结果",
            "screenshot_path": screenshot_result.get("screenshot_path")
        }


if __name__ == "__main__":
    print("=" * 60)
    print("RedNote Automation 测试")
    print("=" * 60)
    
    rednote = RedNoteAutomation()
    
    print("\n1. 正在查找/打开创作者平台窗口...")
    if rednote.find_or_open_creator():
        print("✓ 窗口已就绪")
    else:
        print("✗ 窗口打开失败")
        sys.exit(1)

    print("\n2. 正在检查登录状态...")
    status = rednote.check_login_status()
    print(f"登录状态检查: {status}")
    
    if status.get("screenshot_path"):
        print(f"\n截图已保存: {status['screenshot_path']}")
        print("请 AI 分析截图判断登录状态")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
