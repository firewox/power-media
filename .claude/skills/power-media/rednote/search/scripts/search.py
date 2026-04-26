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

    # 1. 查找/打开搜索页面 (explore 页面，不是 creator 页面)
    print("\n1. 查找小红书搜索页面...")
    if not automation.find_or_open_creator(page_type="explore"):
        print(json.dumps({"success": False, "error": "无法打开小红书搜索页面"}, ensure_ascii=False))
        return

    # 2. 验证当前页面是否为小红书
    print("\n2. 验证当前页面...")
    check_result = automation.mcp.inspect_screen()

    # 多模态 AI 需要确认截图是否为小红书页面
    # 如果不是 explore 页面，导航到 explore
    if check_result.get("success"):
        print(f"  截图已保存: {check_result.get('screenshot_path')}")
        print("  请多模态 AI 确认是否为小红书探索页面")

    # 3. 使用页面内搜索框搜索
    print(f"\n3. 使用搜索框搜索: {args.keyword}")
    result = automation.search_in_page(args.keyword)

    if not result.get("success"):
        print(f"✗ 搜索失败: {result.get('error')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    output = {
        "success": True,
        "keyword": args.keyword,
        "sort": args.sort,
        "screenshot_path": result.get("screenshot_path"),
        "message": "请多模态 AI 分析截图提取搜索结果"
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
