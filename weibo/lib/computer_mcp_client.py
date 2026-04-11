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
    
    def __init__(self):
        self.server_path = self._find_mcp_server()
    
    def _find_mcp_server(self) -> str:
        """查找 MCP 服务器脚本路径"""
        # 尝试常见路径
        possible_paths = [
            "computer-mcp/server.py",
            "../computer-mcp/server.py",
            "../../computer-mcp/server.py",
            "C:/Users/%USERNAME%/.claude/computer-mcp/server.py",
        ]
        
        for path in possible_paths:
            import os
            if os.path.exists(path):
                return path
        
        # 如果找不到，假设在环境变量中
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
        """聚焦窗口"""
        return self.call_tool("computer-mcp/focus_window", {"title": title})
    
    def open_browser(self, url: Optional[str] = None) -> Dict[str, Any]:
        """打开默认浏览器"""
        import webbrowser
        import os
        
        # 使用 Windows 默认浏览器打开
        if url:
            webbrowser.open(url)
        else:
            webbrowser.open("about:blank")
        
        time.sleep(2)  # 等待浏览器打开
        
        return {"success": True, "message": "Browser opened"}
    
    def inspect_screen(self) -> Dict[str, Any]:
        """截图并识别界面元素"""
        return self.call_tool("computer-mcp/inspect_screen", {})
    
    def click(self, x: int, y: int) -> Dict[str, Any]:
        """点击指定坐标"""
        return self.call_tool("computer-mcp/click", {"x": x, "y": y})
    
    def type_text(self, text: str) -> Dict[str, Any]:
        """输入文本"""
        return self.call_tool("computer-mcp/type_text", {"text": text})
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """按键"""
        return self.call_tool("computer-mcp/press_key", {"key": key})
    
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
    
    def find_or_open_weibo(self) -> bool:
        """
        查找或打开微博窗口
        返回：是否成功找到/打开窗口
        """
        # 尝试聚焦现有窗口
        result = self.mcp.focus_window("微博")
        
        if result.get("success"):
            self.window_found = True
            return True
        
        # 尝试其他可能的标题
        for title in ["Weibo", "微博", "weibo.com"]:
            result = self.mcp.focus_window(title)
            if result.get("success"):
                self.window_found = True
                return True
        
        # 未找到，打开浏览器
        print("未找到微博窗口，正在打开默认浏览器...")
        self.mcp.open_browser("https://weibo.com")
        
        # 等待页面加载
        self.mcp.wait(5)
        
        # 再次尝试聚焦
        result = self.mcp.focus_window("微博")
        self.window_found = result.get("success", False)
        
        return self.window_found
    
    def check_login_status(self) -> Dict[str, Any]:
        """
        检查微博登录状态
        返回: {"loggedIn": bool, "userName": str|null}
        """
        # 确保窗口存在
        if not self.window_found:
            if not self.find_or_open_weibo():
                return {
                    "loggedIn": False,
                    "userName": None,
                    "error": "无法打开微博窗口"
                }
        
        # 截图识别
        result = self.mcp.inspect_screen()
        
        if not result.get("success"):
            return {
                "loggedIn": False,
                "userName": None,
                "error": "截图识别失败"
            }
        
        # 分析 OCR 结果
        ocr_text = result.get("text", "")
        
        # 检查是否已登录
        logged_in_indicators = ["的微博", "首页", "关注", "粉丝", "个人中心"]
        login_indicators = ["登录", "注册", "账号密码登录", "短信登录"]
        
        is_logged_in = any(indicator in ocr_text for indicator in logged_in_indicators)
        is_login_page = any(indicator in ocr_text for indicator in login_indicators)
        
        if is_logged_in:
            # 尝试提取用户名
            user_name = None
            for indicator in logged_in_indicators:
                if indicator in ocr_text:
                    # 简单提取用户名逻辑
                    idx = ocr_text.find(indicator)
                    if idx > 0:
                        user_name = ocr_text[max(0, idx-10):idx].strip()
                    break
            
            return {
                "loggedIn": True,
                "userName": user_name or "未知用户"
            }
        elif is_login_page:
            return {
                "loggedIn": False,
                "userName": None
            }
        else:
            # 可能是首页或其他页面，再试一次
            self.mcp.wait(2)
            result = self.mcp.inspect_screen()
            ocr_text = result.get("text", "")
            
            is_logged_in = any(indicator in ocr_text for indicator in logged_in_indicators)
            
            return {
                "loggedIn": is_logged_in,
                "userName": None
            }
    
    def click_element_by_text(self, text: str, retry: int = 3) -> bool:
        """
        根据文字点击元素
        返回：是否点击成功
        """
        for i in range(retry):
            result = self.mcp.inspect_screen()
            
            if not result.get("success"):
                continue
            
            # 从 OCR 结果中查找文字位置
            elements = result.get("elements", [])
            for elem in elements:
                if text in elem.get("text", ""):
                    x = elem.get("x", 0)
                    y = elem.get("y", 0)
                    self.mcp.click(x, y)
                    return True
            
            self.mcp.wait(1)
        
        return False
    
    def post_text_weibo(self, content: str) -> Dict[str, Any]:
        """
        发布纯文本微博
        """
        # 检查登录状态
        login_status = self.check_login_status()
        
        if not login_status.get("loggedIn"):
            return {
                "success": False,
                "error": "未登录，请先登录微博"
            }
        
        # 聚焦窗口
        self.mcp.focus_window("微博")
        
        # 点击输入框
        if not self.click_element_by_text("有什么新鲜事想告诉大家"):
            # 尝试其他可能的提示文字
            if not self.click_element_by_text("发布"):
                return {
                    "success": False,
                    "error": "无法找到输入框"
                }
        
        self.mcp.wait(1)
        
        # 输入内容
        self.mcp.type_text(content)
        self.mcp.wait(1)
        
        # 点击发送按钮
        if not self.click_element_by_text("发送"):
            return {
                "success": False,
                "error": "无法找到发送按钮"
            }
        
        # 等待发布
        self.mcp.wait(3)
        
        # 验证发布结果
        result = self.mcp.inspect_screen()
        ocr_text = result.get("text", "")
        
        if "发布成功" in ocr_text or "刚刚" in ocr_text:
            return {
                "success": True,
                "message": "发布成功"
            }
        else:
            return {
                "success": True,
                "message": "已发送，请检查发布结果"
            }


if __name__ == "__main__":
    # 测试代码
    weibo = WeiboAutomation()
    print("正在检查登录状态...")
    status = weibo.check_login_status()
    print(f"登录状态: {status}")
