#!/usr/bin/env python3
"""
weibo-post-text: 发布纯文本微博
使用百分比坐标，自动适配不同屏幕分辨率
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from computer_mcp_client import WeiboAutomation


def validate_content(content: str) -> tuple:
    """验证微博内容"""
    if not content:
        return False, "内容不能为空"
    if len(content) > 140:
        return False, f"内容超长: {len(content)} 字符 (最多 140 字符)"
    return True, None


def main():
    parser = argparse.ArgumentParser(description="发布纯文本微博")
    parser.add_argument("content", help="微博内容")
    parser.add_argument("--input-x", type=float, help="输入框 X 百分比 (0~1)")
    parser.add_argument("--input-y", type=float, help="输入框 Y 百分比 (0~1)")
    parser.add_argument("--send-x", type=float, help="发送按钮 X 百分比 (0~1)")
    parser.add_argument("--send-y", type=float, help="发送按钮 Y 百分比 (0~1)")

    args = parser.parse_args()
    content = args.content

    print("=" * 50)
    print("发布纯文本微博")
    print("=" * 50)

    print(f"\n内容: {content}")
    is_valid, error = validate_content(content)
    if not is_valid:
        result = {"success": False, "error": error}
        print(f"\n✗ {error}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    print(f"✓ 内容验证通过 ({len(content)} 字符)")

    try:
        weibo = WeiboAutomation()

        print("\n1. 查找或打开微博窗口...")
        if not weibo.find_or_open_weibo():
            result = {"success": False, "error": "无法打开微博窗口"}
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        print("✓ 微博窗口已就绪")

        print("\n2. 截图检查页面状态...")
        status = weibo.check_login_status()
        print(f"截图路径: {status.get('screenshot_path')}")

        if args.input_x is not None and args.send_x is not None:
            print("\n3. 发布微博...")
            result = weibo.post_text_weibo(
                content,
                input_box_pct=(args.input_x, args.input_y),
                send_btn_pct=(args.send_x, args.send_y)
            )
        else:
            result = {
                "success": False,
                "need_coords": True,
                "screenshot_path": status.get("screenshot_path"),
                "message": "请分析截图，提供百分比坐标 (0~1 之间)",
                "usage": "python post_text.py '内容' --input-x 0.42 --input-y 0.17 --send-x 0.58 --send-y 0.17"
            }

        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        print(f"\n✗ 执行出错: {e}")
        print(f"\n结果: {json.dumps(error_result, ensure_ascii=False, indent=2)}")
        return error_result


if __name__ == "__main__":
    result = main()
    if not result.get("success") and not result.get("need_coords"):
        sys.exit(1)
