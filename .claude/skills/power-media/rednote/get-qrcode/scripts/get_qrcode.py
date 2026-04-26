#!/usr/bin/env python3
"""
获取小红书创作者平台登录二维码
"""
import sys
import os
import json
import time

# 添加 lib 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def wait_for_login(automation, timeout=120, check_interval=3):
    """
    等待用户扫码登录
    
    参数:
        automation: RedNoteAutomation 实例
        timeout: 超时时间（秒），默认 120 秒
        check_interval: 检查间隔（秒），默认 3 秒
    """
    print(f"\n等待用户扫码登录（最多等待 {timeout} 秒）...")
    start_time = time.time()
    check_count = 0

    while time.time() - start_time < timeout:
        check_count += 1
        elapsed = int(time.time() - start_time)
        print(f"\n[{elapsed}s] 第 {check_count} 次检查登录状态...")

        # 截图检查
        result = automation.check_login_status()

        if not result.get("success"):
            print(f"  截图失败: {result.get('error')}")
            time.sleep(check_interval)
            continue

        screenshot_path = result.get("screenshot_path")
        print(f"  截图已保存: {screenshot_path}")
        print(f"  请 AI 分析截图判断是否已登录")

        # AI 需要分析截图，如果检测到已登录（有用户头像），则退出循环
        # 这里我们返回截图信息，由 AI 判断
        # 实际使用中，AI 会分析截图并告诉脚本是否已登录

        # 暂时返回，等待 AI 分析
        return {
            "success": True,
            "status": "waiting_for_ai_analysis",
            "screenshot_path": screenshot_path,
            "elapsed": elapsed,
            "message": "请 AI 分析截图判断是否已登录"
        }

        time.sleep(check_interval)

    # 超时
    return {
        "success": False,
        "status": "timeout",
        "message": f"登录超时（{timeout} 秒），请刷新页面重新获取二维码",
        "elapsed": timeout
    }


def main():
    """主函数"""
    print("=" * 60)
    print("📱 获取小红书创作者平台登录二维码")
    print("=" * 60)
    print()

    automation = RedNoteAutomation()

    # 1. 查找/打开窗口
    print("1. 查找创作者平台窗口...")
    if not automation.find_or_open_creator():
        print("✗ 无法打开创作者平台窗口")
        print(json.dumps({
            "success": False,
            "error": "无法打开创作者平台窗口"
        }, ensure_ascii=False, indent=2))
        return

    # 2. 检查是否已登录
    print("\n2. 检查当前登录状态...")
    login_status = automation.check_login_status()

    if not login_status.get("success"):
        print(f"✗ 检查失败: {login_status.get('error')}")
        print(json.dumps(login_status, ensure_ascii=False, indent=2))
        return

    screenshot_path = login_status.get("screenshot_path")
    print(f"\n✓ 截图已保存: {screenshot_path}")
    print("\n请 AI 分析截图:")
    print("  - 如已登录（有用户头像）→ 提示用户已登录，无需扫码")
    print("  - 如未登录（显示二维码）→ 提示用户扫码")

    # 3. 等待登录（如未登录）
    print("\n3. 等待用户扫码登录...")
    print("   请使用小红书 APP 扫描屏幕上的二维码")
    print("   二维码有效期约 2 分钟，超时需刷新页面\n")

    result = wait_for_login(automation, timeout=120, check_interval=3)

    print("\n" + "=" * 60)
    print("JSON 输出:")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
