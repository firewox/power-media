#!/usr/bin/env python3
"""
搜索小红书内容
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def main():
    parser = argparse.ArgumentParser(description='搜索小红书内容')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--sort', choices=['综合', '最新', '最多点赞'], default='综合', help='排序方式')

    args = parser.parse_args()

    print(f"🔍 搜索小红书: {args.keyword}")

    automation = RedNoteAutomation()

    if not automation.find_or_open_creator():
        print(json.dumps({"success": False, "error": "无法打开创作者平台窗口"}, ensure_ascii=False))
        return

    # 导航到搜索页
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={args.keyword}"
    automation.navigate_to(search_url)
    automation.mcp.wait(3)

    # 截图识别
    result = automation.mcp.inspect_screen()

    output = {
        "success": True,
        "keyword": args.keyword,
        "sort": args.sort,
        "screenshot_path": result.get("screenshot_path"),
        "message": "请 AI 分析截图提取搜索结果"
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
