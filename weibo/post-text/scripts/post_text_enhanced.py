#!/usr/bin/env python3
"""
weibo-post-text-enhanced: 发布纯文本微博（增强版）

完整工作流程：
1. 解析命令行参数
2. 读取并验证内容文件
3. 初始化组件
4. 打开/聚焦微博窗口
5. 捕获并保存截图
6. 使用子代理分析截图（带重试）
7. 计算坐标并发送微博
8. 清理旧截图

使用方法:
    python post_text_enhanced.py --content-file content.txt [--max-retries 3] [--screenshot-dir screenshots/weibo/] [--no-cleanup]
"""
import sys
import os
import json
import argparse

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from computer_mcp_client import WeiboAutomation
from subagent_coordinator import SubagentCoordinator, SubagentError
from screenshot_manager import ScreenshotManager, ScreenshotError


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数

    Returns:
        解析后的参数命名空间
    """
    parser = argparse.ArgumentParser(
        description="发布纯文本微博（增强版）- 自动识别界面元素",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python post_text_enhanced.py --content-file content.txt
    python post_text_enhanced.py --content-file content.txt --max-retries 5
    python post_text_enhanced.py --content-file content.txt --screenshot-dir ./my_screenshots/
    python post_text_enhanced.py --content-file content.txt --no-cleanup
        """
    )

    parser.add_argument(
        "--content-file",
        required=True,
        help="包含微博内容的文件路径"
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="子代理分析的最大重试次数 (默认: 3)"
    )

    parser.add_argument(
        "--screenshot-dir",
        default="screenshots/weibo/",
        help="截图保存目录 (默认: screenshots/weibo/)"
    )

    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="禁用旧截图清理"
    )

    return parser.parse_args()


def read_content_file(file_path: str) -> str:
    """
    读取内容文件

    Args:
        file_path: 文件路径

    Returns:
        文件内容

    Raises:
        FileNotFoundError: 文件不存在
        IOError: 读取失败
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"内容文件不存在: {file_path}")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"路径不是文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except IOError as e:
        raise IOError(f"读取文件失败: {e}")


def validate_content(content: str) -> tuple:
    """
    验证微博内容

    Args:
        content: 微博内容

    Returns:
        (is_valid: bool, error_message: str or None)
    """
    if not content:
        return False, "内容不能为空"

    if len(content) > 140:
        return False, f"内容超长: {len(content)} 字符 (最多 140 字符)"

    return True, None


def initialize_components(screenshot_dir: str, no_cleanup: bool) -> tuple:
    """
    初始化组件

    Args:
        screenshot_dir: 截图目录
        no_cleanup: 是否禁用清理

    Returns:
        (weibo_automation, subagent_coordinator, screenshot_manager)
    """
    # 初始化 WeiboAutomation
    weibo = WeiboAutomation()

    # 初始化 SubagentCoordinator
    coordinator = SubagentCoordinator()

    # 初始化 ScreenshotManager
    max_age_days = 0 if no_cleanup else 7
    screenshot_mgr = ScreenshotManager(
        base_dir=screenshot_dir,
        max_age_days=max_age_days
    )

    return weibo, coordinator, screenshot_mgr


def main():
    """主函数"""
    print("=" * 60)
    print("发布纯文本微博（增强版）")
    print("=" * 60)

    # 1. 解析参数
    print("\n[1/8] 解析命令行参数...")
    try:
        args = parse_args()
        print(f"  内容文件: {args.content_file}")
        print(f"  最大重试次数: {args.max_retries}")
        print(f"  截图目录: {args.screenshot_dir}")
        print(f"  清理旧截图: {not args.no_cleanup}")
    except SystemExit as e:
        # argparse 会在 --help 或参数错误时调用 sys.exit
        return {"success": False, "error": "参数解析失败"}

    # 2. 读取并验证内容
    print("\n[2/8] 读取并验证内容文件...")
    try:
        content = read_content_file(args.content_file)
        is_valid, error = validate_content(content)
        if not is_valid:
            result = {
                "success": False,
                "error": error,
                "content_file": args.content_file
            }
            print(f"  ✗ {error}")
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        print(f"  ✓ 内容验证通过 ({len(content)} 字符)")
    except FileNotFoundError as e:
        result = {
            "success": False,
            "error": str(e),
            "content_file": args.content_file
        }
        print(f"  ✗ {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except IOError as e:
        result = {
            "success": False,
            "error": str(e),
            "content_file": args.content_file
        }
        print(f"  ✗ {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    # 3. 初始化组件
    print("\n[3/8] 初始化组件...")
    try:
        weibo, coordinator, screenshot_mgr = initialize_components(
            args.screenshot_dir,
            args.no_cleanup
        )
        print("  ✓ WeiboAutomation 初始化完成")
        print("  ✓ SubagentCoordinator 初始化完成")
        print(f"  ✓ ScreenshotManager 初始化完成 (目录: {args.screenshot_dir})")
    except Exception as e:
        result = {
            "success": False,
            "error": f"组件初始化失败: {e}",
            "content_file": args.content_file
        }
        print(f"  ✗ 初始化失败: {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    # 4. 打开/聚焦微博窗口
    print("\n[4/8] 打开/聚焦微博窗口...")
    try:
        if not weibo.find_or_open_weibo():
            result = {
                "success": False,
                "error": "无法打开或找到微博窗口",
                "content_file": args.content_file,
                "content_length": len(content)
            }
            print("  ✗ 无法打开或找到微博窗口")
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        print("  ✓ 微博窗口已就绪")
    except Exception as e:
        result = {
            "success": False,
            "error": f"打开微博窗口失败: {e}",
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 打开微博窗口失败: {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    # 5. 捕获并保存截图
    print("\n[5/8] 捕获并保存截图...")
    try:
        screenshot_path = screenshot_mgr.capture_and_save(
            weibo.mcp,
            context="home"
        )
        print(f"  ✓ 截图已保存: {screenshot_path}")
    except ScreenshotError as e:
        result = {
            "success": False,
            "error": f"截图失败: {e}",
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 截图失败: {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        result = {
            "success": False,
            "error": f"截图异常: {e}",
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 截图异常: {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    # 6. 子代理分析（带重试）
    print(f"\n[6/8] 子代理分析截图 (最多 {args.max_retries} 次重试)...")
    try:
        elements = coordinator.analyze_screenshot(
            screenshot_path,
            max_retries=args.max_retries
        )
        print("  ✓ 界面元素识别完成")
        print(f"    - 输入框: {elements.get('input_box')}")
        print(f"    - 发送按钮: {elements.get('send_button')}")
        if elements.get('headline_article_button'):
            print(f"    - 头条文章按钮: {elements.get('headline_article_button')}")
    except SubagentError as e:
        result = {
            "success": False,
            "error": f"界面分析失败: {e}",
            "screenshot_path": screenshot_path,
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 界面分析失败: {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        result = {
            "success": False,
            "error": f"分析异常: {e}",
            "screenshot_path": screenshot_path,
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 分析异常: {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    # 7. 计算坐标并发送微博
    print("\n[7/8] 计算坐标并发送微博...")
    try:
        # 获取窗口区域
        window_rect = weibo.get_browser_window_rect()
        if not window_rect:
            result = {
                "success": False,
                "error": "无法获取浏览器窗口区域",
                "screenshot_path": screenshot_path,
                "elements_detected": elements,
                "content_file": args.content_file,
                "content_length": len(content)
            }
            print("  ✗ 无法获取浏览器窗口区域")
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result

        print(f"  窗口区域: left={window_rect['left']}, top={window_rect['top']}, "
              f"width={window_rect['width']}, height={window_rect['height']}")

        # 读取截图真实尺寸
        from PIL import Image
        try:
            with Image.open(screenshot_path) as img:
                screenshot_width, screenshot_height = img.size
            print(f"  截图真实尺寸: width={screenshot_width}, height={screenshot_height}")
        except Exception as e:
            print(f"  警告: 无法读取截图尺寸，使用窗口尺寸: {e}")
            screenshot_width = window_rect['width']
            screenshot_height = window_rect['height']

        # 转换边界框为屏幕坐标
        input_box_bbox = elements['input_box']
        send_button_bbox = elements['send_button']

        input_center = weibo.bbox_to_center(input_box_bbox)
        send_center = weibo.bbox_to_center(send_button_bbox)

        input_x, input_y = weibo.bbox_to_screen_coords(
            input_box_bbox, window_rect, screenshot_width, screenshot_height
        )
        send_x, send_y = weibo.bbox_to_screen_coords(
            send_button_bbox, window_rect, screenshot_width, screenshot_height
        )

        print(f"  输入框: bbox={input_box_bbox} -> center=({input_center[0]:.3f}, {input_center[1]:.3f}) "
              f"-> screen=({input_x}, {input_y})")
        print(f"  发送按钮: bbox={send_button_bbox} -> center=({send_center[0]:.3f}, {send_center[1]:.3f}) "
              f"-> screen=({send_x}, {send_y})")

        # 聚焦窗口
        weibo.mcp.focus_window("微博")

        # 回到页面顶部
        weibo.mcp.hotkey(["ctrl", "home"])
        weibo.mcp.wait(2)

        # 点击输入框
        print("  点击输入框...")
        weibo.mcp.click(input_x, input_y)
        weibo.mcp.wait(1)

        # 全选并替换内容
        print("  输入内容...")
        weibo.mcp.hotkey(["ctrl", "a"])
        weibo.mcp.wait(0.5)
        weibo.mcp.type_text(content)
        weibo.mcp.wait(1)

        # 点击发送按钮
        print("  点击发送按钮...")
        weibo.mcp.click(send_x, send_y)

        # 等待发布
        weibo.mcp.wait(3)

        print("  ✓ 微博发送完成")

    except Exception as e:
        result = {
            "success": False,
            "error": f"发送微博失败: {e}",
            "screenshot_path": screenshot_path,
            "elements_detected": elements,
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 发送微博失败: {e}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result

    # 8. 清理旧截图
    print("\n[8/8] 清理旧截图...")
    try:
        if args.no_cleanup:
            print("  ℹ 清理已禁用 (--no-cleanup)")
            deleted_count = 0
        else:
            deleted_count = screenshot_mgr.cleanup_old_screenshots()
            if deleted_count > 0:
                print(f"  ✓ 已清理 {deleted_count} 个旧截图")
            else:
                print("  ℹ 没有需要清理的旧截图")
    except Exception as e:
        print(f"  ⚠ 清理旧截图时出错: {e}")
        deleted_count = 0

    # 构建成功结果
    result = {
        "success": True,
        "message": "微博发送完成",
        "screenshot_path": screenshot_path,
        "elements_detected": {
            "input_box": input_box_bbox,
            "send_button": send_button_bbox,
            "headline_article_button": elements.get("headline_article_button")
        },
        "content_file": args.content_file,
        "content_length": len(content),
        "cleanup_deleted": deleted_count
    }

    print("\n" + "=" * 60)
    print("执行完成")
    print("=" * 60)
    print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    return result


if __name__ == "__main__":
    result = main()
    if not result.get("success"):
        sys.exit(1)
