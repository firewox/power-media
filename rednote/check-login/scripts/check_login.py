#!/usr/bin/env python3
"""
检查小红书创作者平台登录状态
"""
import sys
import os
import json

# 添加 lib 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 检查小红书创作者平台登录状态")
    print("=" * 60)
    print()

    automation = RedNoteAutomation()

    # 查找/打开窗口
    print("1. 查找创作者平台窗口...")
    if not automation.find_or_open_creator():
        print("✗ 无法打开创作者平台窗口")
        print(json.dumps({
            "success": False,
            "error": "无法打开创作者平台窗口"
        }, ensure_ascii=False, indent=2))
        return

    # 检查登录状态
    print("\n2. 截图检查登录状态...")
    result = automation.check_login_status()

    if not result.get("success"):
        print(f"✗ 检查失败: {result.get('error')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"\n✓ 截图已保存: {result.get('screenshot_path')}")
    print("\n请 AI 分析截图判断登录状态:")
    print("  - 检测到用户头像/昵称 → 已登录")
    print("  - 检测到登录二维码 → 未登录")

    print("\n" + "=" * 60)
    print("JSON 输出:")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
