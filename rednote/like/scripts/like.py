#!/usr/bin/env python3
"""
点赞/取消点赞
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def main():
    parser = argparse.ArgumentParser(description='点赞/取消点赞')
    parser.add_argument('--noteId', required=True, help='笔记ID')
    parser.add_argument('--unlike', action='store_true', help='取消点赞')

    args = parser.parse_args()

    action = "取消点赞" if args.unlike else "点赞"
    print(f"👍 {action}: {args.noteId}")

    automation = RedNoteAutomation()

    if not automation.find_or_open_creator():
        print(json.dumps({"success": False, "error": "无法打开创作者平台窗口"}, ensure_ascii=False))
        return

    # 导航到笔记页
    note_url = f"https://www.xiaohongshu.com/explore/{args.noteId}"
    automation.navigate_to(note_url)
    automation.mcp.wait(3)

    # 截图识别
    result = automation.mcp.inspect_screen()

    output = {
        "success": True,
        "noteId": args.noteId,
        "action": "unlike" if args.unlike else "like",
        "screenshot_path": result.get("screenshot_path"),
        "message": f"请 AI 分析截图并指导{action}操作"
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
