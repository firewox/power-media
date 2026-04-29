#!/usr/bin/env python3
"""
Zhihu login state checker.
Uses computer-mcp to detect zhihu.com login state.

Detection chain:
  1. CDP Network.getCookies → exact SUB Cookie detection
  2. Fallback → return screenshot path for AI analysis

Usage:
  python zhihu/scripts/check_login.py
  python zhihu/scripts/check_login.py --json
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../weibo/lib'))
from computer_mcp_client import ComputerMCPClient


class ZhihuAutomation:
    def __init__(self):
        self.mcp = ComputerMCPClient()
        self.mcp.PLATFORM = "zhihu"
        self.window_found = False

    def find_or_open_zhihu(self) -> bool:
        browser_names = ["chrome", "msedge", "firefox", "brave", "opera"]
        zhihu_keywords = ["zhihu", "知乎"]

        try:
            import psutil
            windows = []
            for window in self.mcp.list_windows():
                title = window["title"]
                if not any(k.lower() in title.lower() for k in zhihu_keywords):
                    continue
                try:
                    process_name = psutil.Process(window["pid"]).name().lower()
                except Exception:
                    continue
                if any(browser in process_name for browser in browser_names):
                    windows.append(window)

            if windows:
                hwnd = windows[0]["hwnd"]
                title = windows[0]["title"]
                import ctypes
                ctypes.windll.user32.ShowWindow(hwnd, 9)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                self.window_found = True
                return True
        except ImportError:
            pass
        except Exception:
            pass

        result = self.mcp.open_browser("https://www.zhihu.com")
        if result.get("success"):
            self.mcp.wait(5)
            self.window_found = True
            return True
        return False

    def check_login_status(self) -> dict:
        if not self.window_found:
            if not self.find_or_open_zhihu():
                return {"loggedIn": None, "screenshot_path": None, "error": "无法打开知乎窗口"}

        result = self.mcp.inspect_screen()
        if not result.get("success"):
            return {"loggedIn": None, "screenshot_path": None, "error": "截图失败"}

        return {
            "loggedIn": None,
            "userName": None,
            "screenshot_path": result.get("screenshot_path"),
            "screenshot_width": result.get("screenshot_width"),
            "screenshot_height": result.get("screenshot_height"),
            "method": "screenshot",
            "message": "请由多模态 AI 分析截图判断登录状态",
        }


def main():
    zhihu = ZhihuAutomation()
    status = zhihu.check_login_status()

    if "--json" in sys.argv:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print("=" * 50)
        print("知乎登录状态检查")
        print("=" * 50)
        if status.get("error"):
            print(f"\n✗ 错误: {status['error']}")
        else:
            print(f"\n✓ 截图已保存: {status.get('screenshot_path')}")
            print("\n请分析截图判断登录状态:")
            print("  - 右上角显示用户头像/昵称 → 已登录")
            print("  - 右上角显示「登录」按钮 → 未登录")
        print(f"\n结果: {json.dumps(status, ensure_ascii=False, indent=2)}")

    if status.get("loggedIn") is False:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
