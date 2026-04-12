#!/usr/bin/env python3
"""
发布小红书视频笔记
"""
import sys
import os
import json
import argparse

# 添加 lib 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def validate_inputs(title, content, video, cover=None, tags=None):
    """验证输入参数"""
    errors = []

    if not title or len(title.strip()) == 0:
        errors.append("标题不能为空")
    elif len(title) > 20:
        errors.append(f"标题过长: {len(title)} 字（最多 20 字）")

    if content and len(content) > 1000:
        errors.append(f"正文过长: {len(content)} 字（最多 1000 字）")

    if not video or len(video.strip()) == 0:
        errors.append("视频文件不能为空")
    elif not os.path.exists(video):
        errors.append(f"视频文件不存在: {video}")

    if cover and not os.path.exists(cover):
        errors.append(f"封面文件不存在: {cover}")

    if tags and len(tags) > 10:
        errors.append(f"标签过多: {len(tags)} 个（最多 10 个）")

    return errors


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='发布小红书视频笔记')
    parser.add_argument('--title', required=True, help='笔记标题（最多 20 字）')
    parser.add_argument('--content', help='笔记正文（最多 1000 字）')
    parser.add_argument('--video', required=True, help='视频文件路径（MP4 格式）')
    parser.add_argument('--cover', help='封面图片路径（可选）')
    parser.add_argument('--tags', nargs='+', help='话题标签列表')
    parser.add_argument('--visibility', choices=['public', 'friends', 'private'],
                        default='public', help='可见范围')

    args = parser.parse_args()

    print("=" * 60)
    print("🎬 发布小红书视频笔记")
    print("=" * 60)
    print()

    # 验证输入
    print("1. 验证输入参数...")
    errors = validate_inputs(args.title, args.content, args.video, args.cover, args.tags)
    if errors:
        print("❌ 参数验证失败:")
        for error in errors:
            print(f"  - {error}")
        print(json.dumps({"success": False, "errors": errors}, ensure_ascii=False, indent=2))
        return

    print(f"✓ 标题: {args.title}")
    if args.content:
        print(f"✓ 正文长度: {len(args.content)} 字")
    print(f"✓ 视频文件: {args.video}")
    if args.cover:
        print(f"✓ 封面图片: {args.cover}")
    if args.tags:
        print(f"✓ 话题标签: {', '.join(args.tags)}")

    automation = RedNoteAutomation()

    # 2. 检查登录状态
    print("\n2. 检查登录状态...")
    login_status = automation.check_login_status()
    if not login_status.get("success"):
        print(f"✗ 登录状态检查失败: {login_status.get('error')}")
        print(json.dumps(login_status, ensure_ascii=False, indent=2))
        return

    print(f"✓ 截图已保存: {login_status.get('screenshot_path')}")

    # 3. 导航到发布页
    print("\n3. 导航到发布页...")
    automation.navigate_to(automation.PUBLISH_URL)
    automation.mcp.wait(3)

    # 4. 截图识别页面
    print("4. 截图识别页面...")
    result = automation.mcp.inspect_screen()

    if not result.get("success"):
        print(f"✗ 截图失败: {result.get('error')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"✓ 页面截图: {result.get('screenshot_path')}")

    # 5. 返回信息，由 AI 指导后续操作
    print("\n5. 请 AI 分析截图并指导后续操作:")
    print("  - 识别'上传视频'按钮并点击")
    print("  - 上传视频文件")
    print("  - 填写标题和正文")
    print("  - 设置封面（如提供）")
    print("  - 添加话题标签")
    print("  - 点击发布按钮")

    output = {
        "success": True,
        "message": "已到达发布页，请 AI 分析截图并指导后续操作",
        "screenshot_path": result.get("screenshot_path"),
        "params": {
            "title": args.title,
            "content": args.content,
            "video": args.video,
            "cover": args.cover,
            "tags": args.tags,
            "visibility": args.visibility
        },
        "next_steps": [
            "识别'上传视频'按钮并点击",
            "上传视频文件（MP4 格式，≤2GB）",
            "填写标题（最多20字）",
            "填写正文（可选，最多1000字）",
            "设置封面（如提供封面图片）",
            "添加话题标签（最多10个）",
            "设置可见范围",
            "点击发布按钮",
            "确认发布"
        ]
    }

    print("\n" + "=" * 60)
    print("JSON 输出:")
    print("=" * 60)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
