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

    # 创作服务平台 - 用于发笔记、笔记管理、数据看板
    CREATOR_URL = "https://creator.xiaohongshu.com/"
    PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish"

    # 用户浏览页面 - 用于搜索笔记、查看笔记、浏览他人内容
    EXPLORE_URL = "https://www.xiaohongshu.com/explore"
    SEARCH_URL = "https://www.xiaohongshu.com/search_result"

    # 创作者平台窗口标题
    CREATOR_WINDOW_TITLES = [
        "小红书创作者中心",
        "creator.xiaohongshu.com",
        "小红书 - ",
        "创作者中心",
        "小红书",
    ]

    # 浏览页面窗口标题
    EXPLORE_WINDOW_TITLES = [
        "小红书 - 你的生活指南",
        "www.xiaohongshu.com",
        "小红书",
    ]

    def __init__(self):
        self.mcp = ComputerMCPClient()
        self.window_found = False
        self.window_rect = None

    def find_or_open_creator(self, page_type: str = "creator") -> bool:
        """
        查找或打开小红书窗口
        
        Args:
            page_type: 页面类型
                - "creator": 创作服务平台 (发笔记、管理)
                - "explore": 用户浏览页面 (搜索、查看)
        """
        if page_type == "explore":
            window_titles = self.EXPLORE_WINDOW_TITLES
            target_url = self.EXPLORE_URL
            page_name = "小红书浏览页面"
        else:
            window_titles = self.CREATOR_WINDOW_TITLES
            target_url = self.CREATOR_URL
            page_name = "小红书创作平台"

        print(f"正在查找{page_name}窗口...")

        # 尝试聚焦已有窗口
        for title in window_titles:
            result = self.mcp.focus_window(title)
            if result.get("success"):
                print(f"✓ 找到小红书窗口 (标题: {title})")
                self.window_found = True
                self._try_get_window_rect()

                # 截图确认当前页面
                check_result = self.mcp.inspect_screen()
                screenshot_path = check_result.get("screenshot_path")
                print(f"  截图确认: {screenshot_path}")
                print("  请多模态 AI 确认是否为正确的页面")

                return True

        # 未找到，直接打开新窗口导航到目标页面
        print(f"未找到合适的窗口，直接打开{page_name}...")
        result = self.mcp.open_browser(target_url)

        if not result.get("success"):
            print(f"✗ 打开浏览器失败: {result.get('error')}")
            return False

        # 等待页面加载
        print("等待页面加载...")
        self.mcp.wait(5)

        # 尝试聚焦新窗口
        for attempt in range(3):
            print(f"尝试聚焦 (第 {attempt + 1} 次)...")
            for title in window_titles:
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
        # 确保聚焦创作平台窗口，不是浏览页面
        if not self.window_found:
            if not self.find_or_open_creator(page_type="creator"):
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

    def search_in_page(self, keyword: str) -> dict:
        """
        在小红书搜索页面内使用搜索框搜索

        参数:
            keyword: 搜索关键词

        返回:
            搜索结果截图
        """
        print(f"  在小红书页面内搜索: {keyword}")

        # 1. 确保在正确的搜索页面
        # 直接导航到搜索页面，避免窗口焦点错误问题
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
        print(f"  导航到: {search_url}")
        
        # 尝试导航，最多重试 2 次
        max_retries = 2
        for attempt in range(max_retries):
            self.navigate_to(search_url)
            self.mcp.wait(3)
            
            # 验证是否导航成功
            verify_result = self.mcp.inspect_screen()
            screenshot_path = verify_result.get("screenshot_path")
            print(f"  第 {attempt + 1} 次尝试，截图: {screenshot_path}")
            print("  请多模态 AI 确认：当前页面 URL 是否包含 'search_result'，以及是否显示搜索结果")
            
            # 这里需要 AI 确认页面是否正确
            # 如果不对，继续重试
            if attempt < max_retries - 1:
                print("  如果页面不正确，将重试导航...")
        
        return verify_result

    def navigate_to(self, url: str) -> bool:
        """导航到指定 URL"""
        print(f"  导航到: {url}")

        # 步骤 1: Ctrl+L 聚焦地址栏
        print("  步骤 1: Ctrl+L 聚焦地址栏")
        self.mcp.hotkey(["ctrl", "l"])
        self.mcp.wait(0.8)

        # 步骤 2: Ctrl+A 全选旧 URL（确保清除）
        print("  步骤 2: Ctrl+A 全选")
        self.mcp.hotkey(["ctrl", "a"])
        self.mcp.wait(0.5)

        # 步骤 3: 删除旧内容
        print("  步骤 3: 按 Delete 清除")
        self.mcp.press_key("delete")
        self.mcp.wait(0.3)

        # 步骤 4: 输入新 URL
        print(f"  步骤 4: 输入 URL: {url}")
        self.mcp.type_text(url)
        self.mcp.wait(0.5)

        # 步骤 5: 回车导航
        print("  步骤 5: 按 Enter 导航")
        self.mcp.press_key("enter")
        self.mcp.wait(4)

        # 步骤 6: 验证是否导航成功
        print("  步骤 6: 截图验证")
        result = self.mcp.inspect_screen()
        print(f"  验证截图: {result.get('screenshot_path')}")
        print("  请 AI 确认：地址栏 URL 是否已变为目标 URL？")

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
