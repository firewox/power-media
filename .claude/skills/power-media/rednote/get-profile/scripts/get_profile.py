#!/usr/bin/env python3
"""
获取用户主页
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def main():
    parser = argparse.ArgumentParser(description='获取用户主页')
    parser.add_argument('--userId', required=True, help='用户ID')

    args = parser.parse_args()

    print(f"👤 获取用户主页: {args.userId}")

    automation = RedNoteAutomation()

    if not automation.find_or_open_creator():
        print(json.dumps({"success": False, "error": "无法打开创作者平台窗口"}, ensure_ascii=False))
        return

    # 导航到用户主页
    profile_url = f"https://www.xiaohongshu.com/user/profile/{args.userId}"
    automation.navigate_to(profile_url)
    automation.mcp.wait(3)

    # 截图识别
    result = automation.mcp.inspect_screen()

    output = {
        "success": True,
        "userId": args.userId,
        "screenshot_path": result.get("screenshot_path"),
        "message": "请 AI 分析截图提取用户信息"
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
