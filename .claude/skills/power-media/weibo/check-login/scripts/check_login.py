#!/usr/bin/env python3
"""
weibo-check-login: 检查微博登录状态
自动打开默认浏览器并访问微博，复用已登录状态
"""
import sys
import os
import json

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from computer_mcp_client import WeiboAutomation


def main():
    """主函数"""
    print("=" * 50)
    print("微博登录状态检查")
    print("=" * 50)
    
    try:
        # 创建微博自动化实例
        weibo = WeiboAutomation()
        
        # 查找或打开微博窗口
        print("\n1. 查找或打开微博窗口...")
        if not weibo.find_or_open_weibo():
            result = {
                "loggedIn": False,
                "userName": None,
                "error": "无法打开微博窗口"
            }
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        
        print("✓ 微博窗口已就绪")
        
        # 检查登录状态
        print("\n2. 检查登录状态...")
        status = weibo.check_login_status()
        
        # 输出结果
        print("\n" + "=" * 50)
        method = status.get("method", "unknown")
        logged_in = status.get("loggedIn")

        if logged_in is True:
            print(f"✓ 已登录 (检测方式: {method})")
            user_name = status.get('userName')
            if user_name:
                print(f"  用户名: {user_name}")
        elif logged_in is False:
            print(f"✗ 未登录 (检测方式: {method})")
            if status.get("error"):
                print(f"  错误: {status['error']}")
        else:
            print(f"? 无法判断登录状态 (检测方式: {method})")
            cdp_err = status.get("cdp_error")
            ollama_err = status.get("ollama_error")
            if cdp_err:
                print(f"  CDP: {cdp_err}")
            if ollama_err:
                print(f"  Ollama: {ollama_err}")
            print(f"  请查看截图: {status.get('screenshot_path', 'N/A')}")
        print("=" * 50)
        
        # 输出 JSON 结果
        print(f"\n结果: {json.dumps(status, ensure_ascii=False, indent=2)}")
        
        return status
        
    except Exception as e:
        error_result = {
            "loggedIn": False,
            "userName": None,
            "error": str(e)
        }
        print(f"\n✗ 执行出错: {e}")
        print(f"\n结果: {json.dumps(error_result, ensure_ascii=False, indent=2)}")
        return error_result


if __name__ == "__main__":
    result = main()

    # 仅明确未登录时返回非零退出码
    # loggedIn=None 表示需人工看截图，不报错
    if result.get("loggedIn") is False:
        sys.exit(1)
