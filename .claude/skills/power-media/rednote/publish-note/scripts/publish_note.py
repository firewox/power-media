#!/usr/bin/env python3
"""
发布小红书图文笔记
"""
import sys
import os
import json
import argparse

# 添加 lib 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def validate_inputs(title, content, images, tags=None):
    """验证输入参数"""
    errors = []

    if not title or len(title.strip()) == 0:
        errors.append("标题不能为空")
    elif len(title) > 20:
        errors.append(f"标题过长: {len(title)} 字（最多 20 字）")

    if not content or len(content.strip()) == 0:
        errors.append("正文不能为空")
    elif len(content) > 1000:
        errors.append(f"正文过长: {len(content)} 字（最多 1000 字）")

    if not images or len(images) == 0:
        errors.append("至少需要一张图片")
    elif len(images) > 18:
        errors.append(f"图片过多: {len(images)} 张（最多 18 张）")

    if tags and len(tags) > 10:
        errors.append(f"标签过多: {len(tags)} 个（最多 10 个）")

    for img_path in images:
        if not os.path.exists(img_path):
            errors.append(f"图片不存在: {img_path}")

    return errors


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='发布小红书图文笔记')
    parser.add_argument('--title', required=True, help='笔记标题（最多 20 字）')
    parser.add_argument('--content', required=True, help='笔记正文（最多 1000 字）')
    parser.add_argument('--images', required=True, nargs='+', help='图片路径列表')
    parser.add_argument('--tags', nargs='+', help='话题标签列表')
    parser.add_argument('--visibility', choices=['public', 'friends', 'private'],
                        default='public', help='可见范围')

    args = parser.parse_args()

    print("=" * 60)
    print("📝 发布小红书图文笔记")
    print("=" * 60)
    print()

    # 验证输入
    print("1. 验证输入参数...")
    errors = validate_inputs(args.title, args.content, args.images, args.tags)
    if errors:
        print("❌ 参数验证失败:")
        for error in errors:
            print(f"  - {error}")
        print(json.dumps({"success": False, "errors": errors}, ensure_ascii=False, indent=2))
        return

    print(f"✓ 标题: {args.title}")
    print(f"✓ 正文长度: {len(args.content)} 字")
    print(f"✓ 图片数量: {len(args.images)} 张")
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
    print("  请 AI 分析截图确认已登录")

    # 3. 直接打开创作平台窗口（避免窗口匹配问题）
    print("\n3. 打开创作平台窗口...")
    print("  直接导航到: " + automation.PUBLISH_URL)
    
    # 使用 open_browser 直接打开新窗口
    open_result = automation.mcp.open_browser(automation.PUBLISH_URL)
    if not open_result.get("success"):
        print(f"✗ 打开创作平台失败: {open_result.get('error')}")
        return
    
    automation.mcp.wait(5)  # 等待页面加载
    
    # 尝试验证页面
    verify_result = automation.mcp.inspect_screen()
    print(f"  页面截图: {verify_result.get('screenshot_path')}")
    print("  请 AI 确认：当前页面是否为创作平台发布页？URL 是否包含 'creator.xiaohongshu.com/publish'？")

    # 4. 截图识别页面
    print("\n4. 截图识别页面...")
    result = automation.mcp.inspect_screen()

    if not result.get("success"):
        print(f"✗ 截图失败: {result.get('error')}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"✓ 页面截图: {result.get('screenshot_path')}")

    # 5. 返回信息，由 AI 指导后续操作
    print("\n5. 请 AI 分析截图并指导后续操作:")
    print("  - 识别'上传图文'按钮并点击")
    print("  - 上传图片文件")
    print("  - 填写标题和正文")
    print("  - 添加话题标签")
    print("  - 设置可见范围")
    print("  - 点击发布按钮")

    output = {
        "success": True,
        "message": "已到达发布页，请 AI 分析截图并指导后续操作",
        "screenshot_path": result.get("screenshot_path"),
        "params": {
            "title": args.title,
            "content": args.content,
            "images": args.images,
            "tags": args.tags,
            "visibility": args.visibility
        },
        "next_steps": [
            "识别'上传图文'按钮并点击",
            "上传图片文件（最多18张）",
            "填写标题（最多20字）",
            "填写正文（最多1000字）",
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
